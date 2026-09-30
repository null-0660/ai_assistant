"""
Улучшенный TTS: разбивка на предложения, паузы, вариация скорости, кэш.
ECHO-ЗАЩИТА: вызывает on_speak callback для каждой произнесённой фразы.
"""
import re
import time
import random
import hashlib
import threading
from collections import OrderedDict
from typing import Optional, Callable

import numpy as np
import sounddevice as sd
import torch

from core.logger import log

try:
    from scipy import signal as scipy_signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class TTSEngine:

    def __init__(
        self,
        model_file: str,
        device: torch.device,
        sample_rate: int = 48000,
        sentence_pause_ms: int = 120,
        speed_variation: float = 0.04,
        cache_size: int = 32,
        on_speak: Optional[Callable[[str], None]] = None,
    ):
        self.sample_rate = sample_rate
        self.sentence_pause_ms = sentence_pause_ms
        self.speed_variation = speed_variation
        self.cache_size = cache_size
        self.on_speak = on_speak

        self._speaking = False
        self._interrupt = threading.Event()
        self._lock = threading.Lock()
        self._cache: "OrderedDict[str, np.ndarray]" = OrderedDict()

        log.info("Загрузка голоса Silero...")
        self.model = torch.package.PackageImporter(model_file).load_pickle(
            "tts_models", "model"
        )
        self.model.to(device)
        log.info("Голос Silero загружен.")

    @property
    def is_speaking(self) -> bool:
        return self._speaking

    @property
    def interrupt_requested(self) -> bool:
        return self._interrupt.is_set()

    def interrupt(self) -> None:
        if self._speaking:
            self._interrupt.set()
            sd.stop()
            log.info("Речь прервана.")

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'[*_#`\n]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _split_sentences(self, text: str) -> list[str]:
        parts = re.split(r'(?<=[.!?])\s+', text)
        return [p.strip() for p in parts if p.strip()]

    def _cache_key(self, text: str, speaker: str) -> str:
        return hashlib.md5(f"{speaker}|{text}".encode("utf-8")).hexdigest()

    def _cache_get(self, key: str) -> Optional[np.ndarray]:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def _cache_put(self, key: str, audio: np.ndarray) -> None:
        if self.cache_size <= 0:
            return
        self._cache[key] = audio
        self._cache.move_to_end(key)
        while len(self._cache) > self.cache_size:
            self._cache.popitem(last=False)

    def _synthesize(self, text: str, speaker: str) -> Optional[np.ndarray]:
        key = self._cache_key(text, speaker)
        cached = self._cache_get(key)
        if cached is not None:
            return cached

        try:
            audio = self.model.apply_tts(
                text=text, speaker=speaker, sample_rate=self.sample_rate
            )
            audio_np = audio.numpy()
        except Exception as e:
            log.error(f"Ошибка синтеза: {e}")
            return None

        if SCIPY_AVAILABLE and self.speed_variation > 0:
            factor = 1.0 + random.uniform(-self.speed_variation, self.speed_variation)
            new_len = max(1, int(len(audio_np) / factor))
            try:
                audio_np = scipy_signal.resample(audio_np, new_len).astype(np.float32)
            except Exception:
                pass

        self._cache_put(key, audio_np)
        return audio_np

    def _play_audio(self, audio: np.ndarray) -> bool:
        if audio is None or len(audio) == 0:
            return True
        sd.play(audio, self.sample_rate)
        while sd.get_stream().active:
            if self._interrupt.is_set():
                sd.stop()
                return False
            time.sleep(0.03)
        return True

    def speak(self, text: str, speaker: str = "kseniya") -> None:
        text = self._clean_text(text)
        if not text:
            return

        with self._lock:
            self._interrupt.clear()
            self._speaking = True
            log.info(f"🔊 Легион [{speaker}]: {text}")

            # ── Echo-защита: уведомляем о фразах ДО воспроизведения ──
            if self.on_speak:
                try:
                    for sent in self._split_sentences(text) or [text]:
                        self.on_speak(sent)
                except Exception as e:
                    log.debug(f"on_speak error: {e}")

            try:
                sentences = self._split_sentences(text) or [text]
                for i, sent in enumerate(sentences):
                    if self._interrupt.is_set():
                        break
                    audio = self._synthesize(sent, speaker)
                    if audio is None:
                        continue
                    if not self._play_audio(audio):
                        break
                    if i < len(sentences) - 1 and self.sentence_pause_ms > 0:
                        pause = self.sentence_pause_ms / 1000.0
                        end = time.time() + pause
                        while time.time() < end:
                            if self._interrupt.is_set():
                                break
                            time.sleep(0.02)
            except Exception as e:
                log.error(f"Ошибка TTS: {e}")
            finally:
                time.sleep(0.1)
                self._speaking = False
                self._interrupt.clear()