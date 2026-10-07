"""
Процессор команд: точка входа + базовые команды.
"""
from dataclasses import dataclass
from typing import List

from number_nol.audio.tts import TTSEngine
from number_nol.commands.registry import CommandRegistry
from number_nol.core.logger import log


@dataclass
class CommandContext:
    """Передаётся в каждую команду — доступ к TTS и состоянию."""
    tts: TTSEngine
    voices: List[str]
    current_voice: str

    def say(self, text: str) -> None:
        self.tts.speak(text, speaker=self.current_voice)


class CommandProcessor:
    """Обрабатывает текст: базовые команды + плагины."""

    def __init__(
        self,
        tts: TTSEngine,
        voices: List[str],
        default_voice: str,
    ):
        self.tts = tts
        self.voices = voices
        self.current_voice = default_voice

        self.registry = CommandRegistry()
        self._register_basic()
        self.registry.load_plugins()

    def _ctx(self) -> CommandContext:
        return CommandContext(
            tts=self.tts,
            voices=self.voices,
            current_voice=self.current_voice,
        )

    def _register_basic(self) -> None:
        """Базовые команды."""
        processor = self

        class ChangeVoice:
            name = "change_voice"

            def matches(self, text: str) -> bool:
                return "голос" in text and any(
                    x in text
                    for x in ["смен", "измен", "помен", "другой", "следующий"]
                )

            def execute(self, text, ctx: CommandContext) -> bool:
                idx = ctx.voices.index(ctx.current_voice)
                new_voice = ctx.voices[(idx + 1) % len(ctx.voices)]
                processor.current_voice = new_voice
                ctx.tts.speak(
                    "Голос изменён. Как вам этот тембр?", speaker=new_voice
                )
                return True

        self.registry.register(ChangeVoice())

    def process(self, text: str) -> bool:
        t = text.lower().strip()
        cmd = self.registry.find(t)
        if cmd is None:
            return False
        try:
            ctx = self._ctx()
            return cmd.execute(t, ctx)
        except Exception as e:
            log.error(f"Ошибка команды {cmd}: {e}")
            self.tts.speak("Команда не выполнена.", speaker=self.current_voice)
            return True