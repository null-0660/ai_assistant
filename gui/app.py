"""
Главное окно Легиона — tkinter GUI.
Тёмная тема, минималистичный интерфейс.
"""
import os
import sys
import time
import json
import queue
import logging
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, font as tkfont
from typing import Optional

from core.config_loader import LegionConfig, load_config
from core.logger import log
from core.avatar_server import AvatarServer
from gui.log_handler import QueueLogHandler
from gui.chat_engine import ChatEngine
from core.assistant import LegionAssistant


# ═══════════════════════════════════════════════
# ЦВЕТА (тёмная тема)
# ═══════════════════════════════════════════════
BG           = "#1a1a1a"
PANEL        = "#242424"
PANEL_2      = "#2d2d2d"
PANEL_3      = "#343434"
BORDER       = "#3a3a3a"
TEXT         = "#e8e8e8"
TEXT_DIM     = "#888888"
ACCENT       = "#4a9eff"
ACCENT_HOVER = "#5aaeff"
RED          = "#e05252"
GREEN        = "#4caf50"
YELLOW       = "#ffb74d"


class LegionGUI:

    def __init__(self, cfg: LegionConfig):
        self.cfg = cfg
        self.log_queue: queue.Queue = queue.Queue()
        self._assistant: Optional[LegionAssistant] = None
        self._assistant_thread: Optional[threading.Thread] = None
        self._chat_engine: Optional[ChatEngine] = None
        self._avatar_server: Optional[AvatarServer] = None
        self._chat_in_progress = False

        self.root = tk.Tk()
        self.root.title("Легион — AI Assistant")
        self.root.geometry("1280x800")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG)

        self._setup_logging()
        self._setup_fonts()
        self._build_ui()
        self._start_avatar_server()
        self._poll_log_queue()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ═══════════════════════════════════════════
    # Инициализация
    # ═══════════════════════════════════════════
    def _setup_logging(self) -> None:
        handler = QueueLogHandler(self.log_queue)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        ))
        logging.getLogger("ЛЕГИОН").addHandler(handler)

    def _setup_fonts(self) -> None:
        self.font_ui = tkfont.Font(family="Segoe UI", size=11)
        self.font_ui_bold = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.font_logo = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        self.font_log = tkfont.Font(family="Consolas", size=9)
        self.font_chat = tkfont.Font(family="Segoe UI", size=11)

    # ═══════════════════════════════════════════
    # Построение UI
    # ═══════════════════════════════════════════
    def _build_ui(self) -> None:
        # Главный контейнер — две колонки
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True)

        # ─── Левая панель ───────────────────
        self._build_left_panel(main)

        # Разделитель
        sep = tk.Frame(main, bg=BORDER, width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y)

        # ─── Правая панель ─────────────────
        self._build_right_panel(main)

    def _build_left_panel(self, parent: tk.Frame) -> None:
        left = tk.Frame(parent, bg=PANEL, width=260)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        # Логотип
        logo_frame = tk.Frame(left, bg=PANEL)
        logo_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        tk.Label(
            logo_frame, text="🤖 ЛЕГИОН",
            bg=PANEL, fg=TEXT, font=self.font_logo,
        ).pack(anchor="w")

        tk.Label(
            logo_frame, text="AI Assistant v4.5",
            bg=PANEL, fg=TEXT_DIM, font=self.font_ui,
        ).pack(anchor="w")

        # Разделитель
        tk.Frame(left, bg=BORDER, height=1).pack(fill=tk.X, padx=20, pady=15)

        # Кнопки
        btn_frame = tk.Frame(left, bg=PANEL)
        btn_frame.pack(fill=tk.X, padx=15, pady=5)

        self.btn_avatar = self._make_button(
            btn_frame, "🎨  Открыть аватар", self._on_open_avatar
        )
        self.btn_avatar.pack(fill=tk.X, pady=4)

        self.btn_voice = self._make_button(
            btn_frame, "🎤  Запустить голос", self._on_toggle_voice
        )
        self.btn_voice.pack(fill=tk.X, pady=4)

        self.btn_stop = self._make_button(
            btn_frame, "⏹  Остановить голос", self._on_stop_voice
        )
        self.btn_stop.pack(fill=tk.X, pady=4)
        self.btn_stop.configure(state=tk.DISABLED)

        # Разделитель
        tk.Frame(left, bg=BORDER, height=1).pack(fill=tk.X, padx=20, pady=15)

        # Статус
        status_frame = tk.Frame(left, bg=PANEL)
        status_frame.pack(fill=tk.X, padx=20)

        tk.Label(
            status_frame, text="СТАТУС",
            bg=PANEL, fg=TEXT_DIM, font=self.font_ui_bold,
        ).pack(anchor="w")

        self.status_label = tk.Label(
            status_frame, text="●  Готов",
            bg=PANEL, fg=GREEN, font=self.font_ui,
        )
        self.status_label.pack(anchor="w", pady=(5, 0))

        self.status_sub = tk.Label(
            status_frame, text="Голосовой режим выключен",
            bg=PANEL, fg=TEXT_DIM, font=self.font_ui,
            wraplength=220, justify="left",
        )
        self.status_sub.pack(anchor="w", pady=(2, 0))

        # Разделитель
        tk.Frame(left, bg=BORDER, height=1).pack(fill=tk.X, padx=20, pady=15)

        # Информация
        info_frame = tk.Frame(left, bg=PANEL)
        info_frame.pack(fill=tk.X, padx=20)

        tk.Label(
            info_frame, text="МОДЕЛЬ",
            bg=PANEL, fg=TEXT_DIM, font=self.font_ui_bold,
        ).pack(anchor="w")

        tk.Label(
            info_frame, text=self.cfg.ai.model_name,
            bg=PANEL, fg=TEXT, font=self.font_ui,
            wraplength=220, justify="left",
        ).pack(anchor="w", pady=(5, 0))

        # Растяжка
        tk.Frame(left, bg=PANEL).pack(fill=tk.BOTH, expand=True)

        # Подпись снизу
        tk.Label(
            left, text="◈ Работает локально",
            bg=PANEL, fg=TEXT_DIM, font=("Segoe UI", 9),
        ).pack(side=tk.BOTTOM, pady=15)

    def _build_right_panel(self, parent: tk.Frame) -> None:
        right = tk.Frame(parent, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ─── Верх: ЧАТ ─────────────────────
        top = tk.Frame(right, bg=BG)
        top.pack(fill=tk.BOTH, expand=True)

        self._build_chat(top)

        # Горизонтальный разделитель
        tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)

        # ─── Низ: ЛОГ ──────────────────────
        bottom = tk.Frame(right, bg=BG)
        bottom.pack(fill=tk.BOTH, expand=True)

        self._build_log(bottom)

    def _build_chat(self, parent: tk.Frame) -> None:
        header = tk.Frame(parent, bg=PANEL)
        header.pack(fill=tk.X)

        tk.Label(
            header, text="💬  ЧАТ",
            bg=PANEL, fg=TEXT, font=self.font_ui_bold,
        ).pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(
            header, text="текстовый режим (без голоса)",
            bg=PANEL, fg=TEXT_DIM, font=("Segoe UI", 9),
        ).pack(side=tk.LEFT)

        # Область диалога
        chat_outer = tk.Frame(parent, bg=BG)
        chat_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 5))

        self.chat_text = tk.Text(
            chat_outer,
            bg=PANEL_2, fg=TEXT,
            font=self.font_chat,
            wrap=tk.WORD,
            relief=tk.FLAT, bd=0,
            padx=15, pady=10,
            insertbackground=TEXT,
            state=tk.DISABLED,
            spacing1=2, spacing3=6,
        )
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        chat_scroll = tk.Scrollbar(
            chat_outer, command=self.chat_text.yview,
            bg=PANEL_3, troughcolor=PANEL,
            activebackground=ACCENT,
            relief=tk.FLAT, bd=0, width=10,
        )
        chat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text.configure(yscrollcommand=chat_scroll.set)

        # Теги для диалога
        self.chat_text.tag_configure(
            "user_name", foreground=ACCENT, font=self.font_ui_bold, spacing1=8
        )
        self.chat_text.tag_configure(
            "user_text", foreground=TEXT, lmargin1=10, lmargin2=10
        )
        self.chat_text.tag_configure(
            "ai_name", foreground=GREEN, font=self.font_ui_bold, spacing1=8
        )
        self.chat_text.tag_configure(
            "ai_text", foreground=TEXT, lmargin1=10, lmargin2=10
        )
        self.chat_text.tag_configure(
            "error_text", foreground=RED, lmargin1=10, lmargin2=10
        )

        # ─── Поле ввода ────────────────────
        input_outer = tk.Frame(parent, bg=BG)
        input_outer.pack(fill=tk.X, padx=15, pady=(5, 12))

        input_frame = tk.Frame(input_outer, bg=PANEL_3)
        input_frame.pack(fill=tk.X)

        self.chat_entry = tk.Entry(
            input_frame,
            bg=PANEL_3, fg=TEXT,
            font=self.font_chat,
            relief=tk.FLAT, bd=0,
            insertbackground=TEXT,
        )
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12, pady=10)
        self.chat_entry.bind("<Return>", lambda e: self._on_send_chat())

        self.btn_send = tk.Button(
            input_frame, text="Отправить  ↵",
            command=self._on_send_chat,
            bg=ACCENT, fg="#ffffff",
            activebackground=ACCENT_HOVER, activeforeground="#ffffff",
            relief=tk.FLAT, bd=0,
            font=self.font_ui_bold,
            padx=20, pady=8,
            cursor="hand2",
        )
        self.btn_send.pack(side=tk.RIGHT, padx=6, pady=6)

    def _build_log(self, parent: tk.Frame) -> None:
        header = tk.Frame(parent, bg=PANEL)
        header.pack(fill=tk.X)

        tk.Label(
            header, text="📜  ЛОГ",
            bg=PANEL, fg=TEXT, font=self.font_ui_bold,
        ).pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(
            header, text="системные события, распознавание, ответы",
            bg=PANEL, fg=TEXT_DIM, font=("Segoe UI", 9),
        ).pack(side=tk.LEFT)

        self.btn_clear_log = tk.Button(
            header, text="Очистить",
            command=self._on_clear_log,
            bg=PANEL_2, fg=TEXT_DIM,
            activebackground=PANEL_3, activeforeground=TEXT,
            relief=tk.FLAT, bd=0,
            font=("Segoe UI", 9),
            padx=10, pady=3,
            cursor="hand2",
        )
        self.btn_clear_log.pack(side=tk.RIGHT, padx=15, pady=6)

        log_outer = tk.Frame(parent, bg=BG)
        log_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 12))

        self.log_text = tk.Text(
            log_outer,
            bg=PANEL_2, fg=TEXT_DIM,
            font=self.font_log,
            wrap=tk.WORD,
            relief=tk.FLAT, bd=0,
            padx=12, pady=10,
            state=tk.DISABLED,
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_scroll = tk.Scrollbar(
            log_outer, command=self.log_text.yview,
            bg=PANEL_3, troughcolor=PANEL,
            activebackground=ACCENT,
            relief=tk.FLAT, bd=0, width=10,
        )
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        # Цвета для уровней
        self.log_text.tag_configure("INFO", foreground=TEXT_DIM)
        self.log_text.tag_configure("WARNING", foreground=YELLOW)
        self.log_text.tag_configure("ERROR", foreground=RED)
        self.log_text.tag_configure("DEBUG", foreground="#666666")

    def _make_button(self, parent: tk.Frame, text: str, command):
        btn = tk.Button(
            parent, text=text, command=command,
            bg=PANEL_2, fg=TEXT,
            activebackground=ACCENT, activeforeground="#ffffff",
            relief=tk.FLAT, bd=0,
            font=self.font_ui,
            padx=14, pady=10,
            cursor="hand2",
            anchor="w", justify="left",
        )

        def on_enter(e):
            if btn["state"] != tk.DISABLED:
                btn.configure(bg=PANEL_3)

        def on_leave(e):
            if btn["state"] != tk.DISABLED:
                btn.configure(bg=PANEL_2)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # ═══════════════════════════════════════════
    # Логи → GUI
    # ═══════════════════════════════════════════
    def _poll_log_queue(self) -> None:
        try:
            while True:
                line = self.log_queue.get_nowait()
                self._append_log(line)
        except queue.Empty:
            pass
        self.root.after(80, self._poll_log_queue)

    def _append_log(self, line: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        tag = "INFO"
        if "[ERROR]" in line:
            tag = "ERROR"
        elif "[WARNING]" in line:
            tag = "WARNING"
        elif "[DEBUG]" in line:
            tag = "DEBUG"
        self.log_text.insert(tk.END, line + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _on_clear_log(self) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    # ═══════════════════════════════════════════
    # Аватар
    # ═══════════════════════════════════════════
    def _start_avatar_server(self) -> None:
        try:
            assets_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "assets",
            )
            self._avatar_server = AvatarServer(
                assets_dir,
                host=self.cfg.avatar.host,
                port=self.cfg.avatar.port,
            )
            self._avatar_server.start()
            log.info(f"Avatar HTTP-сервер: {self._avatar_server.url}")
        except Exception as e:
            log.error(f"Не удалось запустить avatar server: {e}")
            self._avatar_server = None

    def _on_open_avatar(self) -> None:
        if self._avatar_server is None:
            log.error("Avatar сервер не запущен.")
            return
        try:
            webbrowser.open(self._avatar_server.url)
            log.info(f"Открываю аватар: {self._avatar_server.url}")
        except Exception as e:
            log.error(f"Не открыть аватар: {e}")

    # ═══════════════════════════════════════════
    # Голосовой ассистент
    # ═══════════════════════════════════════════
    def _on_toggle_voice(self) -> None:
        if self._assistant_thread is not None and self._assistant_thread.is_alive():
            self._on_stop_voice()
            return
        self._start_voice()

    def _start_voice(self) -> None:
        if self._assistant_thread is not None and self._assistant_thread.is_alive():
            return

        self._set_status("●  Загрузка...", YELLOW, "Инициализация голосового режима")
        self.btn_voice.configure(state=tk.DISABLED)

        def worker():
            try:
                self._assistant = LegionAssistant(
                    self.cfg,
                    avatar_server=self._avatar_server,
                )
                self.root.after(0, lambda: self._set_status(
                    "●  Голос активен", GREEN, "Слушаю вас (микрофон включён)"
                ))
                self.root.after(0, lambda: self.btn_stop.configure(state=tk.NORMAL))
                self._assistant.run()
            except Exception as e:
                log.error(f"Ошибка голосового режима: {e}")
                self.root.after(0, lambda: self._set_status(
                    "●  Ошибка", RED, str(e)[:60]
                ))
            finally:
                self.root.after(0, self._on_voice_stopped)

        self._assistant_thread = threading.Thread(target=worker, daemon=True)
        self._assistant_thread.start()

    def _on_stop_voice(self) -> None:
        if self._assistant is not None:
            log.info("Остановка голосового режима...")
            self._assistant._stop_event.set()
            self._set_status("●  Остановка...", YELLOW, "")

    def _on_voice_stopped(self) -> None:
        self._assistant = None
        self.btn_voice.configure(state=tk.NORMAL)
        self.btn_stop.configure(state=tk.DISABLED)
        self._set_status("●  Готов", GREEN, "Голосовой режим выключен")

    def _set_status(self, line: str, color: str, sub: str) -> None:
        self.status_label.configure(text=line, fg=color)
        self.status_sub.configure(text=sub)

    # ═══════════════════════════════════════════
    # Чат
    # ═══════════════════════════════════════════
    def _on_send_chat(self) -> None:
        text = self.chat_entry.get().strip()
        if not text or self._chat_in_progress:
            return

        self.chat_entry.delete(0, tk.END)
        self._chat_in_progress = True
        self.btn_send.configure(state=tk.DISABLED)

        self._append_chat_user(text)

        if self._chat_engine is None:
            self._chat_engine = ChatEngine(self.cfg)

        # Буфер для стриминга
        chat_buffer = {"text": "", "started": False}

        def on_chunk(token: str) -> None:
            chat_buffer["text"] += token
            if not chat_buffer["started"]:
                chat_buffer["started"] = True
                self.root.after(0, lambda: self._append_chat_ai_start())
            self.root.after(0, lambda t=token: self._append_chat_ai_chunk(t))

        def on_done(full: str) -> None:
            self.root.after(0, self._finish_chat)

        def on_error(err: str) -> None:
            self.root.after(0, lambda: self._append_chat_error(err))
            self.root.after(0, self._finish_chat)

        self._chat_engine.ask(text, on_chunk=on_chunk, on_done=on_done, on_error=on_error)

    def _finish_chat(self) -> None:
        self._chat_in_progress = False
        self.btn_send.configure(state=tk.NORMAL)
        self.chat_entry.focus_set()

    def _append_chat_user(self, text: str) -> None:
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, "Вы\n", "user_name")
        self.chat_text.insert(tk.END, text + "\n\n", "user_text")
        self.chat_text.see(tk.END)
        self.chat_text.configure(state=tk.DISABLED)

    def _append_chat_ai_start(self) -> None:
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, "Легион\n", "ai_name")
        self.chat_text.configure(state=tk.DISABLED)

    def _append_chat_ai_chunk(self, token: str) -> None:
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, token, "ai_text")
        self.chat_text.see(tk.END)
        self.chat_text.configure(state=tk.DISABLED)

    def _append_chat_error(self, err: str) -> None:
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"\n[Ошибка: {err}]\n\n", "error_text")
        self.chat_text.see(tk.END)
        self.chat_text.configure(state=tk.DISABLED)

    # ═══════════════════════════════════════════
    # Завершение
    # ═══════════════════════════════════════════
    def _on_close(self) -> None:
        log.info("Закрытие окна...")
        if self._assistant is not None:
            self._assistant._stop_event.set()
            time.sleep(0.3)
        if self._avatar_server is not None:
            try:
                self._avatar_server.stop()
            except Exception:
                pass
        self.root.destroy()

    def run(self) -> None:
        # Приветствие в чате
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(
            tk.END,
            "Легион\n", "ai_name"
        )
        self.chat_text.insert(
            tk.END,
            "Привет! Я текстовый режим. Могу общаться печатая. "
            "Для голосового режима нажми «Запустить голос» слева.\n\n",
            "ai_text"
        )
        self.chat_text.configure(state=tk.DISABLED)
        self.chat_entry.focus_set()

        self.root.mainloop()