# ⚙️ Описание config.yaml

Все настройки в одном файле. Меняй и перезапускай.

---

## `ai` — мозг (LLM)

```yaml
ai:
  lm_studio_url: "http://127.0.0.1:1234/v1"
  lm_studio_key: "lm-studio"
  model_name: "gemma-3n-e4b-it-text"
  temperature: 0.7
  max_history: 12
  persist_memory: true
  memory_file: "assets/memory.json"
```

| Поле | Что значит |
|---|---|
| `lm_studio_url` | URL OpenAI-совместимого API (**обязательно** `/v1` в конце) |
| `lm_studio_key` | Ключ (для LM Studio — любой) |
| `model_name` | ID модели (как в `GET /v1/models`) |
| `temperature` | Креативность: 0.1 строго, 1.0 хаос |
| `max_history` | Сколько реплик помнить |
| `persist_memory` | Сохранять ли память на диск |
| `memory_file` | Куда сохранять |

---

## `tts` — синтез речи

```yaml
tts:
  model_file: "v5_ru.pt"
  sample_rate: 48000
  default_voice: "kseniya"
  voices: ["kseniya", "aidar", "baya", "xenia", "eugene"]
  sentence_pause_ms: 120
  speed_variation: 0.04
  cache_size: 32
```

| Поле | Что значит |
|---|---|
| `model_file` | Путь к `v5_ru.pt` |
| `sample_rate` | Частота: 48000 или 24000 |
| `default_voice` | Голос по умолчанию |
| `voices` | Список доступных |
| `sentence_pause_ms` | Пауза между предложениями (мс) |
| `speed_variation` | ±% скорости для живости |
| `cache_size` | Сколько фраз кэшировать |

---

## `stt` — распознавание речи

```yaml
stt:
  vosk_model_path: "model"
  sample_rate: 16000
  blocksize: 4000
  vad_enabled: true
  vad_energy_threshold: 300
  vad_silence_frames: 15
  noise_reduction: true
  highpass_hz: 80
  normalize_audio: true
  target_rms: 0.08
  min_confidence: 0.65
  command_hints: [...]
```

| Поле | Что значит |
|---|---|
| `vosk_model_path` | Папка с моделью Vosk |
| `sample_rate` | 16000 — стандарт для Vosk |
| `vad_enabled` | Включить VAD |
| `vad_energy_threshold` | **Главная настройка**: меньше = чувствительнее |
| `vad_silence_frames` | Сколько тихих кадров = конец фразы |
| `noise_reduction` | Включить high-pass фильтр |
| `highpass_hz` | Отсекает ниже этой частоты |
| `normalize_audio` | Нормализация громкости |
| `target_rms` | Целевая громкость |
| `min_confidence` | Минимум уверенности (0..1) |
| `command_hints` | Подсказки Vosk (грамматика) |

### Настройка VAD под микрофон

- **Не слышит** → `vad_energy_threshold: 150`
- **Слишком чувствительно** → `vad_energy_threshold: 600`
- **Отключить VAD** → `vad_enabled: false`

---

## `assistant` — общие настройки

```yaml
assistant:
  torch_threads: 4
  idle_timeout_sec: 45
  interrupt_phrases: [...]
  exit_phrases: [...]
```

| Поле | Что значит |
|---|---|
| `torch_threads` | Потоки CPU для torch |
| `idle_timeout_sec` | Через сколько тишины сказать idle-фразу |
| `interrupt_phrases` | Слова-прерывания речи |
| `exit_phrases` | Слова-выходы |

---

## `avatar` — аватар

```yaml
avatar:
  enabled: true
  host: "127.0.0.1"
  port: 8765
```

| Поле | Что значит |
|---|---|
| `enabled` | Открывать ли аватар |
| `host` / `port` | Адрес HTTP-сервера |

---

## `system_prompt` — характер ИИ

Многострочный промпт — «личность» ассистента. Меняй осторожно: чем длиннее, тем медленнее LLM.

---

## `idle_phrases` — фразы при тишине

Список фраз. Одна выбирается случайно, когда пользователь молчит `idle_timeout_sec` секунд.