# 📦 Как скачать модели

ЛЕГИОН **не включает** модели в репозиторий (они большие). Скачай их отдельно.

---

## 1. Vosk — распознавание речи (RU)

**Куда:** папка `model/` в корне проекта.

**Откуда:** [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)

**Рекомендую:**
- `vosk-model-ru-0.42` (~1.8 GB) — большая, точная
- `vosk-model-small-ru-0.22` (~45 MB) — маленькая, быстрая

**Установка:**

1. Скачай ZIP.
2. Распакуй в `model/`, чтобы получилось:
   ```
   ai_assistant/
   └── model/
       ├── am/
       ├── conf/
       ├── graph/
       ├── ivector/
       └── ...
   ```
3. **НЕ** должно быть `model/vosk-model-ru-0.42/...` — только содержимое внутри `model/`.

**Проверка:**
```python
from vosk import Model
m = Model("model")
print("OK")
```

---

## 2. Silero TTS — синтез речи

**Куда:** `v5_ru.pt` в корне проекта.

**Откуда:** [models.silero.ai/models/tts/ru/v5_ru.pt](https://models.silero.ai/models/tts/ru/v5_ru.pt)

**Установка:**

1. Скачай `v5_ru.pt` (~60 MB).
2. Положи в корень рядом с `main.py`:
   ```
   ai_assistant/
   ├── main.py
   ├── v5_ru.pt       ← сюда
   └── ...
   ```

**Голоса:** `kseniya`, `aidar`, `baya`, `xenia`, `eugene`.

---

## 3. LLM — мозг (через LM Studio)

**Куда:** LM Studio сам хранит.

**Откуда:** через UI LM Studio.

**Установка:**

1. Открой LM Studio.
2. Вкладка **Discover** — найди модель.
3. Рекомендую для 16 GB RAM:
   - `google/gemma-3n-e4b-it-text` — быстрая, качественная
   - `google/gemma-4-12b` — тяжелее, но умнее
4. Нажми **Download**.
5. Затем в **Developer → Local Server** — загрузи модель.
6. Запиши `id` модели (видно в **API Model Identifier**).

**Проверка:**
```bash
curl http://127.0.0.1:1234/v1/models
```
Должен вернуть JSON со списком.

---

## 4. Проверка всех моделей

Запусти `python main.py`. В логе должно быть:
```
✅ TEXT  : gemma-3n-e4b-it-text
```

В логе ассистента:
```
Загрузка голоса Silero... OK
Загрузка Vosk... OK
LM Studio URL: http://127.0.0.1:1234/v1
```

Если что-то не так — ассистент напишет, чего не хватает.