"""
Плагины: окна, клавиши, мышь, буфер обмена.
"""
import pyautogui


class CloseWindowCommand:
    name = "close_window"

    def matches(self, text: str) -> bool:
        return any(x in text for x in [
            "закрой окно", "закрыть окно", "закрой приложение",
        ])

    def execute(self, text, ctx) -> bool:
        ctx.say("Закрываю.")
        pyautogui.hotkey('alt', 'f4')
        return True


class MinimizeAllCommand:
    name = "minimize_all"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["сверни всё", "сверни окна", "рабочий стол"])

    def execute(self, text, ctx) -> bool:
        ctx.say("Сворачиваю.")
        pyautogui.hotkey('win', 'd')
        return True


class AltTabCommand:
    name = "alt_tab"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["переключи окно", "смени окно", "альт таб"])

    def execute(self, text, ctx) -> bool:
        pyautogui.hotkey('alt', 'tab')
        ctx.say("Переключаю.")
        return True


class MaximizeCommand:
    name = "maximize"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["разверни окно", "на весь экран", "максимизируй"])

    def execute(self, text, ctx) -> bool:
        pyautogui.hotkey('win', 'up')
        ctx.say("Развернул.")
        return True


class MouseUpCommand:
    name = "mouse_up"

    def matches(self, text: str) -> bool:
        return "мышь вверх" in text

    def execute(self, text, ctx) -> bool:
        pyautogui.moveRel(0, -100)
        ctx.say("Готово.")
        return True


class MouseDownCommand:
    name = "mouse_down"

    def matches(self, text: str) -> bool:
        return "мышь вниз" in text

    def execute(self, text, ctx) -> bool:
        pyautogui.moveRel(0, 100)
        ctx.say("Готово.")
        return True


class MouseLeftCommand:
    name = "mouse_left"

    def matches(self, text: str) -> bool:
        return "мышь влево" in text

    def execute(self, text, ctx) -> bool:
        pyautogui.moveRel(-100, 0)
        ctx.say("Готово.")
        return True


class MouseRightCommand:
    name = "mouse_right"

    def matches(self, text: str) -> bool:
        return "мышь вправо" in text

    def execute(self, text, ctx) -> bool:
        pyautogui.moveRel(100, 0)
        ctx.say("Готово.")
        return True


class ClickCommand:
    name = "click"

    def matches(self, text: str) -> bool:
        return any(x in text for x in [
            "левый клик", "правый клик", "двойной клик", "кликни мышью",
        ])

    def execute(self, text, ctx) -> bool:
        if "правый" in text:
            pyautogui.rightClick()
        elif "двойной" in text:
            pyautogui.doubleClick()
        else:
            pyautogui.click()
        ctx.say("Кликнул.")
        return True


class ScrollCommand:
    name = "scroll"

    def matches(self, text: str) -> bool:
        return any(x in text for x in [
            "прокрути вниз", "прокрути вверх", "скролл вниз", "скролл вверх",
        ])

    def execute(self, text, ctx) -> bool:
        pyautogui.scroll(-3 if "вниз" in text else 3)
        ctx.say("Прокрутил.")
        return True


class CopyCommand:
    name = "copy"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["скопируй", "копировать текст"])

    def execute(self, text, ctx) -> bool:
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        ctx.say("Скопировал.")
        return True


class PasteCommand:
    name = "paste"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["вставь", "вставить текст"])

    def execute(self, text, ctx) -> bool:
        pyautogui.hotkey('ctrl', 'v')
        ctx.say("Вставил.")
        return True


class UndoCommand:
    name = "undo"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["отмени действие", "ctrl z"])

    def execute(self, text, ctx) -> bool:
        pyautogui.hotkey('ctrl', 'z')
        ctx.say("Отменил.")
        return True


class EnterCommand:
    name = "enter"

    def matches(self, text: str) -> bool:
        return "нажми enter" in text or "нажми ввод" in text

    def execute(self, text, ctx) -> bool:
        pyautogui.press('enter')
        ctx.say("Enter.")
        return True


class EscapeCommand:
    name = "escape"

    def matches(self, text: str) -> bool:
        return "нажми escape" in text or "нажми эскейп" in text

    def execute(self, text, ctx) -> bool:
        pyautogui.press('escape')
        ctx.say("Escape.")
        return True


def register(registry):
    for cls in [
        CloseWindowCommand, MinimizeAllCommand, AltTabCommand, MaximizeCommand,
        MouseUpCommand, MouseDownCommand, MouseLeftCommand, MouseRightCommand,
        ClickCommand, ScrollCommand, CopyCommand, PasteCommand, UndoCommand,
        EnterCommand, EscapeCommand,
    ]:
        registry.register(cls())