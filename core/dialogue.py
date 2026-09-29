"""
Менеджер диалога с сохранением памяти на диск.
"""
import os
import json
from typing import List, Dict

from core.logger import log


class DialogueManager:
    """Хранит историю, гарантирует строгое чередование user/assistant."""

    def __init__(
        self,
        system_prompt: str,
        max_history: int = 12,
        memory_file: str | None = None,
        persist: bool = True,
    ):
        self.max_history = max_history
        self.system_prompt = system_prompt
        self.memory_file = memory_file
        self.persist = persist and bool(memory_file)

        self.history: List[Dict] = [{"role": "system", "content": system_prompt}]
        if self.persist:
            self._load()

    # ── Публичное API ───────────────────────────────
    def add(self, role: str, content: str) -> None:
        if not content or not content.strip():
            return
        self.history.append({"role": role, "content": content.strip()})
        self._clean()
        self._trim()
        self._save()

    def pop_last_user(self) -> None:
        if len(self.history) > 1 and self.history[-1]["role"] == "user":
            self.history.pop()
            self._save()

    def get(self) -> List[Dict]:
        return list(self.history)

    def reset(self) -> None:
        self.history = [{"role": "system", "content": self.system_prompt}]
        self._save()

    # ── Внутреннее ──────────────────────────────────
    def _clean(self) -> None:
        """Склеивает подряд идущие сообщения одной роли."""
        cleaned = [self.history[0]]
        for msg in self.history[1:]:
            content = msg.get("content", "")
            if isinstance(content, str) and not content.strip():
                continue
            if (
                isinstance(cleaned[-1].get("content"), str)
                and cleaned[-1]["role"] == msg["role"]
                and isinstance(content, str)
            ):
                cleaned[-1]["content"] += " " + content.strip()
            else:
                cleaned.append(msg)
        self.history = cleaned

    def _trim(self) -> None:
        if len(self.history) > self.max_history + 1:
            self.history = [self.history[0]] + self.history[-(self.max_history):]

    def _save(self) -> None:
        if not self.persist:
            return
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            # Сохраняем без system, только реплики
            data = [m for m in self.history if m["role"] != "system"]
            tmp = self.memory_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.memory_file)
        except Exception as e:
            log.warning(f"Не удалось сохранить память: {e}")

    def _load(self) -> None:
        if not os.path.exists(self.memory_file):
            return
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for msg in data[-self.max_history:]:
                    if msg.get("role") in ("user", "assistant") and msg.get("content"):
                        self.history.append(msg)
                self._clean()
                log.info(f"Загружено {len(self.history) - 1} реплик из памяти.")
        except Exception as e:
            log.warning(f"Не удалось загрузить память: {e}")