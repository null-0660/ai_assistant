"""
Плагины: система, питание, информация.
"""
import os
import re
import time
import datetime
import subprocess

import psutil

from core.logger import log


MONTHS_RU = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]
DAYS_RU = [
    "понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье",
]


class TimeCommand:
    name = "time"

    def matches(self, text: str) -> bool:
        return any(x in text for x in [
            "который час", "сколько время", "сколько часов", "время сейчас",
        ]) or text.strip() == "время"

    def execute(self, text, ctx) -> bool:
        ctx.say(f"Сейчас {time.strftime('%H:%M')}.")
        return True


class DateCommand:
    name = "date"

    def matches(self, text: str) -> bool:
        return any(x in text for x in [
            "какое число", "какая дата", "какой сегодня день", "день недели",
        ]) or text.strip() in ("дата", "число")

    def execute(self, text, ctx) -> bool:
        now = datetime.datetime.now()
        if "день недели" in text or "какой сегодня день" in text:
            ctx.say(f"Сегодня {DAYS_RU[now.weekday()]}.")
        else:
            ctx.say(f"Сегодня {now.day} {MONTHS_RU[now.month - 1]} {now.year} года.")
        return True


class BatteryCommand:
    name = "battery"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["заряд", "батарея", "аккумулятор"])

    def execute(self, text, ctx) -> bool:
        bat = psutil.sensors_battery()
        if bat:
            state = "подключён к сети" if bat.power_plugged else "от батареи"
            ctx.say(f"Заряд {int(bat.percent)} процентов, {state}.")
        else:
            ctx.say("Данные о батарее недоступны.")
        return True


class CpuCommand:
    name = "cpu"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["загрузка процессора", "цпу", "процессор"])

    def execute(self, text, ctx) -> bool:
        cpu = psutil.cpu_percent(interval=1)
        ctx.say(f"Загрузка процессора {cpu} процентов.")
        return True


class MemoryCommand:
    name = "memory"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["оперативная память", "озу", "память"])

    def execute(self, text, ctx) -> bool:
        mem = psutil.virtual_memory()
        used = mem.used / (1024 ** 3)
        total = mem.total / (1024 ** 3)
        ctx.say(f"Используется {used:.1f} из {total:.1f} гигабайт памяти.")
        return True


class DiskCommand:
    name = "disk"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["место на диске", "свободное место", "диск"])

    def execute(self, text, ctx) -> bool:
        path = "C:\\" if os.name == "nt" else "/"
        d = psutil.disk_usage(path)
        free = d.free / (1024 ** 3)
        total = d.total / (1024 ** 3)
        ctx.say(f"Свободно {free:.0f} из {total:.0f} гигабайт.")
        return True


class TaskManagerCommand:
    name = "taskmgr"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["диспетчер задач", "task manager"])

    def execute(self, text, ctx) -> bool:
        ctx.say("Открываю диспетчер задач.")
        os.system("start taskmgr")
        return True


class SettingsCommand:
    name = "settings"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["параметры системы", "настройки системы", "открой параметры"])

    def execute(self, text, ctx) -> bool:
        ctx.say("Открываю параметры.")
        os.system("start ms-settings:")
        return True


class CalcCommand:
    name = "calc"

    def matches(self, text: str) -> bool:
        return "калькулятор" in text

    def execute(self, text, ctx) -> bool:
        ctx.say("Открываю калькулятор.")
        os.system("start calc")
        return True


class NotepadCommand:
    name = "notepad"

    def matches(self, text: str) -> bool:
        return "блокнот" in text or "notepad" in text

    def execute(self, text, ctx) -> bool:
        ctx.say("Открываю блокнот.")
        os.system("start notepad")
        return True


class ExplorerCommand:
    name = "explorer"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["проводник", "мой компьютер", "открой папку"])

    def execute(self, text, ctx) -> bool:
        ctx.say("Открываю проводник.")
        os.system("start explorer")
        return True


class TerminalCommand:
    name = "terminal"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["терминал", "консоль", "командная строка", "powershell"])

    def execute(self, text, ctx) -> bool:
        if "powershell" in text:
            ctx.say("Открываю PowerShell.")
            os.system("start powershell")
        else:
            ctx.say("Открываю терминал.")
            os.system("start cmd")
        return True


class ShutdownCommand:
    name = "shutdown"

    def matches(self, text: str) -> bool:
        return any(x in text for x in [
            "выключи компьютер", "завершение работы", "shutdown",
        ])

    def execute(self, text, ctx) -> bool:
        ctx.say("Выключаю через 10 секунд. Скажите отмена чтобы остановить.")
        time.sleep(10)
        os.system("shutdown /s /t 0")
        return True


class RebootCommand:
    name = "reboot"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["перезагрузка", "перезагрузить", "рестарт"])

    def execute(self, text, ctx) -> bool:
        ctx.say("Перезагружаю через 10 секунд.")
        time.sleep(10)
        os.system("shutdown /r /t 0")
        return True


class SleepCommand:
    name = "sleep"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["режим сна", "спящий режим"]) or text.strip() == "сон"

    def execute(self, text, ctx) -> bool:
        ctx.say("Сон через 5 секунд.")
        time.sleep(5)
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return True


class CancelShutdownCommand:
    name = "cancel_shutdown"

    def matches(self, text: str) -> bool:
        return "отмена" in text or "отмени выключение" in text

    def execute(self, text, ctx) -> bool:
        os.system("shutdown /a")
        ctx.say("Выключение отменено.")
        return True


def register(registry):
    for cls in [
        TimeCommand, DateCommand, BatteryCommand, CpuCommand, MemoryCommand,
        DiskCommand, TaskManagerCommand, SettingsCommand, CalcCommand,
        NotepadCommand, ExplorerCommand, TerminalCommand, ShutdownCommand,
        RebootCommand, SleepCommand, CancelShutdownCommand,
    ]:
        registry.register(cls())