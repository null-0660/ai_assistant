"""
Улучшенный слух: Vosk + VAD + шумодав + нормализация + confidence.
"""
import json
import queue
import threading
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel

from core.logger import log
from audio.audio_utils import (
    pcm_bytes_to_float32,
    is_speech,
    highpass_filter,
    normalize_audio,
    float32_to_pcm_bytes,
)


class STTEngine:
    """
    Обёртка над Vosk с VAD, шумодавом и обработкой confidence.
    Работает в отдельном потоке и вызывает callback(text, confidence).
    """

    def __init__(
        self,
        model_path: str,
        sample_rate: int = 16000,
        blocksize: int = 4000,
        vad_enabled: bool = True,
        vad_energy_threshold: int = 300,
        vad_silence_frames: int = 15,
        noise_reduction: bool = True,
        highpass_hz: int = 80,
        normalize_audio: bool = True,
        target_rms: float = 0.08,
        min_confidence: float = 0.65,
        command_hints: Optional[list] = None,
        on_text: Optional[Callable[[str, float], None]] = None,
    ):
        SetLogLevel(-1)  # меньше спама от Vosk

        self.sample_rate = sample_rate
        self.blocksize = blocksize
        self.vad_enabled = vad_enabled
        self.vad_energy_threshold_norm = vad_energy_threshold / 32768.0
        self.vad_silence_frames = vad_silence_frames
        self.noise_reduction = noise_reduction
        self.highpass_hz = highpass_hz
        self.normalize_audio = normalize_audio
        self.target_rms = target_rms
        self.min_confidence = min_confidence
        self.on_text = on_text

        # Модель Vosk
        log.info("Загрузка Vosk...")
        self.model = Model(model_path)

        # Грамматика для подсказок (если заданы)
        if command_hints:
            grammar = json.dumps(command_hints + ["[unk]"], ensure_ascii=False)
            self.recognizer = KaldiRecognizer(self.model, sample_rate, grammar)
            log.info(f"Vosk с грамматикой ({len(command_hints)} подсказок).")
        else:
            self.recognizer = KaldiRecognizer(self.model, sample_rate)
            log.info("Vosk загружен (свободная грамматика).")

        self.recognizer.SetWords(True)  # нужны слова для confidence

        # Состояние VAD
        self._silence_counter = 0
        self._speech_started = False
        self._audio_buffer: list[np.ndarray] = []

        # Потоковая обработка
        self._audio_queue: queue.Queue = queue.Queue()
        self._stop = threading.Event()
        self._stream: Optional[sd.RawInputStream] = None
        self._worker: Optional[threading.Thread] = None
        self._paused = threading.Event()

    # ── Управление ─────────────────────────────────
    def start(self) -> None:
        self._stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.blocksize,
            dtype="int16",
            channels=1,
            callback=self._audio_callback,
        )
        self._stream.start()

        self._worker = threading.Thread(
            target=self._process_loop, name="STTWorker", daemon=True
        )
        self._worker.start()
        log.info("STT запущен (слушаю).")

    def stop(self) -> None:
        self._stop.set()
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if self._worker is not None:
            self._worker.join(timeout=2)
        log.info("STT остановлен.")

    def pause(self) -> None:
        """Приостановить распознавание (например, пока ассистент говорит)."""
        self._paused.set()

    def resume(self) -> None:
        self._paused.clear()
        self.recognizer.Reset()
        self._silence_counter = 0
        self._speech_started = False
        self._audio_buffer.clear()

    def reset(self) -> None:
        self.recognizer.Reset()
        self._silence_counter = 0
        self._speech_started = False
        self._audio_buffer.clear()

    # ── Внутреннее ─────────────────────────────────
    def _audio_callback(self, indata, frames, time_info, status) -> None:
        if self._stop.is_set() or self._paused.is_set():
            return
        self._audio_queue.put(bytes(indata))

    def _preprocess(self, pcm_bytes: bytes) -> np.ndarray:
        audio = pcm_bytes_to_float32(pcm_bytes)
        if self.noise_reduction:
            audio = highpass_filter(audio, self.sample_rate, self.highpass_hz)
        if self.normalize_audio:
            audio = normalize_audio(audio, self.target_rms)
        return audio

    def _process_loop(self) -> None:
        while not self._stop.is_set():
            try:
                pcm_bytes = self._audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if self._paused.is_set():
                continue

            audio = self._preprocess(pcm_bytes)
            has_speech = (
                is_speech(audio, self.vad_energy_threshold_norm)
                if self.vad_enabled
                else True
            )

            # VAD-логика
            if self.vad_enabled:
                if has_speech:
                    self._silence_counter = 0
                    self._speech_started = True
                else:
                    if self._speech_started:
                        self._silence_counter += 1
                    if (
                        self._speech_started
                        and self._silence_counter >= self.vad_silence_frames
                    ):
                        # Конец фразы — форсируем Result
                        self._flush_recognizer()
                        self._speech_started = False
                        self._silence_counter = 0
                        continue
                    # Тишина до начала речи — не кормим Vosk
                    if not self._speech_started:
                        continue

            # Кормим Vosk
            processed_bytes = float32_to_pcm_bytes(audio)
            if self.recognizer.AcceptWaveform(processed_bytes):
                self._handle_result(self.recognizer.Result())

    def _flush_recognizer(self) -> None:
        """Принудительно завершить текущую фразу."""
        try:
            final = self.recognizer.FinalResult()
            self._handle_result(final)
        except Exception as e:
            log.debug(f"Flush error: {e}")
        self.recognizer.Reset()

    def _handle_result(self, result_json: str) -> None:
        try:
            data = json.loads(result_json)
        except Exception:
            return

        text = (data.get("text") or "").strip()
        if not text:
            return

        # Confidence = среднее по словам
        confidence = 1.0
        words = data.get("result") or []
        if words:
            confs = [w.get("conf", 1.0) for w in words]
            confidence = float(np.mean(confs))

        if confidence < self.min_confidence:
            log.debug(f"Отброшено (conf={confidence:.2f}): '{text}'")
            return

        log.info(f"🎤 Распознано [{confidence:.2f}]: {text}")
        if self.on_text:
            try:
                self.on_text(text, confidence)
            except Exception as e:
                log.error(f"Ошибка callback STT: {e}")