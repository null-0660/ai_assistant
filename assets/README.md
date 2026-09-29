# 📁 Папка `assets/` — ресурсы

## Файлы

### `legion_avatar.html`
HTML-аватар с CSS-анимациями. Открывается автоматически в браузере при запуске ассистента. 4 состояния: `idle`, `listening`, `thinking`, `speaking`.

### `avatar_state.json`
**Генерируется автоматически**, не коммитится в git (в `.gitignore`). Содержит:
```json
{"state": "idle", "text": "Слушаю"}
```

## HTTP-сервер

Отдаётся через `core/avatar_server.py` на `http://127.0.0.1:8765/`. Это решает проблему CORS при `file://`.