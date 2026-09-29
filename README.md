# 🤖 ЛЕГИОН — Голосовой ИИ-ассистент

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()

**ЛЕГИОН** — модульный голосовой ассистент на русском языке. Работает полностью **локально**, без облаков и API-ключей. Слушает микрофон, распознаёт речь (Vosk), думает (локальная LLM через LM Studio), отвечает голосом (Silero TTS) и выполняет 50+ системных команд.

---

## ✨ Возможности

### 🎤 Слух
- Распознавание речи через **Vosk** (русская модель)
- **VAD** (Voice Activity Detection) — не реагирует на тишину
- **Шумоподавление** и **нормализация** аудио
- **Confidence-фильтр** — отбрасывает неразборчивые фразы
- **Грамматика-подсказки** для точного распознавания команд

### 🧠 Мозг
- Локальная LLM через **LM Studio** (OpenAI-совместимый API)
- Потоковые ответы (стриминг) — начинает говорить до конца генерации
- Сохранение памяти между сессиями (`assets/memory.json`)
- Автосброс при ошибках чередования ролей

### 🔊 Голос
- Синтез речи через **Silero TTS** (5 голосов: kseniya, aidar, baya, xenia, eugene)
- **Разбивка на предложения** — паузы между ними
- **Вариация скорости** ±4% — речь живее
- **LRU-кэш** повторяющихся фраз
- **Прерывание** речи голосом («стоп», «хватит», «замолчи»)

### 🎯 Команды (50+)
- **Система**: время, дата, батарея, CPU, память, диск
- **Медиа**: громкость, пауза, треки, яркость
- **Браузер**: ютуб, телеграм, гитхаб, поиск
- **Окна**: закрыть, свернуть, alt+tab, максимизировать
- **Клавиши**: enter, escape, копировать, вставить, undo
- **Мышь**: двинуть, кликнуть, прокрутить
- **Питание**: сон, перезагрузка, выключение

---

## 🚀 Быстрый старт

### 1. Требования

- **Python 3.10+**
- **LM Studio** — [скачать](https://lmstudio.ai/)
- **Микрофон**
- **Windows 10/11**, Linux или macOS

### 2. Установка

```bash
git clone https://github.com/null-0660/ai_assistant.git
cd ai_assistant
pip install -r requirements.txt
```

### 3. Модели (заглушки + инструкция)

В проекте **нет** самих моделей — только папки-заглушки с инструкциями. Скачай их отдельно:

| Модель | Куда положить | Откуда взять |
|---|---|---|
| **Vosk RU** | `model/` | [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models) → `vosk-model-ru-0.42` |
| **Silero TTS** | `v5_ru.pt` (в корень) | [models.silero.ai](https://models.silero.ai/models/tts/ru/v5_ru.pt) |
| **LLM** | LM Studio | Через UI LM Studio (`gemma-3n-e4b-it-text` или другая) |

Подробнее → [`docs/MODELS.md`](docs/MODELS.md)

### 4. Настройка LM Studio

1. Открой LM Studio → **Developer → Local Server**
2. Запусти сервер (порт `1234`)
3. Загрузи **одну** текстовую модель (например, `gemma-3n-e4b-it-text`)
4. Проверь: [http://127.0.0.1:1234/v1/models](http://127.0.0.1:1234/v1/models)

### 5. Конфиг

Открой `config.yaml` и проверь:
```yaml
ai:
  lm_studio_url: "http://127.0.0.1:1234/v1"
  model_name: "gemma-3n-e4b-it-text"     # ← точно как в LM Studio
```

### 6. Запуск

```bash
python main.py
```

---

## 📁 Структура проекта

```
ai_assistant/
├── main.py                       # точка входа
├── config.yaml                   # конфиг (YAML)
├── requirements.txt
├── README.md                     # этот файл
├── LICENSE
├── .gitignore
│
├── core/                         # ядро
│   ├── config_loader.py          # загрузка YAML
│   ├── logger.py                 # логирование
│   ├── dialogue.py               # память диалога
│   ├── assistant.py              # главный цикл
│   └── avatar_server.py          # HTTP для аватара
│
├── audio/                        # аудио
│   ├── audio_utils.py            # VAD, шумодав, нормализация
│   ├── stt.py                    # распознавание (Vosk)
│   └── tts.py                    # синтез (Silero)
│
├── commands/                     # команды
│   ├── processor.py              # обработчик
│   ├── registry.py               # реестр
│   └── plugins/                  # плагины
│       ├── system.py             # система
│       ├── media.py              # звук/медиа
│       ├── web.py                # браузер
│       └── windows.py            # окна/клавиши/мышь
│
├── assets/                       # ресурсы
│   ├── legion_avatar.html        # HTML аватар
│   └── avatar_state.json         # состояние аватара
│
├── docs/                         # документация
│   ├── ARCHITECTURE.md           # архитектура
│   ├── MODELS.md                 # как скачать модели
│   ├── COMMANDS.md               # список команд
│   ├── CONFIG.md                 # описание config.yaml
│   └── PLUGINS.md                # как писать плагины
│
└── model/                        # ЗАГЛУШКА для Vosk
    └── README.md                 # инструкция
```

Подробнее о каждом файле → [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## 🎯 Примеры команд

Скажи голосом:

```
привет
который час
какая сегодня дата
заряд батареи
открой ютуб
найди в интернете погода в москве
громче
тише
яркость на максимум
пауза
следующий трек
сверни всё
закрой окно
нажми enter
скопируй
выход
```

Полный список → [`docs/COMMANDS.md`](docs/COMMANDS.md)

---

## 🔧 Настройка слуха под микрофон

Если Vosk **не слышит** — уменьши порог:

```yaml
stt:
  vad_energy_threshold: 150   # было 300
```

Если слышит **слишком много шума** — увеличь:

```yaml
stt:
  vad_energy_threshold: 600
```

Подробнее → [`docs/CONFIG.md`](docs/CONFIG.md)

---

## 🧩 Написание плагинов

Создай файл `commands/plugins/my_plugin.py`:

```python
class MyCommand:
    name = "my_command"

    def matches(self, text: str) -> bool:
        return "моя команда" in text

    def execute(self, text, ctx) -> bool:
        ctx.say("Выполняю!")
        return True


def register(registry):
    registry.register(MyCommand())
```

Плагин **автоматически загрузится** при старте. Подробнее → [`docs/PLUGINS.md`](docs/PLUGINS.md)

---

## 🐛 Известные проблемы

| Проблема | Решение |
|---|---|
| `Model has not started loading` | Загружена вторая модель в LM Studio — Eject |
| `Unexpected endpoint` в LM Studio | Проверь, что в `config.yaml` URL заканчивается на `/v1` |
| CORS при открытии аватара | Использовать HTTP-сервер, а не `file://` (уже так и есть) |
| Vosk не распознаёт | Уменьши `vad_energy_threshold` в config |
| Ассистент не слышит | Проверь микрофон: `python -m sounddevice` |

---

## 📚 Документация

| Документ | О чём |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Архитектура, каждый файл и папка |
| [MODELS.md](docs/MODELS.md) | Где скачать модели |
| [COMMANDS.md](docs/COMMANDS.md) | Все голосовые команды |
| [CONFIG.md](docs/CONFIG.md) | Описание `config.yaml` |
| [PLUGINS.md](docs/PLUGINS.md) | Как писать плагины |

---

## 📜 Лицензия

MIT — используй, форкай, улучшай.

---

## 🙏 Благодарности

- [Vosk](https://alphacephei.com/vosk/) — распознавание речи
- [Silero](https://github.com/snakers4/silero-models) — синтез речи
- [LM Studio](https://lmstudio.ai/) — локальный LLM-сервер
- [OpenAI Python SDK](https://github.com/openai/openai-python) — клиент