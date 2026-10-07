"""
Утилиты обработки аудио: VAD, шумодав, нормализация.
"""
import numpy as np

try:
    from scipy import signal as sp_signal
    SCIPY = True
except ImportError:
    SCIPY = False


def pcm_bytes_to_float32(data: bytes) -> np.ndarray:
    """int16 PCM → float32 в [-1, 1]."""
    arr = np.frombuffer(data, dtype=np.int16).astype(np.float32)
    return arr / 32768.0


def rms_energy(audio: np.ndarray) -> float:
    """RMS громкость сигнала [0..1]."""
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(audio ** 2)))


def is_speech(audio: np.ndarray, threshold_rms: float = 0.01) -> bool:
    """Простой VAD по энергии."""
    return rms_energy(audio) > threshold_rms


def highpass_filter(audio: np.ndarray, sample_rate: int, cutoff_hz: int = 80) -> np.ndarray:
    """Убирает низкочастотный гул (ветер, шум микрофона)."""
    if not SCIPY or audio.size < 32:
        return audio
    nyq = sample_rate / 2.0
    if cutoff_hz >= nyq:
        return audio
    b, a = sp_signal.butter(4, cutoff_hz / nyq, btype="high")
    try:
        return sp_signal.filtfilt(b, a, audio).astype(np.float32)
    except Exception:
        return audio


def normalize_audio(audio: np.ndarray, target_rms: float = 0.08) -> np.ndarray:
    """Нормализует громкость к целевому RMS."""
    rms = rms_energy(audio)
    if rms < 1e-6:
        return audio
    gain = target_rms / rms
    # Ограничиваем усиление, чтобы не вытащить шум
    gain = float(np.clip(gain, 0.5, 8.0))
    out = audio * gain
    # Мягкий клиппинг
    return np.clip(out, -1.0, 1.0).astype(np.float32)


def float32_to_pcm_bytes(audio: np.ndarray) -> bytes:
    """float32 [-1,1] → int16 PCM bytes."""
    clipped = np.clip(audio, -1.0, 1.0)
    return (clipped * 32767.0).astype(np.int16).tobytes()