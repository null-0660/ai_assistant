"""
Текстовый чат через LM Studio. Без TTS и STT.
Автоматически добавляет /no_think для Qwen3, если он в имени модели.
"""
import os
import threading
from typing import Optional, Callable

from openai import OpenAI

from core.config_loader import LegionConfig
from core.dialogue import DialogueManager
from core.logger import log


class ChatEngine:

    def __init__(self, cfg: LegionConfig):
        self.cfg = cfg
        self.ai = OpenAI(
            base_url=cfg.ai.lm_studio_url,
            api_key=cfg.ai.lm_studio_key,
        )
        self._dialogue: Optional[DialogueManager] = None
        self._lock = threading.Lock()

    def _get_dialogue(self) -> DialogueManager:
        if self._dialogue is None:
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            memory_file = os.path.join(root, self.cfg.ai.memory_file)
            self._dialogue = DialogueManager(
                system_prompt=self.cfg.system_prompt,
                max_history=self.cfg.ai.max_history,
                memory_file=memory_file,
                persist=self.cfg.ai.persist_memory,
            )
        return self._dialogue

    def ask(
        self,
        text: str,
        on_chunk: Optional[Callable[[str], None]] = None,
        on_done: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> None:

        def worker():
            with self._lock:
                dialogue = self._get_dialogue()
                dialogue.add("user", text)
                try:
                    response = self.ai.chat.completions.create(
                        model=self.cfg.ai.model_name,
                        messages=dialogue.get(),
                        temperature=self.cfg.ai.temperature,
                        max_tokens=250,          # ↑ для чата (не голос)
                        stream=True,
                        timeout=90,
                    )
                    full = ""
                    for chunk in response:
                        token = chunk.choices[0].delta.content
                        if not token:
                            continue
                        full += token
                        if on_chunk:
                            on_chunk(token)
                    if full.strip():
                        dialogue.add("assistant", full)
                    if on_done:
                        on_done(full)
                except Exception as e:
                    log.error(f"Chat error: {e}")
                    dialogue.pop_last_user()
                    if on_error:
                        on_error(str(e))

        threading.Thread(target=worker, daemon=True).start()