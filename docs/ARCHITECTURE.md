# 🏗 Архитектура ЛЕГИОНа

Полное описание проекта: что делает каждая папка и каждый файл.

---

## 🗂 Дерево проекта

```
ai_assistant/
├── main.py                       # точка входа
├── config.yaml                   # конфиг
├── requirements.txt              # зависимости
├── README.md                     # главная документация
├── LICENSE                       # MIT
├── .gitignore
│
├── core/                         # ЯДРО
├── audio/                        # АУДИО
├── commands/                     # КОМАНДЫ
├── assets/                       # РЕСУРСЫ
├── docs/                         # ДОКУМЕНТАЦИЯ
└── model/                        # ЗАГЛУШКА для Vosk
```

---

## 📂 `core/` — ядро ассистента

### `main.py` (в корне)
**Роль:** точка входа.
**Что делает:**
- Загружает `config.yaml`
- Проверяет LM Studio (доступность + наличие модели)
- Создаёт `LegionAssistant` и запускает главный цикл

**Когда править:** если хочешь добавить pre-flight проверки или изменить точку старта.

---

### `core/config_loader.py`
**Роль:** читает YAML и превращает в dataclass.
**Что делает:**
- Определяет структуры `AIConfig`, `TTSConfig`, `STTConfig`, `AssistantConfig`, `AvatarConfig`, `LegionConfig`
- Валидирует поля
- Преобразует списки в tuple там, где нужно

**Когда править:** при добавлении нового поля в `config.yaml`.

---

### `core/logger.py`
**Роль:** единая точка логирования.
**Что делает:**
- Настраивает `logging` один раз
- Экспортирует `log` — общий логгер

**Когда править:** если нужен другой формат логов или запись в файл.

---

### `core/dialogue.py`
**Роль:** управление историей диалога.
**Что делает:**
- Хранит `history: list[{role, content}]`
- Гарантирует чередование `user` / `assistant` (защита от jinja-ошибок)
- Склеивает подряд идущие реплики одной роли
- Обрезает историю до `max_history`
- **Сохраняет и загружает** память из `assets/memory.json`

**Когда править:** если нужно добавить summarization или другой формат памяти.

---

### `core/assistant.py`
**Роль:** главный класс — «мозг» ассистента.
**Что делает:**
- Инициализирует TTS, STT, OpenAI-клиент, команды, аватар
- Слушает микрофон в отдельном потоке (STT)
- Обрабатывает распознанный текст: команда или ИИ
- Стримит ответ от LLM, разбивает на предложения, озвучивает
- Пишет состояние аватара
- Idle-loop — говорит фразы при тишине
- Обрабатывает прерывания и выход

**Когда править:** при изменении логики диалога или порядка обработки.

---

### `core/avatar_server.py`
**Роль:** локальный HTTP-сервер для аватара.
**Что делает:**
- Отдаёт `legion_avatar.html` на `http://127.0.0.1:8765/`
- Отдаёт `avatar_state.json` (состояние аватара)
- Решает CORS-проблему `file://`

**Когда править:** если менять порт или добавлять новые эндпоинты.

---

## 📂 `audio/` — аудио

### `audio/audio_utils.py`
**Роль:** низкоуровневая обработка сигнала.
**Что делает:**
- `pcm_bytes_to_float32` — int16 → float32
- `rms_energy` — громкость
- `is_speech` — простой VAD по энергии
- `highpass_filter` — убирает гул (через scipy)
- `normalize_audio` — RMS-нормализация
- `float32_to_pcm_bytes` — обратно в PCM

**Когда править:** если хочешь другой алгоритм VAD или шумодава.

---

### `audio/stt.py`
**Роль:** распознавание речи (Vosk).
**Что делает:**
- Загружает Vosk-модель
- Опционально применяет грамматику (подсказки команд)
- Работает в отдельном потоке
- Применяет VAD, шумодав, нормализацию
- Фильтрует по confidence
- Вызывает callback `on_text(text, confidence)`

**Когда править:** если менять модель или логику VAD.

---

### `audio/tts.py`
**Роль:** синтез речи (Silero).
**Что делает:**
- Загружает модель Silero
- Разбивает текст на предложения
- Синтезирует каждое предложение
- Варьирует скорость ±4%
- Кэширует повторяющиеся фразы (LRU)
- Играет через `sounddevice`
- Поддерживает прерывание

**Когда править:** при смене голоса или добавлении эффектов.

---

## 📂 `commands/` — команды

### `commands/processor.py`
**Роль:** точка входа для команд.
**Что делает:**
- Создаёт `CommandContext` (доступ к TTS, голосам)
- Регистрирует базовые команды
- Загружает плагины через `CommandRegistry`
- `process(text)` — ищет подходящую команду и выполняет

**Когда править:** при добавлении «встроенных» команд вне плагинов.

---

### `commands/registry.py`
**Роль:** реестр команд + автозагрузка плагинов.
**Что делает:**
- Хранит список команд
- `find(text)` — находит первую подходящую
- `load_plugins()` — сканирует `commands/plugins/` и импортирует все модули, вызывая `register(registry)`

**Когда править:** если менять протокол команд.

---

### `commands/plugins/system.py`
**Роль:** системные команды.
**Команды:**
- `TimeCommand` — время
- `DateCommand` — дата и день недели
- `BatteryCommand` — заряд батареи
- `CpuCommand` — загрузка CPU
- `MemoryCommand` — ОЗУ
- `DiskCommand` — диск
- `TaskManagerCommand` — диспетчер задач
- `SettingsCommand` — параметры Windows
- `CalcCommand`, `NotepadCommand`, `ExplorerCommand`, `TerminalCommand`
- `ShutdownCommand`, `RebootCommand`, `SleepCommand`, `CancelShutdownCommand`

---

### `commands/plugins/media.py`
**Роль:** звук, медиа, яркость.
**Команды:**
- `MuteCommand`, `VolumeUpCommand`, `VolumeDownCommand`
- `PlayPauseCommand`, `NextTrackCommand`, `PrevTrackCommand`
- `BrightnessCommand`

---

### `commands/plugins/web.py`
**Роль:** браузер и веб.
**Команды:**
- `BrowserCommand`, `YouTubeCommand`, `TelegramCommand`, `GithubCommand`
- `SearchCommand` — поиск в Google

---

### `commands/plugins/windows.py`
**Роль:** окна, клавиши, мышь, буфер.
**Команды:**
- `CloseWindowCommand`, `MinimizeAllCommand`, `AltTabCommand`, `MaximizeCommand`
- `MouseUpCommand`, `MouseDownCommand`, `MouseLeftCommand`, `MouseRightCommand`
- `ClickCommand`, `ScrollCommand`
- `CopyCommand`, `PasteCommand`, `UndoCommand`
- `EnterCommand`, `EscapeCommand`

---

## 📂 `assets/` — ресурсы

### `assets/legion_avatar.html`
HTML-аватар с CSS-анимациями. 4 состояния (`idle`, `listening`, `thinking`, `speaking`). Опрашивает `avatar_state.json` каждые 200 мс.

### `assets/avatar_state.json`
Файл состояния (перезаписывается ассистентом).
```json
{"state": "idle", "text": "Слушаю"}
```
**В .gitignore** — не коммитится.

---

## 📂 `docs/` — документация

| Файл | О чём |
|---|---|
| `ARCHITECTURE.md` | этот файл |
| `MODELS.md` | как скачать модели |
| `COMMANDS.md` | список команд |
| `CONFIG.md` | описание config.yaml |
| `PLUGINS.md` | как писать плагины |

---

## 📂 `model/` — заглушка для Vosk

Папка существует, но пуста. Внутри — `README.md` с инструкцией.

**В .gitignore** — сама модель не коммитится.

---

## 🔄 Поток данных

```
🎤 Микрофон
   ↓
audio/stt.py (VAD, шумодав, Vosk)
   ↓
core/assistant.py::_on_stt_text
   ↓
   ├── команда? → commands/processor.py → плагин
   └── диалог? → core/assistant.py::_ask_ai
                     ↓
                 LM Studio (LLM)
                     ↓
                 audio/tts.py (Silero)
                     ↓
                 🔊 Динамики
```

Параллельно:
```
core/assistant.py::_write_avatar_state
   ↓
assets/avatar_state.json
   ↓
core/avatar_server.py (HTTP)
   ↓
assets/legion_avatar.html (браузер)
```