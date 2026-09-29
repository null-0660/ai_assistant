# 📁 Папка `model/` — ЗАГЛУШКА

Здесь должна лежать **модель Vosk для русского языка**.

## Что сюда положить

Скачай одну из моделей:

- **`vosk-model-ru-0.42`** (~1.8 GB) — большая, точная
- **`vosk-model-small-ru-0.22`** (~45 MB) — маленькая, быстрая

## Откуда

[https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)

## Как установить

1. Скачай ZIP-архив.
2. Распакуй **содержимое** в эту папку. Должно получиться:

```
ai_assistant/
└── model/
    ├── am/
    ├── conf/
    ├── graph/
    ├── ivector/
    ├── README.md       ← этот файл
    └── ...
```

⚠️ **НЕ должно быть** вложенной папки:
```
ai_assistant/
└── model/
    └── vosk-model-ru-0.42/    ❌ неправильно
        ├── am/
        └── ...
```

Если так получилось — перемести содержимое `vosk-model-ru-0.42/` на уровень выше.

## Проверка

```python
from vosk import Model
m = Model("model")
print("Vosk OK")
```

## Почему модель не в репозитории

Модель весит 1.8 GB — GitHub не примет такие файлы. Поэтому она в `.gitignore`.