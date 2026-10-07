"""
Загрузка и валидация конфига из YAML.
"""
import os
import yaml
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class AIConfig:
    lm_studio_url: str = "http://127.0.0.1:1234/v1"
    lm_studio_key: str = "lm-studio"
    model_name: str = "gemma-3n-e4b-it-text"
    temperature: float = 0.7
    max_history: int = 12
    persist_memory: bool = True
    memory_file: str = "assets/memory.json"


@dataclass
class TTSConfig:
    model_file: str = "v5_ru.pt"
    sample_rate: int = 48000
    default_voice: str = "kseniya"
    voices: List[str] = field(default_factory=lambda: ["kseniya", "aidar", "baya"])
    sentence_pause_ms: int = 120
    speed_variation: float = 0.04
    cache_size: int = 32


@dataclass
class STTConfig:
    vosk_model_path: str = "model"
    sample_rate: int = 16000
    blocksize: int = 4000
    vad_enabled: bool = True
    vad_energy_threshold: int = 300
    vad_silence_frames: int = 15
    noise_reduction: bool = True
    highpass_hz: int = 80
    normalize_audio: bool = True
    target_rms: float = 0.08
    min_confidence: float = 0.65
    command_hints: List[str] = field(default_factory=list)


@dataclass
class AssistantConfig:
    torch_threads: int = 4
    idle_timeout_sec: int = 45
    interrupt_phrases: Tuple[str, ...] = ()
    exit_phrases: Tuple[str, ...] = ()


@dataclass
class AvatarConfig:
    enabled: bool = True
    host: str = "127.0.0.1"
    port: int = 8765


@dataclass
class LegionConfig:
    ai: AIConfig = field(default_factory=AIConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    stt: STTConfig = field(default_factory=STTConfig)
    assistant: AssistantConfig = field(default_factory=AssistantConfig)
    avatar: AvatarConfig = field(default_factory=AvatarConfig)
    system_prompt: str = ""
    idle_phrases: List[str] = field(default_factory=list)


def _tuplify(value):
    if isinstance(value, list):
        return tuple(value)
    return value


def load_config(path: str = "config.yaml") -> LegionConfig:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Конфиг не найден: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    cfg = LegionConfig(
        ai=AIConfig(**raw.get("ai", {})),
        tts=TTSConfig(**raw.get("tts", {})),
        stt=STTConfig(**raw.get("stt", {})),
        assistant=AssistantConfig(
            **{
                **raw.get("assistant", {}),
                "interrupt_phrases": _tuplify(
                    raw.get("assistant", {}).get("interrupt_phrases", [])
                ),
                "exit_phrases": _tuplify(
                    raw.get("assistant", {}).get("exit_phrases", [])
                ),
            }
        ),
        avatar=AvatarConfig(**raw.get("avatar", {})),
        system_prompt=raw.get("system_prompt", ""),
        idle_phrases=raw.get("idle_phrases", []),
    )
    return cfg