"""
Главный ассистент ЛЕГИОН v4.1 (без vision).
"""
import os
import json
import time
import random
import threading
from typing import Optional

import torch
import webbrowser
from openai import OpenAI

from core.config_loader import LegionConfig
from core.logger import log
from core.dialogue import DialogueManager
from core.avatar_server import AvatarServer
from audio.tts import TTSEngine
from audio.stt import STTEngine
from commands.processor import CommandProcessor


class LegionAssistant:

    def __init__(self, cfg: LegionConfig):
        self.cfg = cfg
        self._stop_event = threading.Event()
        self._last_speech_time = time.time()
        self._idle_thread: Optional[threading.Thread] = None

        torch.set_num_threads(cfg.assistant.torch_threads)
        device = torch.device("cpu")

        # TTS
        self.tts = TTSEngine(
            model_file=cfg.tts.model_file,
            device=device,
            sample_rate=cfg.tts.sample_rate,
            sentence_pause_ms=cfg.tts.sentence_pause_ms,
            speed_variation=cfg.tts.speed_variation,
            cache_size=cfg.tts.cache_size,
        )

        # Диалог
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        memory_file = os.path.join(root_dir, cfg.ai.memory_file)
        self.dialogue = DialogueManager(
            system_prompt=cfg.system_prompt,
            max_history=cfg.ai.max_history,
            memory_file=memory_file,
            persist=cfg.ai.persist_memory,
        )

        # ИИ (только текст)
        log.info(f"LM Studio URL: {cfg.ai.lm_studio_url}")
        self.ai = OpenAI(
            base_url=cfg.ai.lm_studio_url,
            api_key=cfg.ai.lm_studio_key,
        )

        # Команды (без screen)
        self.commands = CommandProcessor(
            tts=self.tts,
            voices=cfg.tts.voices,
            default_voice=cfg.tts.default_voice,
        )

        # STT
        self.stt = STTEngine(
            model_path=cfg.stt.vosk_model_path,
            sample_rate=cfg.stt.sample_rate,
            blocksize=cfg.stt.blocksize,
            vad_enabled=cfg.stt.vad_enabled,
            vad_energy_threshold=cfg.stt.vad_energy_threshold,
            vad_silence_frames=cfg.stt.vad_silence_frames,
            noise_reduction=cfg.stt.noise_reduction,
            highpass_hz=cfg.stt.highpass_hz,
            normalize_audio=cfg.stt.normalize_audio,
            target_rms=cfg.stt.target_rms,
            min_confidence=cfg.stt.min_confidence,
            command_hints=cfg.stt.command_hints or None,
            on_text=self._on_stt_text,
        )

        # Аватар
        self._assets_dir = os.path.join(root_dir, "assets")
        os.makedirs(self._assets_dir, exist_ok=True)
        self._avatar_state_file = os.path.join(self._assets_dir, "avatar_state.json")
        self._avatar_server = AvatarServer(
            self._assets_dir,
            host=cfg.avatar.host,
            port=cfg.avatar.port,
        )

    # ─────────────────────────────────────────────
    # STT callback
    # ─────────────────────────────────────────────
    def _on_stt_text(self, phrase: str, confidence: float) -> None:
        if self._stop_event.is_set():
            return

        phrase_lower = phrase.lower().strip()
        self._last_speech_time = time.time()

        if self.tts.is_speaking:
            if self._is_interrupt(phrase_lower):
                log.info(f"Прерывание: '{phrase}'")
                self.tts.interrupt()
            return

        if self._is_noise(phrase_lower):
            return

        if self._is_interrupt(phrase_lower):
            self.tts.speak("Молчу.", speaker=self.commands.current_voice)
            return

        if phrase_lower in self.cfg.assistant.exit_phrases:
            self.tts.speak(
                "Легион уходит. До встречи.",
                speaker=self.commands.current_voice,
            )
            self._stop_event.set()
            return

        self.stt.pause()
        try:
            self._write_avatar_state("listening", phrase[:40])
            if not self.commands.process(phrase_lower):
                self._ask_ai(phrase)
            self._write_avatar_state("idle", "Слушаю")
        finally:
            self.stt.resume()

    def _is_noise(self, phrase: str) -> bool:
        stripped = phrase.strip()
        allowed = {"да", "нет", "а", "всё", "все", "стоп", "ок", "окей"}
        return len(stripped) <= 2 and stripped not in allowed

    def _is_interrupt(self, phrase: str) -> bool:
        return any(ip in phrase for ip in self.cfg.assistant.interrupt_phrases)

    # ─────────────────────────────────────────────
    # ИИ
    # ─────────────────────────────────────────────
    def _ask_ai(self, user_input: str) -> None:
        self.dialogue.add("user", user_input)
        self._write_avatar_state("thinking", "Думаю...")

        last_err = None
        for attempt in range(2):
            try:
                response = self.ai.chat.completions.create(
                    model=self.cfg.ai.model_name,
                    messages=self.dialogue.get(),
                    temperature=self.cfg.ai.temperature,
                    stream=True,
                    timeout=60,
                )

                buffer = ""
                full_response = ""

                for chunk in response:
                    if self._stop_event.is_set():
                        break
                    token = chunk.choices[0].delta.content
                    if not token:
                        continue
                    buffer += token
                    full_response += token

                    if any(p in token for p in ['.', '!', '?', '\n']):
                        clean = buffer.strip()
                        if clean:
                            self._write_avatar_state("speaking", clean[:60])
                            self.tts.speak(clean, speaker=self.commands.current_voice)
                            if self.tts.interrupt_requested:
                                break
                        buffer = ""

                if buffer.strip() and not self.tts.interrupt_requested:
                    self.tts.speak(
                        buffer.strip(), speaker=self.commands.current_voice
                    )

                if full_response.strip():
                    self.dialogue.add("assistant", full_response)

                self._write_avatar_state("idle", "Слушаю")
                return  # успех

            except Exception as e:
                last_err = e
                log.warning(f"Попытка {attempt + 1} не удалась: {e}")
                time.sleep(0.8)

        err = str(last_err)
        log.error(f"Ошибка ИИ (после ретраев): {err}")
        self.dialogue.pop_last_user()
        if "roles must alternate" in err or "jinja" in err.lower():
            self.dialogue.reset()
            self.tts.speak(
                "Сбросил память диалога.", speaker=self.commands.current_voice
            )
        else:
            self.tts.speak(
                "Не могу достучаться до модели.", speaker=self.commands.current_voice
            )
        self._write_avatar_state("idle", "Ошибка")

    # ─────────────────────────────────────────────
    # Idle
    # ─────────────────────────────────────────────
    def _idle_loop(self) -> None:
        while not self._stop_event.is_set():
            time.sleep(5)
            if (
                not self.tts.is_speaking
                and time.time() - self._last_speech_time
                > self.cfg.assistant.idle_timeout_sec
                and self.cfg.idle_phrases
            ):
                phrase = random.choice(self.cfg.idle_phrases)
                self.tts.speak(phrase, speaker=self.commands.current_voice)
                self._last_speech_time = time.time()

    # ─────────────────────────────────────────────
    # Аватар
    # ─────────────────────────────────────────────
    def _write_avatar_state(self, state: str, text: str = "") -> None:
        try:
            data = json.dumps({"state": state, "text": text}, ensure_ascii=False)
            tmp = self._avatar_state_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(data)
            os.replace(tmp, self._avatar_state_file)
        except Exception:
            pass

    def _launch_avatar(self) -> None:
        if not self.cfg.avatar.enabled:
            return
        self._avatar_server.start()
        try:
            webbrowser.open(self._avatar_server.url)
            log.info(f"Аватар: {self._avatar_server.url}")
        except Exception as e:
            log.warning(f"Не удалось открыть аватар: {e}")

    # ─────────────────────────────────────────────
    # Запуск
    # ─────────────────────────────────────────────
    def run(self) -> None:
        log.info("🤖 ЛЕГИОН v4.1 (без vision) запущен!")
        self._launch_avatar()
        self._write_avatar_state("idle", "Запуск систем...")

        self._write_avatar_state("speaking", "Легион онлайн")
        self.tts.speak(
            "Легион онлайн. Системы в норме. Слушаю вас.",
            speaker=self.commands.current_voice,
        )
        self._write_avatar_state("idle", "Слушаю вас")
        self._last_speech_time = time.time()

        self._idle_thread = threading.Thread(target=self._idle_loop, daemon=True)
        self._idle_thread.start()

        self.stt.start()

        try:
            while not self._stop_event.is_set():
                time.sleep(0.5)
        except KeyboardInterrupt:
            log.info("Ctrl+C — завершение.")
        finally:
            self._stop_event.set()
            self.stt.stop()
            self._avatar_server.stop()
            log.info("ЛЕГИОН остановлен.")