"""
Реестр команд: базовые + плагины с автозагрузкой.
"""
import os
import pkgutil
import importlib
from typing import List, Protocol, TYPE_CHECKING

from number_nol.core.logger import log

if TYPE_CHECKING:
    from number_nol.commands.processor import CommandContext


class Command(Protocol):
    """Интерфейс команды."""
    name: str
    keywords: List[str]

    def matches(self, text: str) -> bool: ...
    def execute(self, text: str, ctx: "CommandContext") -> bool: ...


class CommandRegistry:
    """Хранит команды и ищет подходящую."""

    def __init__(self):
        self.commands: List[Command] = []

    def register(self, cmd: Command) -> None:
        self.commands.append(cmd)

    def find(self, text: str):
        for cmd in self.commands:
            try:
                if cmd.matches(text):
                    return cmd
            except Exception as e:
                log.error(f"Ошибка matches в {cmd}: {e}")
        return None

    def load_plugins(self, package: str = "commands.plugins") -> None:
        """Автозагрузка всех модулей из commands/plugins/."""
        try:
            pkg = importlib.import_module(package)
        except ImportError as e:
            log.warning(f"Пакет плагинов не найден: {e}")
            return

        for _, mod_name, is_pkg in pkgutil.iter_modules(pkg.__path__):
            if mod_name.startswith("_"):
                continue
            full_name = f"{package}.{mod_name}"
            try:
                module = importlib.import_module(full_name)
                if hasattr(module, "register"):
                    module.register(self)
                    log.info(f"Плагин загружен: {full_name}")
            except Exception as e:
                log.error(f"Плагин {full_name} не загружен: {e}")