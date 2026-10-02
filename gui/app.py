"""
Главное окно Легиона — современный минималистичный GUI v2.
Чат-пузыри с аватарками, время, цветные кнопки, живые акценты.
"""
import os
import time
import queue
import logging
import threading
import webbrowser
from datetime import datetime
from typing import Optional

import tkinter as tk
from tkinter import font as tkfont

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
        self._status_pulse_id = None

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
            "%(asctime)s  %(message)s", datefmt="%H:%M:%S"
        ))
        logging.getLogger("ЛЕГИОН").addHandler(handler)

    def _setup_fonts(self) -> None:
        F = T.FONT_FAMILY
        M = T.FONT_MONO
        self.f_logo      = tkfont.Font(family=F, size=22, weight="bold")
        self.f_subtitle  = tkfont.Font(family=F, size=10)
        self.f_section   = tkfont.Font(family=F, size=8, weight="bold")
        self.f_body      = tkfont.Font(family=F, size=10)
        self.f_body_bold = tkfont.Font(family=F, size=10, weight="bold")
        self.f_button    = tkfont.Font(family=F, size=10, weight="bold")
        self.f_small     = tkfont.Font(family=F, size=9)
        self.f_tiny      = tkfont.Font(family=F, size=8)
        self.f_name      = tkfont.Font(family=F, size=10, weight="bold")
        self.f_chat      = tkfont.Font(family=F, size=11)
        self.f_chat_meta = tkfont.Font(family=F, size=8)
        self.f_log       = tkfont.Font(family=M, size=9)
        self.f_input     = tkfont.Font(family=F, size=11)
        self.f_heading   = tkfont.Font(family=F, size=14, weight="bold")
        self.f_avatar    = tkfont.Font(family=F, size=10, weight="bold")

    # ═══════════════════════════════════════════
    # UI
    # ═══════════════════════════════════════════
    def _build_ui(self) -> None:
        main = tk.Frame(self.root, bg=T.BG_ROOT)
        main.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar(main)
        tk.Frame(main, bg=T.BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)
        self._build_right(main)

    # ──────────────────────────────────────────
    # САЙДБАР
    # ──────────────────────────────────────────
    def _build_sidebar(self, parent: tk.Frame) -> None:
        sb = tk.Frame(parent, bg=T.BG_SIDEBAR, width=T.SIDEBAR_WIDTH)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        sb.pack_propagate(False)

        # ── Логотип ──
        logo = tk.Frame(sb, bg=T.BG_SIDEBAR)
        logo.pack(fill=tk.X, padx=T.PAD_XL, pady=(T.PAD_XL, T.PAD_LG))

        # Круг-иконка (через Canvas для сглаживания)
        cv = tk.Canvas(logo, width=48, height=48,
                       bg=T.BG_SIDEBAR, highlightthickness=0)
        cv.pack(side=tk.LEFT)
        cv.create_oval(2, 2, 46, 46, fill=T.ACCENT_BG, outline=T.ACCENT, width=2)
        cv.create_text(24, 24, text="◈", fill=T.ACCENT, font=(T.FONT_FAMILY, 20, "bold"))

        tbox = tk.Frame(logo, bg=T.BG_SIDEBAR)
        tbox.pack(side=tk.LEFT, padx=(T.PAD_MD, 0))

        tk.Label(tbox, text="Легион",
                 bg=T.BG_SIDEBAR, fg=T.TEXT_HEADING,
                 font=self.f_logo).pack(anchor="w")
        tk.Label(tbox, text="AI Assistant",
                 bg=T.BG_SIDEBAR, fg=T.TEXT_DIM,
                 font=self.f_subtitle).pack(anchor="w")

        # ── УПРАВЛЕНИЕ ──
        self._section(sb, "УПРАВЛЕНИЕ")

        btn_box = tk.Frame(sb, bg=T.BG_SIDEBAR)
        btn_box.pack(fill=tk.X, padx=T.PAD_LG, pady=(0, T.PAD_MD))

        self.btn_avatar = self._mk_btn(
            btn_box, "🎨", "Открыть аватар",
            self._on_open_avatar, "default"
        )
        self.btn_voice = self._mk_btn(
            btn_box, "🎤", "Запустить голос",
            self._on_toggle_voice, "accent"
        )
        self.btn_stop = self._mk_btn(
            btn_box, "⏹", "Остановить голос",
            self._on_stop_voice, "danger"
        )
        self.btn_stop.configure(state=tk.DISABLED)

        # ── СТАТУС ──
        self._section(sb, "СТАТУС")

        status_box = tk.Frame(sb, bg=T.BG_SIDEBAR)
        status_box.pack(fill=tk.X, padx=T.PAD_LG, pady=(0, T.PAD_MD))

        status_card = tk.Frame(status_box, bg=T.BG_PANEL)
        status_card.pack(fill=tk.X)

        row = tk.Frame(status_card, bg=T.BG_PANEL)
        row.pack(fill=tk.X, padx=T.PAD_MD, pady=(T.PAD_MD, 4))

        self.status_dot = tk.Canvas(row, width=12, height=12,
                                     bg=T.BG_PANEL, highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT)
        self._dot_id = self.status_dot.create_oval(2, 2, 10, 10,
                                                     fill=T.SUCCESS, outline="")

        self.status_label = tk.Label(
            row, text="Готов",
            bg=T.BG_PANEL, fg=T.TEXT, font=self.f_body_bold,
        )
        self.status_label.pack(side=tk.LEFT, padx=(T.PAD_SM, 0))

        self.status_sub = tk.Label(
            status_card, text="Голосовой режим выключен",
            bg=T.BG_PANEL, fg=T.TEXT_MUTED, font=self.f_small,
            wraplength=230, justify="left", anchor="w",
        )
        self.status_sub.pack(fill=tk.X, padx=T.PAD_MD, pady=(0, T.PAD_MD))

        # ── МОДЕЛЬ ──
        self._section(sb, "МОДЕЛЬ")

        model_box = tk.Frame(sb, bg=T.BG_SIDEBAR)
        model_box.pack(fill=tk.X, padx=T.PAD_LG)

        model_card = tk.Frame(model_box, bg=T.BG_PANEL)
        model_card.pack(fill=tk.X)

        tk.Label(
            model_card, text=_short_model_name(self.cfg.ai.model_name),
            bg=T.BG_PANEL, fg=T.ACCENT, font=self.f_small,
            wraplength=230, justify="left", anchor="w",
            padx=T.PAD_MD, pady=T.PAD_MD,
        ).pack(fill=tk.X)

        # ── Растяжка ──
        tk.Frame(sb, bg=T.BG_SIDEBAR).pack(fill=tk.BOTH, expand=True)

        # ── Футер ──
        footer = tk.Frame(sb, bg=T.BG_SIDEBAR)
        footer.pack(fill=tk.X, padx=T.PAD_LG, pady=T.PAD_LG)

        tk.Frame(footer, bg=T.BORDER, height=1).pack(fill=tk.X, pady=(0, T.PAD_MD))

        tk.Label(
            footer, text="●  Работает локально",
            bg=T.BG_SIDEBAR, fg=T.TEXT_DIM, font=self.f_tiny,
        ).pack()

    def _section(self, parent, text: str) -> None:
        tk.Label(
            parent, text=text,
            bg=T.BG_SIDEBAR, fg=T.TEXT_DIM,
            font=self.f_section,
        ).pack(anchor="w", padx=T.PAD_LG, pady=(T.PAD_LG, T.PAD_SM))

    def _mk_btn(self, parent, icon: str, text: str, cmd, variant="default") -> tk.Button:
        colors = {
            "default": (T.BG_PANEL, T.BG_HOVER, T.TEXT),
            "accent":  (T.ACCENT_DIM, T.ACCENT, "#ffffff"),
            "danger":  (T.BG_PANEL, T.DANGER_BG, T.TEXT),
        }
        bg, hover, fg = colors[variant]

        wrapper = tk.Frame(parent, bg=T.BG_SIDEBAR)
        wrapper.pack(fill=tk.X, pady=3)

        btn = tk.Button(
            wrapper, text=f"  {icon}    {text}",
            command=cmd,
            bg=bg, fg=fg,
            activebackground=hover, activeforeground="#ffffff",
            relief=tk.FLAT, bd=0,
            font=self.f_button,
            anchor="w", justify="left",
            padx=T.PAD_MD, pady=12,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=T.BORDER,
            highlightcolor=hover,
        )
        btn.pack(fill=tk.X)

        def enter(e):
            if btn["state"] != tk.DISABLED:
                btn.configure(bg=hover)

        def leave(e):
            if btn["state"] != tk.DISABLED:
                btn.configure(bg=bg)

        btn.bind("<Enter>", enter)
        btn.bind("<Leave>", leave)
        return btn

    # ──────────────────────────────────────────
    # ПРАВАЯ ЧАСТЬ
    # ──────────────────────────────────────────
    def _build_right(self, parent: tk.Frame) -> None:
        right = tk.Frame(parent, bg=T.BG_ROOT)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_chat(right)
        tk.Frame(right, bg=T.BORDER, height=1).pack(fill=tk.X)
        self._build_log(right)

    # ──────────────────────────────────────────
    # ЧАТ
    # ──────────────────────────────────────────
    def _build_chat(self, parent: tk.Frame) -> None:
        chat = tk.Frame(parent, bg=T.BG_ROOT)
        chat.pack(fill=tk.BOTH, expand=True)

        # Header
        hdr = tk.Frame(chat, bg=T.BG_ROOT)
        hdr.pack(fill=tk.X, padx=T.PAD_XL, pady=(T.PAD_LG, T.PAD_MD))

        tk.Label(hdr, text="Чат",
                 bg=T.BG_ROOT, fg=T.TEXT_HEADING,
                 font=self.f_heading).pack(side=tk.LEFT)

        tk.Label(hdr, text="  текстовый режим",
                 bg=T.BG_ROOT, fg=T.TEXT_DIM,
                 font=self.f_small).pack(side=tk.LEFT)

        # Сообщения
        msg_outer = tk.Frame(chat, bg=T.BG_PANEL)
        msg_outer.pack(fill=tk.BOTH, expand=True, padx=T.PAD_XL, pady=(0, T.PAD_MD))

        self.chat_canvas = tk.Canvas(
            msg_outer, bg=T.BG_PANEL,
            highlightthickness=0, bd=0,
        )
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = tk.Scrollbar(msg_outer, orient="vertical",
                              command=self.chat_canvas.yview,
                              bg=T.BG_PANEL_2, troughcolor=T.BG_PANEL,
                              activebackground=T.ACCENT,
                              relief=tk.FLAT, bd=0, width=10)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.configure(yscrollcommand=scroll.set)

        self.msg_frame = tk.Frame(self.chat_canvas, bg=T.BG_PANEL)
        self._canvas_win = self.chat_canvas.create_window(
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
            lambda e: self.chat_canvas.itemconfig(self._canvas_win, width=e.width),
        )

        def wheel(event):
            self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.chat_canvas.bind_all("<MouseWheel>", wheel)

        # Ввод
        inp_outer = tk.Frame(chat, bg=T.BG_ROOT)
        inp_outer.pack(fill=tk.X, padx=T.PAD_XL, pady=(0, T.PAD_LG))

        inp_card = tk.Frame(inp_outer, bg=T.BG_INPUT,
                             highlightthickness=1,
                             highlightbackground=T.BORDER,
                             highlightcolor=T.ACCENT)
        inp_card.pack(fill=tk.X)

        self.chat_entry = tk.Entry(
            inp_card,
            bg=T.BG_INPUT, fg=T.TEXT,
            font=self.f_input,
            relief=tk.FLAT, bd=0,
            insertbackground=T.ACCENT,
            highlightthickness=0,
        )
        self.chat_entry.pack(
            side=tk.LEFT, fill=tk.X, expand=True,
            padx=(T.PAD_LG, T.PAD_MD), pady=16,
        )
        self.chat_entry.bind("<Return>", lambda e: self._on_send_chat())

        self.btn_send = tk.Button(
            inp_card, text="Отправить  ↵",
            command=self._on_send_chat,
            bg=T.ACCENT_DIM, fg="#ffffff",
            activebackground=T.ACCENT, activeforeground="#ffffff",
            relief=tk.FLAT, bd=0,
            font=self.f_button,
            padx=T.PAD_LG, pady=12,
            cursor="hand2",
        )
        self.btn_send.pack(side=tk.RIGHT, padx=(0, 6), pady=6)

    # ──────────────────────────────────────────
    # ЛОГ
    # ──────────────────────────────────────────
    def _build_log(self, parent: tk.Frame) -> None:
        log_f = tk.Frame(parent, bg=T.BG_ROOT)
        log_f.pack(fill=tk.BOTH, expand=True)

        hdr = tk.Frame(log_f, bg=T.BG_ROOT)
        hdr.pack(fill=tk.X, padx=T.PAD_XL, pady=(T.PAD_MD, T.PAD_MD))

        tk.Label(hdr, text="Лог",
                 bg=T.BG_ROOT, fg=T.TEXT_HEADING,
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)

        tk.Label(hdr, text="  системные события",
                 bg=T.BG_ROOT, fg=T.TEXT_DIM,
                 font=self.f_small).pack(side=tk.LEFT)

        tk.Button(
            hdr, text="Очистить", command=self._on_clear_log,
            bg=T.BG_PANEL, fg=T.TEXT_MUTED,
            activebackground=T.BG_HOVER, activeforeground=T.TEXT,
            relief=tk.FLAT, bd=0,
            font=self.f_tiny, padx=10, pady=3,
            cursor="hand2",
        ).pack(side=tk.RIGHT)

        log_outer = tk.Frame(log_f, bg=T.BG_PANEL)
        log_outer.pack(fill=tk.BOTH, expand=True, padx=T.PAD_XL, pady=(0, T.PAD_LG))

        self.log_text = tk.Text(
            log_outer,
            bg=T.BG_PANEL, fg=T.TEXT_MUTED,
            font=self.f_log, wrap=tk.WORD,
            relief=tk.FLAT, bd=0,
            padx=T.PAD_LG, pady=T.PAD_MD,
            state=tk.DISABLED,
            highlightthickness=0,
            spacing1=1, spacing3=3,
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ls = tk.Scrollbar(log_outer, orient="vertical",
                          command=self.log_text.yview,
                          bg=T.BG_PANEL_2, troughcolor=T.BG_PANEL,
                          activebackground=T.ACCENT,
                          relief=tk.FLAT, bd=0, width=10)
        ls.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=ls.set)

        self.log_text.tag_configure("time", foreground=T.TEXT_DIM)
        self.log_text.tag_configure("INFO", foreground=T.TEXT_MUTED)
        self.log_text.tag_configure("WARNING", foreground=T.WARNING)
        self.log_text.tag_configure("ERROR", foreground=T.DANGER)
        self.log_text.tag_configure("DEBUG", foreground="#555555")

    # ═══════════════════════════════════════════
    # ЧАТ — пузыри
    # ═══════════════════════════════════════════
    def _bubble_user(self, text: str) -> None:
        self._bubble(text, is_user=True)

    def _bubble_ai_start(self) -> tk.Label:
        return self._bubble("", is_user=False)

    def _bubble(self, text: str, is_user: bool):
        """Универсальная отрисовка пузыря с аватаркой и временем."""
        now = datetime.now().strftime("%H:%M")

        container = tk.Frame(self.msg_frame, bg=T.BG_PANEL)
        container.pack(fill=tk.X, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_SM))

        # Горизонтальный блок: аватар + контент
        row = tk.Frame(container, bg=T.BG_PANEL)
        row.pack(fill=tk.X)

        if is_user:
            row.pack_configure(anchor="e")
        else:
            row.pack_configure(anchor="w")

        # Аватарка (круг с буквой)
        av_color = T.USER_AVATAR if is_user else T.AI_AVATAR
        avatar = tk.Canvas(row, width=36, height=36,
                            bg=T.BG_PANEL, highlightthickness=0)
        avatar.create_oval(0, 0, 36, 36, fill=av_color, outline="")
        letter = "В" if is_user else "Л"
        avatar.create_text(18, 18, text=letter, fill="#ffffff",
                            font=(T.FONT_FAMILY, 13, "bold"))

        # Блок с именем, пузырём и временем
        content = tk.Frame(row, bg=T.BG_PANEL)

        # Имя + время
        meta = tk.Frame(content, bg=T.BG_PANEL)
        meta.pack(anchor="e" if is_user else "w")

        name = "Вы" if is_user else "Легион"
        name_color = T.ACCENT if is_user else T.SUCCESS

        tk.Label(meta, text=name, bg=T.BG_PANEL, fg=name_color,
                 font=self.f_name).pack(side=tk.LEFT)
        tk.Label(meta, text=f"  {now}", bg=T.BG_PANEL, fg=T.TEXT_DIM,
                 font=self.f_tiny).pack(side=tk.LEFT)

        # Пузырь
        bubble_color = T.USER_BUBBLE if is_user else T.AI_BUBBLE
        bubble = tk.Frame(content, bg=bubble_color,
                          highlightthickness=1,
                          highlightbackground=bubble_color)
        bubble.pack(anchor="e" if is_user else "w", pady=(3, 0))

        label = tk.Label(
            bubble, text=text,
            bg=bubble_color,
            fg=T.USER_TEXT if is_user else T.AI_TEXT,
            font=self.f_chat,
            wraplength=560,
            justify="left", anchor="w",
            padx=T.PAD_LG, pady=T.PAD_MD,
        )
        label.pack()

        # Размещение
        if is_user:
            content.pack(side=tk.RIGHT, padx=(0, T.PAD_MD))
            avatar.pack(side=tk.RIGHT)
        else:
            avatar.pack(side=tk.LEFT)
            content.pack(side=tk.LEFT, padx=(T.PAD_MD, 0))

        self._scroll_chat_bottom()
        return label

    def _scroll_chat_bottom(self) -> None:
        self.msg_frame.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    # ═══════════════════════════════════════════
    # Логи
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
            assets = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "assets",
            )
            self._avatar_server = AvatarServer(
                assets,
                host=self.cfg.avatar.host,
                port=self.cfg.avatar.port,
            )
            self._avatar_server.start()
            log.info(f"Avatar: {self._avatar_server.url}")
        except Exception as e:
            log.error(f"Avatar error: {e}")
            self._avatar_server = None

    def _on_open_avatar(self) -> None:
        if self._avatar_server is None:
            log.error("Avatar не запущен")
            return
        try:
            webbrowser.open(self._avatar_server.url)
            log.info(f"Открываю аватар")
        except Exception as e:
            log.error(f"Не открыть: {e}")

    # ═══════════════════════════════════════════
    # Голос
    # ═══════════════════════════════════════════
    def _on_toggle_voice(self) -> None:
        if self._assistant_thread and self._assistant_thread.is_alive():
            self._on_stop_voice()
            return
        self._start_voice()

    def _start_voice(self) -> None:
        if self._assistant_thread and self._assistant_thread.is_alive():
            return

        self._set_status("Загрузка...", T.WARNING, "Инициализация...")
        self.btn_voice.configure(state=tk.DISABLED)
        self._start_pulse()

        def worker():
            try:
                self._assistant = LegionAssistant(
                    self.cfg, avatar_server=self._avatar_server,
                )
                self.root.after(0, self._stop_pulse)
                self.root.after(0, lambda: self._set_status(
                    "Голос активен", T.SUCCESS, "Слушаю микрофон"
                ))
                self.root.after(0, lambda: self.btn_stop.configure(state=tk.NORMAL))
                self._assistant.run()
            except Exception as e:
                log.error(f"Voice error: {e}")
                self.root.after(0, self._stop_pulse)
                self.root.after(0, lambda: self._set_status(
                    "Ошибка", T.DANGER, str(e)[:60]
                ))
            finally:
                self.root.after(0, self._on_voice_stopped)

        self._assistant_thread = threading.Thread(target=worker, daemon=True)
        self._assistant_thread.start()

    def _on_stop_voice(self) -> None:
        if self._assistant is not None:
            log.info("Остановка голоса...")
            self._assistant._stop_event.set()
            self._set_status("Остановка...", T.WARNING, "")

    def _on_voice_stopped(self) -> None:
        self._assistant = None
        self._stop_pulse()
        self.btn_voice.configure(state=tk.NORMAL)
        self.btn_stop.configure(state=tk.DISABLED)
        self._set_status("Готов", T.SUCCESS, "Голосовой режим выключен")

    def _start_pulse(self) -> None:
        self._pulse_on = True

        def pulse():
            if not self._pulse_on:
                return
            cur = self.status_dot.itemcget(self._dot_id, "fill")
            new = T.WARNING if cur != T.WARNING else T.WARNING_BG
            self.status_dot.itemconfig(self._dot_id, fill=new)
            self.root.after(600, pulse)

        pulse()

    def _stop_pulse(self) -> None:
        self._pulse_on = False
        self.status_dot.itemconfig(self._dot_id, fill=T.SUCCESS)

    def _set_status(self, text: str, color: str, sub: str) -> None:
        self.status_label.configure(text=text)
        if not self._pulse_on:
            self.status_dot.itemconfig(self._dot_id, fill=color)
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

        self._bubble_user(text)

        if self._chat_engine is None:
            self._chat_engine = ChatEngine(self.cfg)

        ai_label = {"widget": None}
        ai_buf = {"text": ""}
        first_chunk = {"seen": False}

        def on_chunk(token: str) -> None:
            ai_buf["text"] += token
            if not first_chunk["seen"]:
                first_chunk["seen"] = True
                self.root.after(0, lambda: ai_label.update(
                    {"widget": self._bubble_ai_start()}
                ))
            self.root.after(0, lambda: self._update_ai(
                ai_label, ai_buf["text"]
            ))

        def on_done(full: str) -> None:
            if not first_chunk["seen"] and full.strip():
                self.root.after(0, lambda: self._bubble_ai_full(full))
            self.root.after(0, self._finish_chat)

        def on_error(err: str) -> None:
            self.root.after(0, lambda: self._bubble_user(f"[Ошибка] {err}"))
            self.root.after(0, self._finish_chat)

        self._chat_engine.ask(text, on_chunk=on_chunk, on_done=on_done, on_error=on_error)

    def _update_ai(self, ai_label: dict, text: str) -> None:
        if ai_label["widget"] is not None:
            ai_label["widget"].configure(text=text)
            self._scroll_chat_bottom()

    def _bubble_ai_full(self, text: str) -> None:
        lbl = self._bubble_ai_start()
        lbl.configure(text=text)

    def _finish_chat(self) -> None:
        self._chat_in_progress = False
        self.btn_send.configure(state=tk.NORMAL, bg=T.ACCENT_DIM)
        self.chat_entry.focus_set()
        self._scroll_chat_bottom()

    # ═══════════════════════════════════════════
    # Завершение
    # ═══════════════════════════════════════════
    def _on_close(self) -> None:
        log.info("Закрытие...")
        if self._assistant:
            self._assistant._stop_event.set()
            time.sleep(0.3)
        if self._avatar_server:
            try:
                self._avatar_server.stop()
            except Exception:
                pass
        self.root.destroy()

    def run(self) -> None:
        # Приветствие
        lbl = self._bubble_ai_start()
        lbl.configure(text=(
            "Привет! Я Легион — локальный AI-ассистент.\n\n"
            "Пиши мне сообщения прямо здесь — я отвечу текстом. "
            "Для голосового режима нажми «🎤 Запустить голос» слева."
        ))
        self.chat_entry.focus_set()
        self.root.mainloop()


def _short_model_name(name: str) -> str:
    if not name:
        return "не задана"
    if "/" in name:
        return name.split("/")[-1]
    return name