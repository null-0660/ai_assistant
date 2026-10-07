"""
Плагины: звук, медиа, яркость.
"""
import pyautogui
import screen_brightness_control as sbc

from number_nol.core.logger import log


class MuteCommand:
    name = "mute"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["выключи звук", "без звука", "мьют"])

    def execute(self, text, ctx) -> bool:
        pyautogui.hotkey('volumemute')
        ctx.say("Звук отключён.")
        return True


class VolumeUpCommand:
    name = "volume_up"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["громче", "увеличь громкость", "звук громче"])

    def execute(self, text, ctx) -> bool:
        for _ in range(5):
            pyautogui.hotkey('volumeup')
        ctx.say("Громче.")
        return True


class VolumeDownCommand:
    name = "volume_down"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["тише", "уменьши громкость", "звук тише"])

    def execute(self, text, ctx) -> bool:
        for _ in range(5):
            pyautogui.hotkey('volumedown')
        ctx.say("Тише.")
        return True


class PlayPauseCommand:
    name = "playpause"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["пауза", "стоп музыка", "остановить музыку", "плей"])

    def execute(self, text, ctx) -> bool:
        pyautogui.hotkey('playpause')
        ctx.say("Пауза.")
        return True


class NextTrackCommand:
    name = "next_track"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["следующий трек", "следующая песня", "далее трек"])

    def execute(self, text, ctx) -> bool:
        pyautogui.hotkey('nexttrack')
        ctx.say("Следующий трек.")
        return True


class PrevTrackCommand:
    name = "prev_track"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["предыдущий трек", "предыдущая песня", "назад трек"])

    def execute(self, text, ctx) -> bool:
        pyautogui.hotkey('prevtrack')
        ctx.say("Предыдущий трек.")
        return True


class BrightnessCommand:
    name = "brightness"

    def matches(self, text: str) -> bool:
        return "яркость" in text

    def execute(self, text, ctx) -> bool:
        try:
            if any(x in text for x in ["максимум", "сто", "добавь", "ярче"]):
                sbc.set_brightness(100)
                ctx.say("Яркость максимальная.")
            elif any(x in text for x in ["минимум", "уменьш", "ноль", "снизь", "темнее"]):
                sbc.set_brightness(20)
                ctx.say("Яркость минимальная.")
            else:
                curr = sbc.get_brightness()
                level = curr[0] if isinstance(curr, list) else curr
                ctx.say(f"Яркость {level} процентов.")
        except Exception as e:
            log.warning(f"Яркость: {e}")
            ctx.say("Управление яркостью недоступно.")
        return True


def register(registry):
    for cls in [
        MuteCommand, VolumeUpCommand, VolumeDownCommand, PlayPauseCommand,
        NextTrackCommand, PrevTrackCommand, BrightnessCommand,
    ]:
        registry.register(cls())