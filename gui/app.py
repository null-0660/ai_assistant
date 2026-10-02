"""
Главное окно Легиона — современный минималистичный GUI.
Стиль: тёмная тема Deep Ocean, аккуратная типографика, чёткая иерархия.
"""
import os
import time
import json
import queue
import logging
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, font as tkfont
from typing import Optional

from core.config_loader import LegionConfig
from core.logger import log
from core.avatar_server import AvatarServer
from gui.log_handler import QueueLogHandler
from gui.chat_engine import ChatEngine
from gui import theme as T
from core.assistant import LegionAssistant


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
        self.root.geometry(f"{T.WINDOW_W}x{T.WINDOW_H}")
        self.root.minsize(T.MIN_W, T.MIN_H)
        self.root.configure(bg=T.BG_ROOT)

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
            "%(asctime)s  %(message)s",
            datefmt="%H:%M:%S",
        ))
        logging.getLogger("ЛЕГИОН").addHandler(handler)

    def _setup_fonts(self) -> None:
        # UI-шрифты
        self.f_logo      = tkfont.Font(family=T.FONT_FAMILY, size=20, weight="bold")
        self.f_subtitle  = tkfont.Font(family=T.FONT_FAMILY, size=10)
        self.f_section   = tkfont.Font(family=T.FONT_FAMILY, size=9, weight="bold")
        self.f_body      = tkfont.Font(family=T.FONT_FAMILY, size=11)
        self.f_body_bold = tkfont.Font(family=T.FONT_FAMILY, size=11, weight="bold")
        self.f_button    = tkfont.Font(family=T.FONT_FAMILY, size=10, weight="bold")
        self.f_small     = tkfont.Font(family=T.FONT_FAMILY, size=9)
        self.f_name      = tkfont.Font(family=T.FONT_FAMILY, size=10, weight="bold")
        self.f_chat      = tkfont.Font(family=T.FONT_FAMILY, size=11)
        self.f_log       = tkfont.Font(family=T.FONT_MONO, size=9)
        self.f_input     = tkfont.Font(family=T.FONT_FAMILY, size=11)

    # ═══════════════════════════════════════════
    # Построение UI
    # ═══════════════════════════════════════════
    def _build_ui(self) -> None:
        main = tk.Frame(self.root, bg=T.BG_ROOT)
        main.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar(main)

        # Разделитель
        tk.Frame(main, bg=T.BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

        self._build_right(main)

    # ────────────────────────────────────────────
    # САЙДБАР
    # ────────────────────────────────────────────
    def _build_sidebar(self, parent: tk.Frame) -> None:
        sidebar = tk.Frame(parent, bg=T.BG_SIDEBAR, width=T.SIDEBAR_WIDTH)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # ─── Логотип ─────────────────────
        logo = tk.Frame(sidebar, bg=T.BG_SIDEBAR)
        logo.pack(fill=tk.X, padx=T.PAD_XL, pady=(T.PAD_XL, T.PAD_LG))

        # Иконка-кружок
        circle = tk.Canvas(
            logo, width=40, height=40,
            bg=T.BG_SIDEBAR, highlightthickness=0,
        )
        circle.pack(side=tk.LEFT)
        circle.create_oval(2, 2, 38, 38, fill=T.ACCENT_DIM, outline=T.ACCENT, width=2)
        circle.create_text(20, 20, text="◈", fill=T.TEXT, font=(T.FONT_FAMILY, 14, "bold"))

        text_box = tk.Frame(logo, bg=T.BG_SIDEBAR)
        text_box.pack(side=tk.LEFT, padx=(T.PAD_MD, 0))

        tk.Label(
            text_box, text="Легион",
            bg=T.BG_SIDEBAR, fg=T.TEXT_HEADING, font=self.f_logo,
        ).pack(anchor="w")
        tk.Label(
            text_box, text="AI Assistant",
            bg=T.BG_SIDEBAR, fg=T.TEXT_DIM, font=self.f_subtitle,
        ).pack(anchor="w")

        # ─── Секция "Управление" ─────────
        self._section_label(sidebar, "УПРАВЛЕНИЕ")

        btn_box = tk.Frame(sidebar, bg=T.BG_SIDEBAR)
        btn_box.pack(fill=tk.X, padx=T.PAD_LG, pady=(0, T.PAD_LG))

        self.btn_avatar = self._make_btn(
            btn_box, "🎨", "Открыть аватар",
            "Открыть HTML-аватар в браузере",
            self._on_open_avatar,
            variant="default",
        )
        self.btn_avatar.pack(fill=tk.X, pady=3)

        self.btn_voice = self._make_btn(
            btn_box, "🎤", "Запустить голос",
            "Активировать микрофон",
            self._on_toggle_voice,
            variant="accent",
        )
        self.btn_voice.pack(fill=tk.X, pady=3)

        self.btn_stop = self._make_btn(
            btn_box, "⏹", "Остановить голос",
            "Выключить микрофон",
            self._on_stop_voice,
            variant="danger",
        )
        self.btn_stop.pack(fill=tk.X, pady=3)
        self.btn_stop.configure(state=tk.DISABLED)

        # ─── Секция "Статус" ──────────────
        self._section_label(sidebar, "СТАТУС")

        status_box = tk.Frame(sidebar, bg=T.BG_SIDEBAR)
        status_box.pack(fill=tk.X, padx=T.PAD_LG, pady=(0, T.PAD_LG))

        status_inner = tk.Frame(status_box, bg=T.BG_PANEL)
        status_inner.pack(fill=tk.X)

        dot_row = tk.Frame(status_inner, bg=T.BG_PANEL)
        dot_row.pack(fill=tk.X, padx=T.PAD_MD, pady=(T.PAD_MD, 4))

        self.status_dot = tk.Canvas(
            dot_row, width=10, height=10,
            bg=T.BG_PANEL, highlightthickness=0,
        )
        self.status_dot.pack(side=tk.LEFT)
        self._dot_item = self.status_dot.create_oval(
            1, 1, 9, 9, fill=T.SUCCESS, outline=""
        )

        self.status_label = tk.Label(
            dot_row, text="Готов",
            bg=T.BG_PANEL, fg=T.TEXT, font=self.f_body_bold,
        )
        self.status_label.pack(side=tk.LEFT, padx=(T.PAD_SM, 0))

        self.status_sub = tk.Label(
            status_inner, text="Голосовой режим выключен",
            bg=T.BG_PANEL, fg=T.TEXT_MUTED, font=self.f_small,
            wraplength=210, justify="left", anchor="w",
        )
        self.status_sub.pack(fill=tk.X, padx=T.PAD_MD, pady=(0, T.PAD_MD))

        # ─── Секция "Модель" ──────────────
        self._section_label(sidebar, "МОДЕЛЬ")

        model_box = tk.Frame(sidebar, bg=T.BG_SIDEBAR)
        model_box.pack(fill=tk.X, padx=T.PAD_LG)

        model_inner = tk.Frame(model_box, bg=T.BG_PANEL)
        model_inner.pack(fill=tk.X)

        tk.Label(
            model_inner, text=cfg_model_name(self.cfg),
            bg=T.BG_PANEL, fg=T.ACCENT, font=self.f_small,
            wraplength=210, justify="left", anchor="w",
            padx=T.PAD_MD, pady=T.PAD_MD,
        ).pack(fill=tk.X)

        # ─── Растяжка ─────────────────────
        tk.Frame(sidebar, bg=T.BG_SIDEBAR).pack(fill=tk.BOTH, expand=True)

        # ─── Футер ────────────────────────
        footer = tk.Frame(sidebar, bg=T.BG_SIDEBAR)
        footer.pack(fill=tk.X, padx=T.PAD_LG, pady=T.PAD_LG)

        tk.Frame(footer, bg=T.BORDER, height=1).pack(fill=tk.X, pady=(0, T.PAD_MD))

        tk.Label(
            footer, text="● Локально · Без облака",
            bg=T.BG_SIDEBAR, fg=T.TEXT_DIM, font=self.f_small,
        ).pack()

    def _section_label(self, parent: tk.Widget, text: str) -> None:
        tk.Label(
            parent, text=text,
            bg=T.BG_SIDEBAR, fg=T.TEXT_DIM,
            font=self.f_section,
        ).pack(anchor="w", padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_SM))

    def _make_btn(
        self, parent, icon: str, text: str, tip: str,
        command, variant: str = "default",
    ) -> tk.Button:
        """Кнопка с иконкой и текстом. Variant: default/accent/danger."""
        colors = {
            "default": (T.BG_PANEL, T.BG_HOVER, T.TEXT),
            "accent":  (T.ACCENT_DIM, T.ACCENT, T.TEXT),
            "danger":  (T.BG_PANEL, T.DANGER_HOVER, T.TEXT),
        }
        bg, hover, fg = colors.get(variant, colors["default"])

        # Фрейм-обёртка
        wrapper = tk.Frame(parent, bg=bg)
        wrapper.pack_propagate(False)

        btn = tk.Button(
            wrapper,
            text=f"  {icon}   {text}",
            command=command,
            bg=bg, fg=fg,
            activebackground=hover, activeforeground=T.TEXT_HEADING,
            relief=tk.FLAT, bd=0,
            font=self.f_button,
            anchor="w", justify="left",
            padx=T.PAD_MD, pady=10,
            cursor="hand2",
        )
        btn.pack(fill=tk.BOTH, expand=True)

        def on_enter(e):
            if btn["state"] != tk.DISABLED:
                btn.configure(bg=hover)

        def on_leave(e):
            if btn["state"] != tk.DISABLED:
                btn.configure(bg=bg)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        # Хак: возвращаем сам btn, а wrapper держим для pack
        btn._wrapper = wrapper
        return btn

    # ────────────────────────────────────────────
    # ПРАВАЯ ЧАСТЬ
    # ────────────────────────────────────────────
    def _build_right(self, parent: tk.Frame) -> None:
        right = tk.Frame(parent, bg=T.BG_ROOT)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Верх: чат
        self._build_chat(right)

        # Разделитель
        tk.Frame(right, bg=T.BORDER, height=1).pack(fill=tk.X)

        # Низ: лог
        self._build_log(right)

    def _build_chat(self, parent: tk.Frame) -> None:
        chat = tk.Frame(parent, bg=T.BG_ROOT)
        chat.pack(fill=tk.BOTH, expand=True)

        # ─── Заголовок ───────────────────
        header = tk.Frame(chat, bg=T.BG_ROOT)
        header.pack(fill=tk.X, padx=T.PAD_XL, pady=(T.PAD_LG, T.PAD_MD))

        title_row = tk.Frame(header, bg=T.BG_ROOT)
        title_row.pack(fill=tk.X)

        tk.Label(
            title_row, text="Чат",
            bg=T.BG_ROOT, fg=T.TEXT_HEADING, font=("Segoe UI", 14, "bold"),
        ).pack(side=tk.LEFT)

        tk.Label(
            title_row, text="  · текстовый режим без голоса",
            bg=T.BG_ROOT, fg=T.TEXT_DIM, font=self.f_small,
        ).pack(side=tk.LEFT)

        # ─── Область сообщений ───────────
        msg_outer = tk.Frame(chat, bg=T.BG_ROOT)
        msg_outer.pack(fill=tk.BOTH, expand=True, padx=T.PAD_XL, pady=(0, T.PAD_MD))

        self.chat_canvas = tk.Canvas(
            msg_outer,
            bg=T.BG_PANEL,
            highlightthickness=0,
            bd=0,
        )
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        chat_scroll = ttk.Scrollbar(
            msg_outer, orient="vertical",
            command=self.chat_canvas.yview,
        )
        chat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.configure(yscrollcommand=chat_scroll.set)

        # Внутренний фрейм для сообщений
        self.msg_frame = tk.Frame(self.chat_canvas, bg=T.BG_PANEL)
        self._canvas_window = self.chat_canvas.create_window(
            (0, 0), window=self.msg_frame, anchor="nw"
        )

        self.msg_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(
                scrollregion=self.chat_canvas.bbox("all")
            ),
        )
        self.chat_canvas.bind(
            "<Configure>",
            lambda e: self.chat_canvas.itemconfig(
                self._canvas_window, width=e.width
            ),
        )

        # Scroll по колесу
        def _on_mousewheel(event):
            self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.chat_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ─── Строка ввода ────────────────
        input_outer = tk.Frame(chat, bg=T.BG_ROOT)
        input_outer.pack(fill=tk.X, padx=T.PAD_XL, pady=(0, T.PAD_LG))

        input_box = tk.Frame(input_outer, bg=T.BG_INPUT)
        input_box.pack(fill=tk.X)

        self.chat_entry = tk.Entry(
            input_box,
            bg=T.BG_INPUT, fg=T.TEXT,
            font=self.f_input,
            relief=tk.FLAT, bd=0,
            insertbackground=T.ACCENT,
            highlightthickness=0,
        )
        self.chat_entry.pack(
            side=tk.LEFT, fill=tk.X, expand=True,
            padx=(T.PAD_LG, T.PAD_MD), pady=14,
        )
        self.chat_entry.bind("<Return>", lambda e: self._on_send_chat())

        self.btn_send = tk.Button(
            input_box, text="Отправить  ↵",
            command=self._on_send_chat,
            bg=T.ACCENT_DIM, fg=T.TEXT_HEADING,
            activebackground=T.ACCENT, activeforeground=T.TEXT_HEADING,
            relief=tk.FLAT, bd=0,
            font=self.f_button,
            padx=T.PAD_LG, pady=10,
            cursor="hand2",
        )
        self.btn_send.pack(side=tk.RIGHT, padx=(0, 8), pady=6)

        def on_enter(e):
            if self.btn_send["state"] != tk.DISABLED:
                self.btn_send.configure(bg=T.ACCENT)
        def on_leave(e):
            if self.btn_send["state"] != tk.DISABLED:
                self.btn_send.configure(bg=T.ACCENT_DIM)
        self.btn_send.bind("<Enter>", on_enter)
        self.btn_send.bind("<Leave>", on_leave)

    def _build_log(self, parent: tk.Frame) -> None:
        log_frame = tk.Frame(parent, bg=T.BG_ROOT)
        log_frame.pack(fill=tk.BOTH, expand=True)

        # ─── Заголовок ───────────────────
        header = tk.Frame(log_frame, bg=T.BG_ROOT)
        header.pack(fill=tk.X, padx=T.PAD_XL, pady=(T.PAD_MD, T.PAD_MD))

        tk.Label(
            header, text="Лог событий",
            bg=T.BG_ROOT, fg=T.TEXT_HEADING, font=("Segoe UI", 12, "bold"),
        ).pack(side=tk.LEFT)

        tk.Label(
            header, text="  · системные события и распознавание",
            bg=T.BG_ROOT, fg=T.TEXT_DIM, font=self.f_small,
        ).pack(side=tk.LEFT)

        btn_clear = tk.Button(
            header, text="Очистить",
            command=self._on_clear_log,
            bg=T.BG_PANEL, fg=T.TEXT_MUTED,
            activebackground=T.BG_HOVER, activeforeground=T.TEXT,
            relief=tk.FLAT, bd=0,
            font=self.f_small,
            padx=T.PAD_MD, pady=4,
            cursor="hand2",
        )
        btn_clear.pack(side=tk.RIGHT)

        # ─── Лог ─────────────────────────
        log_outer = tk.Frame(log_frame, bg=T.BG_ROOT)
        log_outer.pack(fill=tk.BOTH, expand=True, padx=T.PAD_XL, pady=(0, T.PAD_LG))

        self.log_text = tk.Text(
            log_outer,
            bg=T.BG_PANEL, fg=T.TEXT_MUTED,
            font=self.f_log,
            wrap=tk.WORD,
            relief=tk.FLAT, bd=0,
            padx=T.PAD_MD, pady=T.PAD_MD,
            state=tk.DISABLED,
            highlightthickness=0,
            spacing1=1, spacing3=2,
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_scroll = ttk.Scrollbar(
            log_outer, orient="vertical",
            command=self.log_text.yview,
        )
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        # Теги
        self.log_text.tag_configure("INFO",    foreground=T.TEXT_MUTED)
        self.log_text.tag_configure("WARNING", foreground=T.WARNING)
        self.log_text.tag_configure("ERROR",   foreground=T.DANGER)
        self.log_text.tag_configure("DEBUG",   foreground=T.TEXT_DIM)
        self.log_text.tag_configure("time",    foreground=T.TEXT_DIM)

    # ═══════════════════════════════════════════
    # ЧАТ — пузыри сообщений
    # ═══════════════════════════════════════════
    def _append_user_bubble(self, text: str) -> None:
        row = tk.Frame(self.msg_frame, bg=T.BG_PANEL)
        row.pack(fill=tk.X, padx=T.PAD_LG, pady=(T.PAD_MD, 2))

        # Имя
        tk.Label(
            row, text="Вы",
            bg=T.BG_PANEL, fg=T.ACCENT, font=self.f_name,
        ).pack(anchor="e")

        # Пузырь
        bubble = tk.Frame(row, bg=T.USER_BUBBLE)
        bubble.pack(anchor="e", pady=(2, 0))

        tk.Label(
            bubble, text=text,
            bg=T.USER_BUBBLE, fg=T.TEXT_HEADING,
            font=self.f_chat,
            wraplength=520, justify="left", anchor="w",
            padx=T.PAD_MD, pady=T.PAD_SM,
        ).pack()

        self._scroll_chat_bottom()

    def _append_ai_bubble_start(self) -> tk.Label:
        """Начинает пузырь ИИ, возвращает Label для обновления текста."""
        row = tk.Frame(self.msg_frame, bg=T.BG_PANEL)
        row.pack(fill=tk.X, padx=T.PAD_LG, pady=(T.PAD_MD, 2))

        tk.Label(
            row, text="Легион",
            bg=T.BG_PANEL, fg=T.SUCCESS, font=self.f_name,
        ).pack(anchor="w")

        bubble = tk.Frame(row, bg=T.AI_BUBBLE)
        bubble.pack(anchor="w", pady=(2, 0))

        label = tk.Label(
            bubble, text="",
            bg=T.AI_BUBBLE, fg=T.TEXT,
            font=self.f_chat,
            wraplength=520, justify="left", anchor="w",
            padx=T.PAD_MD, pady=T.PAD_SM,
        )
        label.pack()

        self._scroll_chat_bottom()
        return label

    def _scroll_chat_bottom(self) -> None:
        self.msg_frame.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

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

        self._set_status("Загрузка...", T.WARNING, "Инициализация голосового режима")
        self.btn_voice.configure(state=tk.DISABLED)

        def worker():
            try:
                self._assistant = LegionAssistant(
                    self.cfg, avatar_server=self._avatar_server,
                )
                self.root.after(0, lambda: self._set_status(
                    "Голос активен", T.SUCCESS, "Слушаю микрофон"
                ))
                self.root.after(0, lambda: self.btn_stop.configure(state=tk.NORMAL))
                self._assistant.run()
            except Exception as e:
                log.error(f"Ошибка голосового режима: {e}")
                self.root.after(0, lambda: self._set_status(
                    "Ошибка", T.DANGER, str(e)[:60]
                ))
            finally:
                self.root.after(0, self._on_voice_stopped)

        self._assistant_thread = threading.Thread(target=worker, daemon=True)
        self._assistant_thread.start()

    def _on_stop_voice(self) -> None:
        if self._assistant is not None:
            log.info("Остановка голосового режима...")
            self._assistant._stop_event.set()
            self._set_status("Остановка...", T.WARNING, "")

    def _on_voice_stopped(self) -> None:
        self._assistant = None
        self.btn_voice.configure(state=tk.NORMAL)
        self.btn_stop.configure(state=tk.DISABLED)
        self._set_status("Готов", T.SUCCESS, "Голосовой режим выключен")

    def _set_status(self, text: str, color: str, sub: str) -> None:
        self.status_label.configure(text=text)
        self.status_dot.itemconfig(self._dot_item, fill=color)
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
        self.btn_send.configure(state=tk.DISABLED, bg=T.BG_HOVER)

        self._append_user_bubble(text)

        if self._chat_engine is None:
            self._chat_engine = ChatEngine(self.cfg)

        ai_label = {"widget": None}
        ai_text = {"buffer": ""}

        def on_chunk(token: str) -> None:
            ai_text["buffer"] += token
            self.root.after(0, lambda: self._update_ai_bubble(ai_label, ai_text["buffer"]))

        def on_done(full: str) -> None:
            self.root.after(0, self._finish_chat)

        def on_error(err: str) -> None:
            self.root.after(0, lambda: self._show_chat_error(err))
            self.root.after(0, self._finish_chat)

        # Создаём пузырь ИИ
        def start_ai():
            ai_label["widget"] = self._append_ai_bubble_start()
        self.root.after(0, start_ai)

        self._chat_engine.ask(text, on_chunk=on_chunk, on_done=on_done, on_error=on_error)

    def _update_ai_bubble(self, ai_label: dict, text: str) -> None:
        if ai_label["widget"] is not None:
            ai_label["widget"].configure(text=text)
            self._scroll_chat_bottom()

    def _show_chat_error(self, err: str) -> None:
        self._append_user_bubble(f"[Ошибка: {err}]")

    def _finish_chat(self) -> None:
        self._chat_in_progress = False
        self.btn_send.configure(state=tk.NORMAL, bg=T.ACCENT_DIM)
        self.chat_entry.focus_set()
        self._scroll_chat_bottom()

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
        # Приветствие
        welcome = self._append_ai_bubble_start()
        welcome.configure(
            text=(
                "Привет! Я Легион — твой локальный AI-ассистент.\n\n"
                "• Пиши сюда — получишь текстовый ответ\n"
                "• Нажми «🎤 Запустить голос» — общайся голосом\n"
                "• «🎨 Открыть аватар» — визуальный интерфейс\n"
            )
        )
        self.chat_entry.focus_set()
        self.root.mainloop()


def cfg_model_name(cfg: LegionConfig) -> str:
    """Короткое имя модели для отображения."""
    name = cfg.ai.model_name or ""
    # Если есть '/', берём последнюю часть
    if "/" in name:
        return name.split("/")[-1]
    return name