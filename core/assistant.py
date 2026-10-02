"""
Главный ассистент ЛЕГИОН v4.5
Новое:
- Команда выхода работает ВСЕГДА (во время речи и в тишине)
- Fallback по последнему слову для выхода
- Echo-защита с логами
- Убрано зависание при выходе
- Поддержка внешнего avatar_server (для GUI)
"""
import os
import re
import json
import time
import random
import threading
from difflib import SequenceMatcher
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

    def __init__(self, cfg: LegionConfig, avatar_server=None):
        self.cfg = cfg
        self._stop_event = threading.Event()
        self._last_speech_time = time.time()
        self._idle_thread: Optional[threading.Thread] = None

        # Echo-защита
        self._recent_tts_texts: list[str] = []
        self._recent_tts_lock = threading.Lock()
        self._last_tts_end_time: float = 0.0

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
            on_speak=self._remember_tts_text,
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

        # ИИ
        log.info(f"LM Studio URL: {cfg.ai.lm_studio_url}")
        self.ai = OpenAI(
            base_url=cfg.ai.lm_studio_url,
            api_key=cfg.ai.lm_studio_key,
        )

        # Команды
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

        # Аватар — внешний (от GUI) или создаём свой
        self._assets_dir = os.path.join(root_dir, "assets")
        os.makedirs(self._assets_dir, exist_ok=True)
        self._avatar_state_file = os.path.join(self._assets_dir, "avatar_state.json")

        if avatar_server is not None:
            self._avatar_server = avatar_server
            self._owns_avatar_server = False
        else:
            self._avatar_server = AvatarServer(
                self._assets_dir,
                host=cfg.avatar.host,
                port=cfg.avatar.port,
            )
            self._owns_avatar_server = True

    # ═════════════════════════════════════════════
    # ECHO-ЗАЩИТА
    # ═════════════════════════════════════════════
    def _remember_tts_text(self, text: str) -> None:
        """TTS уведомляет о каждой произнесённой фразе."""
        with self._recent_tts_lock:
            self._recent_tts_texts.append(text.lower().strip())
            if len(self._recent_tts_texts) > 20:
                self._recent_tts_texts.pop(0)
        self._last_tts_end_time = time.time()

    def _is_echo(self, phrase: str, threshold: float = 0.6) -> bool:
        """Похожа ли фраза на недавнюю TTS-речь?"""
        p = phrase.lower().strip()
        if not p or len(p) < 3:
            return False

        with self._recent_tts_lock:
            candidates = list(self._recent_tts_texts)

        if not candidates:
            return False

        for t in candidates:
            if p in t or t in p:
                log.info(f"🔇 Эхо (вхождение): '{p[:40]}'")
                return True

        for t in candidates:
            ratio = SequenceMatcher(None, p, t).ratio()
            if ratio > threshold:
                log.info(f"🔇 Эхо (ratio={ratio:.2f}): '{p[:40]}'")
                return True

        p_words = set(p.split())
        for t in candidates:
            t_words = set(t.split())
            overlap = p_words & t_words
            if len(overlap) >= 2:
                log.info(f"🔇 Эхо (слов {len(overlap)}): '{p[:40]}'")
                return True

        return False

    # ═════════════════════════════════════════════
    # ПРОВЕРКИ
    # ═════════════════════════════════════════════
    def _is_noise(self, phrase: str) -> bool:
        stripped = phrase.strip()
        allowed = {"да", "нет", "а", "всё", "все", "стоп", "ок", "окей"}
        return len(stripped) <= 2 and stripped not in allowed

    def _is_interrupt(self, phrase: str) -> bool:
        if any(ip in phrase for ip in self.cfg.assistant.interrupt_phrases):
            return True
        words = phrase.split()
        if words and words[-1] in self.cfg.assistant.interrupt_phrases:
            return True
        return False

    def _is_exit(self, phrase: str) -> bool:
        if phrase in self.cfg.assistant.exit_phrases:
            return True
        for ep in self.cfg.assistant.exit_phrases:
            if ep in phrase:
                return True
        words = phrase.split()
        if words and words[-1] in self.cfg.assistant.exit_phrases:
            return True
        return False

    # ═════════════════════════════════════════════
    # ВЫХОД
    # ═════════════════════════════════════════════
    def _do_exit(self, phrase: str, during_speech: bool = False) -> None:
        """Корректный выход из программы."""
        label = "во время речи" if during_speech else "в тишине"
        log.info(f"🚪 Выход ({label}): '{phrase}'")

        if self.tts.is_speaking:
            self.tts.interrupt()
            time.sleep(0.3)

        self._write_avatar_state("idle", "Выключение")

        try:
            self.tts.speak(
                "Легион уходит. До встречи.",
                speaker=self.commands.current_voice,
            )
        except Exception:
            pass

        time.sleep(0.4)
        self._stop_event.set()

    # ═════════════════════════════════════════════
    # STT CALLBACK
    # ═════════════════════════════════════════════
    def _on_stt_text(self, phrase: str, confidence: float) -> None:
        if self._stop_event.is_set():
            return

        phrase_lower = phrase.lower().strip()
        if not phrase_lower:
            return

        # ═══════════════════════════════════════════
        # РЕЖИМ 1: TTS говорит
        # ═══════════════════════════════════════════
        if self.tts.is_speaking:
            if self._is_exit(phrase_lower):
                self._do_exit(phrase, during_speech=True)
                return

            if self._is_interrupt(phrase_lower):
                log.info(f"🛑 Прерывание: '{phrase}'")
                self.tts.interrupt()
                self._write_avatar_state("idle", "Прервано")
                return

            log.debug(f"🔇 Игнор во время речи: '{phrase}'")
            return

        # ═══════════════════════════════════════════
        # РЕЖИМ 2: TTS молчит
        # ═══════════════════════════════════════════
        if self._is_exit(phrase_lower):
            self._do_exit(phrase, during_speech=False)
            return

        time_since_tts = time.time() - self._last_tts_end_time
        if time_since_tts < 5.0:
            if self._is_interrupt(phrase_lower):
                log.info(f"🛑 Прерывание (после TTS): '{phrase}'")
                self.tts.speak("Молчу.", speaker=self.commands.current_voice)
                return
            log.info(f"🔇 Игнор ({time_since_tts:.1f}с после TTS): '{phrase[:40]}'")
            return

        if self._is_echo(phrase_lower):
            return

        if self._is_noise(phrase_lower):
            return

        if self._is_interrupt(phrase_lower):
            self.tts.speak("Молчу.", speaker=self.commands.current_voice)
            return

        self._last_speech_time = time.time()
        self._write_avatar_state("listening", phrase[:40])
        try:
            if not self.commands.process(phrase_lower):
                self._ask_ai(phrase)
        finally:
            self._write_avatar_state("idle", "Слушаю")

    # ═════════════════════════════════════════════
    # ИИ
    # ═════════════════════════════════════════════
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
                    max_tokens=120,
                    stream=True,
                    timeout=60,
                )

                buffer = ""
                full_response = ""
                was_interrupted = False

                for chunk in response:
                    if self._stop_event.is_set():
                        was_interrupted = True
                        break

                    if self.tts.interrupt_requested:
                        log.info("⏹ Генерация прервана пользователем.")
                        was_interrupted = True
                        try:
                            response.close()
                        except Exception:
                            pass
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
                                log.info("⏹ Прерывание после фразы.")
                                was_interrupted = True
                                try:
                                    response.close()
                                except Exception:
                                    pass
                                break
                        buffer = ""

                if (
                    buffer.strip()
                    and not was_interrupted
                    and not self.tts.interrupt_requested
                    and not self._stop_event.is_set()
                ):
                    self.tts.speak(
                        buffer.strip(), speaker=self.commands.current_voice
                    )

                if full_response.strip() and not was_interrupted:
                    self.dialogue.add("assistant", full_response)
                elif was_interrupted:
                    log.info("⏹ Ответ не сохранён (прерван).")
                    self.dialogue.pop_last_user()

                self._write_avatar_state("idle", "Слушаю")
                return

            except Exception as e:
                last_err = e
                log.warning(f"Попытка {attempt + 1} не удалась: {e}")
                time.sleep(0.5)

        err = str(last_err)
        log.error(f"Ошибка ИИ (после ретраев): {err}")
        self.dialogue.pop_last_user()
        if "roles must alternate" in err or "jinja" in err.lower():
            self.dialogue.reset()
            log.warning("История сброшена (jinja error).")
        else:
            self.tts.speak(
                "Не могу достучаться до модели.",
                speaker=self.commands.current_voice,
            )
        self._write_avatar_state("idle", "Ошибка")

    # ═════════════════════════════════════════════
    # IDLE
    # ═════════════════════════════════════════════
    def _idle_loop(self) -> None:
        while not self._stop_event.is_set():
            time.sleep(5)
            if self._stop_event.is_set():
                break
            if (
                not self.tts.is_speaking
                and time.time() - self._last_speech_time
                > self.cfg.assistant.idle_timeout_sec
                and self.cfg.idle_phrases
            ):
                phrase = random.choice(self.cfg.idle_phrases)
                self.tts.speak(phrase, speaker=self.commands.current_voice)
                self._last_speech_time = time.time()

    # ═════════════════════════════════════════════
    # АВАТАР
    # ═════════════════════════════════════════════
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
        # Если сервер внешний (GUI) — он уже запущен
        if self._owns_avatar_server:
            self._avatar_server.start()
            try:
                webbrowser.open(self._avatar_server.url)
                log.info(f"Аватар: {self._avatar_server.url}")
            except Exception as e:
                log.warning(f"Не удалось открыть аватар: {e}")

    # ═════════════════════════════════════════════
    # ЗАПУСК
    # ═════════════════════════════════════════════
    def run(self) -> None:
        log.info("🤖 ЛЕГИОН v4.5 (выход работает всегда) запущен!")
        self._launch_avatar()
        self._write_avatar_state("idle", "Запуск систем...")

        self._write_avatar_state("speaking", "Легион онлайн")
        self.tts.speak(
            "Легион онлайн. Системы в норме.",
            speaker=self.commands.current_voice,
        )
        self._write_avatar_state("idle", "Слушаю вас")
        self._last_speech_time = time.time()

        self._idle_thread = threading.Thread(target=self._idle_loop, daemon=True)
        self._idle_thread.start()

        self.stt.start()

        try:
            while not self._stop_event.is_set():
                time.sleep(0.3)
        except KeyboardInterrupt:
            log.info("Ctrl+C — завершение.")
        finally:
            self._shutdown()

    def _shutdown(self) -> None:
        """Корректное завершение без зависаний."""
        log.info("Завершение работы...")
        self._stop_event.set()

        try:
            if self.tts.is_speaking:
                self.tts.interrupt()
        except Exception:
            pass

        try:
            self.stt.stop()
        except Exception as e:
            log.debug(f"Ошибка остановки STT: {e}")

        # Стопаем аватар только если он наш
        if self._owns_avatar_server:
            try:
                self._avatar_server.stop()
            except Exception as e:
                log.debug(f"Ошибка остановки аватара: {e}")

        log.info("ЛЕГИОН остановлен.")