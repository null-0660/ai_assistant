# 🔌 Как писать плагины

Каждая команда — отдельный класс с методами `matches` и `execute`.

---

## Минимальный плагин

Создай `commands/plugins/my_plugin.py`:

```python
class HelloCommand:
    name = "hello"

    def matches(self, text: str) -> bool:
        return "привет легион" in text

    def execute(self, text, ctx) -> bool:
        ctx.say("И тебе привет!")
        return True


def register(registry):
    registry.register(HelloCommand())
```

Плагин **автоматически загрузится** при следующем запуске.

---

## Интерфейс команды

### `name: str`
Уникальное имя для логов.

### `matches(text) -> bool`
Вызывается для каждой фразы. **Первый** плагин, вернувший `True`, побеждает.

Правила:
- Работай с `text.lower()`
- Не делай тяжёлых операций — вызывается часто
- Используй `any(...)` для списка ключевых слов

### `execute(text, ctx) -> bool`
Возвращает `True` — команда обработана.
Возвращает `False` — фраза уйдёт в LLM.

### `ctx` (CommandContext)
```python
ctx.say("текст")          # озвучить
ctx.tts                    # TTSEngine
ctx.voices                 # список голосов
ctx.current_voice          # текущий голос
```

---

## Пример: погода (заглушка)

```python
import webbrowser
import urllib.parse


class WeatherCommand:
    name = "weather"

    def matches(self, text: str) -> bool:
        return "погода" in text or "погоду" in text

    def execute(self, text, ctx) -> bool:
        city = text.replace("погода", "").replace("погоду", "").strip()
        if not city:
            ctx.say("В каком городе?")
            return True
        ctx.say(f"Смотрю погоду в {city}.")
        webbrowser.open(
            f"https://yandex.ru/pogoda/{urllib.parse.quote(city)}"
        )
        return True


def register(registry):
    registry.register(WeatherCommand())
```

---

## Пример: калькулятор

```python
import re


class CalcCommand:
    name = "calc"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["сколько будет", "посчитай"])

    def execute(self, text, ctx) -> bool:
        expr = re.sub(r'(сколько будет|посчитай)', '', text)
        expr = expr.replace("плюс", "+").replace("минус", "-")
        expr = expr.replace("умножить на", "*").replace("разделить на", "/")

        # Защита от инъекций
        if not re.fullmatch(r'[\d\s+\-*/().]+', expr):
            return False

        try:
            result = eval(expr, {"__builtins__": {}}, {})
            ctx.say(f"Получается {result}.")
        except Exception:
            ctx.say("Не смог посчитать.")
        return True


def register(registry):
    registry.register(CalcCommand())
```

---

## Советы

1. **Имя файла** — `snake_case`, без ведущего `_`.
2. **Имя команды** — уникальное, осмысленное.
3. **`matches`** — быстрый, без сетевых вызовов.
4. **`execute`** — можно долгий, но предупреди через `ctx.say()`.
5. **Регистрация** — функция `register(registry)` обязательна.

---

## Отладка

Если плагин не грузится — смотри лог:

```
[INFO] Плагин загружен: commands.plugins.my_plugin
[ERROR] Плагин commands.plugins.bad не загружен: ...
```

Проверь:
- Файл в `commands/plugins/`
- Есть функция `register(registry)`
- Нет синтаксических ошибок