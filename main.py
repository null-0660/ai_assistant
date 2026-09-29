"""
Точка входа ЛЕГИОН v4.1.
"""
import sys
import json
import urllib.request
import urllib.error

from core.config_loader import load_config
from core.assistant import LegionAssistant
from core.logger import log


def check_lm_studio(cfg) -> bool:
    """Проверяет LM Studio и наличие нужной модели."""
    base = cfg.ai.lm_studio_url.rstrip("/")

    print("─" * 60)
    print(f"LM Studio URL : {base}")
    print(f"Text model    : {cfg.ai.model_name}")

    if not base.endswith("/v1"):
        print(f"❌ base_url должен заканчиваться на /v1 (сейчас: {base})")
        return False

    url = f"{base}/models"
    try:
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {cfg.ai.lm_studio_key}"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"❌ LM Studio недоступен: {e}")
        print("   Запусти Developer → Local Server в LM Studio.")
        return False
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

    models = [m.get("id") for m in data.get("data", [])]
    print(f"Доступно моделей: {len(models)}")

    if cfg.ai.model_name in models:
        print(f"✅ TEXT  : {cfg.ai.model_name}")
        print("─" * 60)
        return True

    print(f"❌ TEXT  : {cfg.ai.model_name} (не найдена)")
    print("\nДоступные id:")
    for m in models:
        print(f"   - {m}")
    print("─" * 60)
    return False


def main() -> int:
    try:
        cfg = load_config("config.yaml")
    except Exception as e:
        log.error(f"Ошибка загрузки конфига: {e}")
        return 1

    if not check_lm_studio(cfg):
        log.error("Проверка LM Studio не пройдена. Выход.")
        return 2

    assistant = LegionAssistant(cfg)
    assistant.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())