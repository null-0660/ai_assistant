"""
Плагины: браузер, поиск.
"""
import re
import urllib.parse
import webbrowser


class BrowserCommand:
    name = "browser"

    def matches(self, text: str) -> bool:
        return any(x in text for x in [
            "открой браузер", "открой интернет", "открой хром",
        ])

    def execute(self, text, ctx) -> bool:
        ctx.say("Открываю браузер.")
        webbrowser.open("https://google.com")
        return True


class YouTubeCommand:
    name = "youtube"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["ютуб", "youtube"])

    def execute(self, text, ctx) -> bool:
        ctx.say("Открываю Ютуб.")
        webbrowser.open("https://youtube.com")
        return True


class TelegramCommand:
    name = "telegram"

    def matches(self, text: str) -> bool:
        return "телеграм" in text or "telegram" in text

    def execute(self, text, ctx) -> bool:
        ctx.say("Открываю Telegram.")
        webbrowser.open("https://web.telegram.org")
        return True


class GithubCommand:
    name = "github"

    def matches(self, text: str) -> bool:
        return any(x in text for x in ["гитхаб", "github"])

    def execute(self, text, ctx) -> bool:
        ctx.say("Открываю GitHub.")
        webbrowser.open("https://github.com")
        return True


class SearchCommand:
    name = "search"

    def matches(self, text: str) -> bool:
        return any(x in text for x in [
            "найди в интернете", "найти в интернете", "поиск в интернете", "погугли",
        ])

    def execute(self, text, ctx) -> bool:
        query = text
        for kw in ["найди в интернете", "найти в интернете", "поиск в интернете", "погугли"]:
            query = query.replace(kw, "")
        query = query.strip()
        if query:
            ctx.say(f"Ищу: {query}")
            webbrowser.open(
                f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            )
        else:
            ctx.say("Что искать?")
        return True


def register(registry):
    for cls in [BrowserCommand, YouTubeCommand, TelegramCommand, GithubCommand, SearchCommand]:
        registry.register(cls())