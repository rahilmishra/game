"""Smart Quiz Challenge application.

QuizApp is the main class. It switches between four screens:
welcome, category selection, the quiz itself, and the final result.
Tkinter events (button clicks, key presses, and after() timers)
drive the program. No code runs the quiz in a loop of its own.
"""

import tkinter as tk
from tkinter import messagebox

from questions import CATEGORY_DETAILS, CATEGORY_ORDER, prepare_quiz
from styles import COLORS, FONTS

# Each question gives the player 20 seconds.
TIMER_SECONDS = 20
# After a timeout, show the correct answer briefly, then move on.
TIMEOUT_PAUSE_MS = 1800


def enable_windows_dpi():
    """Make text sharper on Windows displays. Safe to skip if it fails."""
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            from ctypes import windll

            windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def calculate_percentage(correct, total):
    """Percentage = (correct answers / total questions) x 100.

    The value is rounded to the nearest whole number so the result screen
    and the performance message always use the same figure.
    """
    if total <= 0:
        return 0
    # Adding 0.5 before int() rounds to the nearest whole percent.
    return int((correct / total) * 100 + 0.5)


def performance_message(percentage):
    """Pick the result message from the player's percentage."""
    if percentage >= 90:
        return "Excellent!"
    if percentage >= 75:
        return "Very Good!"
    if percentage >= 50:
        return "Good Job!"
    return "Keep Practicing!"


def message_color(message):
    """Color used for the performance message on the result screen."""
    colors = {
        "Excellent!": COLORS["excellent"],
        "Very Good!": COLORS["very_good"],
        "Good Job!": COLORS["good"],
        "Keep Practicing!": COLORS["practice"],
    }
    return colors.get(message, COLORS["text"])


class ProgressBar(tk.Canvas):
    """A flat bar that shows how much of the quiz is finished."""

    def __init__(self, parent, height=12):
        super().__init__(
            parent,
            height=height,
            bg=COLORS["progress_track"],
            highlightthickness=0,
            bd=0,
        )
        self.percent = 0
        self.bar_color = COLORS["accent"]
        self.bind("<Configure>", self._redraw)

    def set_percent(self, percent):
        """Store a value from 0 to 100 and draw it."""
        self.percent = max(0, min(100, percent))
        self._redraw()

    def _redraw(self, _event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 2 or height < 2:
            return
        self.delete("all")
        self.create_rectangle(0, 0, width, height, fill=COLORS["progress_track"], outline="")
        fill_width = int(width * (self.percent / 100))
        if fill_width > 0:
            self.create_rectangle(0, 0, fill_width, height, fill=self.bar_color, outline="")


class QuizApp(tk.Tk):
    """Desktop window that owns the player's name, category, score, and timer."""

    def __init__(self):
        enable_windows_dpi()
        super().__init__()

        self.title("Smart Quiz Challenge")
        self.configure(bg=COLORS["bg"])
        self.minsize(900, 740)
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.confirm_exit)

        # Game values. They are reset when a new quiz starts.
        self.player_name = ""
        self.category = ""
        self.selected_category = ""
        self.quiz_questions = []
        self.question_index = 0
        self.score = 0
        self.answer_log = []
        self.current_question = None
        self.answered = False
        self.option_rows = []
        self.result_summary = {}

        # after() ids. Cancelling these stops old timers from firing.
        self.timer_job = None
        self.advance_job = None
        self.time_left = TIMER_SECONDS
        self.displayed_time = TIMER_SECONDS
        self.sound_enabled = True
        self.screen_name = ""
        self._welcome_size = None

        accent_line = tk.Frame(self, bg=COLORS["accent"], height=4)
        accent_line.pack(side="top", fill="x")

        self.container = tk.Frame(self, bg=COLORS["bg"])
        self.container.pack(fill="both", expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.bind("<Configure>", self._fit_screen)
        self.center_window(1040, 760)
        self.show_welcome()

    def center_window(self, width, height):
        """Open the window in the middle of the screen."""
        self.update_idletasks()
        x = max(0, (self.winfo_screenwidth() - width) // 2)
        y = max(0, (self.winfo_screenheight() - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _alive(self):
        try:
            return bool(self.winfo_exists())
        except tk.TclError:
            return False

    def cancel_timer(self):
        """Stop only the countdown, not a pending move to the next question."""
        if self.timer_job is not None:
            try:
                self.after_cancel(self.timer_job)
            except tk.TclError:
                pass
            self.timer_job = None

    def cancel_jobs(self):
        """Cancel every scheduled callback before changing screens."""
        self.cancel_timer()
        if self.advance_job is not None:
            try:
                self.after_cancel(self.advance_job)
            except tk.TclError:
                pass
            self.advance_job = None

    def destroy(self):
        """Cancel timers first so a callback cannot touch a closed window."""
        try:
            self.cancel_jobs()
        except Exception:
            pass
        super().destroy()

    def clear_screen(self):
        """Remove the current screen's widgets."""
        self.cancel_jobs()
        for child in self.container.winfo_children():
            child.destroy()
        self.option_rows = []

    def _fit_screen(self, event=None):
        """Keep text inside the window when the user resizes it."""
        if event is not None and event.widget is not self:
            return
        try:
            if self.screen_name == "welcome":
                self._fit_welcome_card()
            elif self.screen_name == "quiz":
                self._fit_quiz_text()
            elif self.screen_name == "result":
                self._fit_result_text()
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    # Small widget helpers
    # ------------------------------------------------------------------

    def make_button(self, parent, text, command, primary=True):
        """Create a flat button and return it. primary=False is the quiet style."""
        if primary:
            normal = COLORS["accent"]
            hover = COLORS["accent_hover"]
            text_color = COLORS["white"]
        else:
            normal = COLORS["card_alt"]
            hover = COLORS["card_hover"]
            text_color = COLORS["text"]

        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=normal,
            fg=text_color,
            activebackground=hover,
            activeforeground=text_color,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            font=FONTS["button"],
            padx=18,
            pady=10,
        )
        button.normal_bg = normal
        button.hover_bg = hover

        def on_enter(_event, btn=button):
            btn.configure(bg=btn.hover_bg)

        def on_leave(_event, btn=button):
            btn.configure(bg=btn.normal_bg)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        return button

    def pointer_inside(self, widget):
        """True when the mouse is still over a card, even if it is over a child label."""
        try:
            x, y = self.winfo_pointerxy()
            target = self.winfo_containing(x, y)
        except tk.TclError:
            return False
        while target is not None:
            if target == widget:
                return True
            target = target.master
        return False

    def play_sound(self, kind):
        """Play a short Windows system sound. The quiz continues if audio fails."""
        if not self.sound_enabled:
            return
        try:
            import winsound

            sounds = {
                "correct": winsound.MB_OK,
                "wrong": winsound.MB_ICONHAND,
                "timeout": winsound.MB_ICONEXCLAMATION,
            }
            winsound.MessageBeep(sounds.get(kind, winsound.MB_OK))
        except Exception:
            # A missing sound device should never stop the quiz.
            self.sound_enabled = False

    # ------------------------------------------------------------------
    # Welcome screen
    # ------------------------------------------------------------------

    def show_welcome(self):
        """Centered card: banner, title, name box, and Start Quiz button."""
        self.clear_screen()
        self.screen_name = "welcome"
        self.selected_category = ""
        self.title("Smart Quiz Challenge")

        screen = tk.Frame(self.container, bg=COLORS["bg"])
        screen.grid(row=0, column=0, sticky="nsew")
        # Side and top columns grow so the card stays in the middle.
        screen.rowconfigure(0, weight=1)
        screen.rowconfigure(2, weight=1)
        screen.columnconfigure(0, weight=1)
        screen.columnconfigure(2, weight=1)

        self.welcome_card = tk.Frame(
            screen,
            bg=COLORS["card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            width=760,
            height=640,
        )
        self.welcome_card.grid(row=1, column=1)
        self.welcome_card.grid_propagate(False)
        self.welcome_card.columnconfigure(0, weight=1)
        self.welcome_card.rowconfigure(1, weight=1)
        self._welcome_size = None

        banner = tk.Frame(self.welcome_card, bg=COLORS["banner_start"], height=118)
        banner.grid(row=0, column=0, sticky="ew")
        banner.grid_propagate(False)
        self.welcome_banner = tk.Canvas(
            banner,
            height=118,
            bg=COLORS["banner_start"],
            highlightthickness=0,
            bd=0,
        )
        self.welcome_banner.place(x=0, y=0, relwidth=1, relheight=1)
        self.welcome_banner.bind("<Configure>", self._paint_welcome_banner)

        body = tk.Frame(self.welcome_card, bg=COLORS["card"])
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.columnconfigure(2, weight=1)
        body.rowconfigure(0, weight=1)
        body.rowconfigure(2, weight=1)

        # The form stays a comfortable width. Extra card space is empty margin.
        self.welcome_form = tk.Frame(body, bg=COLORS["card"])
        self.welcome_form.grid(row=1, column=1, sticky="n", pady=8)
        self.welcome_form.columnconfigure(0, weight=1, minsize=460)

        header = tk.Frame(self.welcome_form, bg=COLORS["card"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(0, weight=1)

        logo = tk.Canvas(header, width=52, height=52, bg=COLORS["card"], highlightthickness=0)
        logo.create_oval(2, 2, 50, 50, fill=COLORS["accent"], outline="")
        logo.create_text(26, 26, text="Q", fill=COLORS["white"], font=("Segoe UI", 18, "bold"))
        logo.grid(row=0, column=0, pady=(0, 8))

        self.welcome_title = tk.Label(
            header,
            text="SMART QUIZ CHALLENGE",
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=FONTS["title"],
            justify="center",
        )
        self.welcome_title.grid(row=1, column=0)

        accent_line = tk.Frame(header, bg=COLORS["accent"], height=3, width=72)
        accent_line.grid(row=2, column=0, pady=(8, 6))

        self.welcome_subtitle = tk.Label(
            header,
            text="Test Your Knowledge, Challenge Yourself!",
            bg=COLORS["card"],
            fg=COLORS["accent_soft"],
            font=FONTS["subtitle"],
            justify="center",
        )
        self.welcome_subtitle.grid(row=3, column=0)

        stats = tk.Frame(self.welcome_form, bg=COLORS["card"])
        stats.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        for column, (value, caption) in enumerate(
            (("4", "Categories"), ("10", "Questions"), ("20s", "Each question"))
        ):
            stats.columnconfigure(column, weight=1)
            tile = tk.Frame(
                stats,
                bg=COLORS["card_alt"],
                highlightbackground=COLORS["border"],
                highlightthickness=1,
            )
            tile.grid(row=0, column=column, sticky="ew", padx=5)
            tk.Label(
                tile,
                text=value,
                bg=COLORS["card_alt"],
                fg=COLORS["accent_soft"],
                font=FONTS["stat"],
            ).pack(pady=(8, 0))
            tk.Label(
                tile,
                text=caption,
                bg=COLORS["card_alt"],
                fg=COLORS["muted"],
                font=FONTS["small"],
            ).pack(pady=(0, 8))

        name_label = tk.Label(
            self.welcome_form,
            text="PLAYER NAME",
            bg=COLORS["card"],
            fg=COLORS["muted"],
            font=FONTS["chip"],
            anchor="w",
        )
        name_label.grid(row=2, column=0, sticky="w")

        self.name_var = tk.StringVar(value=self.player_name)
        self.name_entry = tk.Entry(
            self.welcome_form,
            textvariable=self.name_var,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            font=FONTS["input"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
        )
        self.name_entry.grid(row=3, column=0, sticky="ew", pady=(8, 0), ipady=8)
        self.name_entry.bind("<Return>", lambda _event: self.on_start_welcome())

        self.name_error = tk.Label(
            self.welcome_form,
            text="",
            bg=COLORS["card"],
            fg=COLORS["wrong"],
            font=FONTS["small"],
            anchor="w",
            height=1,
        )
        self.name_error.grid(row=4, column=0, sticky="ew", pady=(4, 6))

        start = self.make_button(self.welcome_form, "Start Quiz", self.on_start_welcome, primary=True)
        start.grid(row=5, column=0, sticky="ew", ipady=4)

        hint = tk.Label(
            self.welcome_form,
            text="Press Enter to continue",
            bg=COLORS["card"],
            fg=COLORS["muted"],
            font=FONTS["small"],
        )
        hint.grid(row=6, column=0, pady=(10, 0))

        self.name_entry.focus_set()
        self.update_idletasks()
        self._fit_welcome_card()

    def _mix_color(self, start, end, amount):
        """Blend two hex colors. amount is 0 at start and 1 at end."""
        amount = max(0.0, min(1.0, amount))
        first = tuple(int(start[index:index + 2], 16) for index in (1, 3, 5))
        second = tuple(int(end[index:index + 2], 16) for index in (1, 3, 5))
        mixed = tuple(int(first[channel] + (second[channel] - first[channel]) * amount) for channel in range(3))
        return "#{:02x}{:02x}{:02x}".format(*mixed)

    def _paint_welcome_banner(self, _event=None):
        """Draw the navy-to-purple banner. Labels below it stay easy to read."""
        canvas = getattr(self, "welcome_banner", None)
        if canvas is None or not canvas.winfo_exists():
            return
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 2 or height < 2:
            return
        canvas.delete("all")
        for line in range(height):
            color = self._mix_color(COLORS["banner_start"], COLORS["banner_end"], line / (height - 1))
            canvas.create_line(0, line, width, line, fill=color)
        canvas.create_oval(width - 150, -70, width + 50, 130, outline="", fill="#8B74FF")
        canvas.create_oval(-80, height - 50, 90, height + 90, outline="", fill="#3C2C88")
        canvas.create_text(
            28,
            28,
            text="COLLEGE MINI PROJECT",
            anchor="w",
            fill=COLORS["accent_soft"],
            font=FONTS["chip"],
        )

    def _fit_welcome_card(self):
        """Resize the card with the window, and keep the title on one or two lines."""
        card = getattr(self, "welcome_card", None)
        if card is None or not card.winfo_exists():
            return
        window_w = self.winfo_width()
        window_h = self.winfo_height()
        if window_w < 200 or window_h < 200:
            window_w, window_h = 1040, 760
        card_w = max(700, min(960, window_w - 72))
        card_h = max(640, min(740, window_h - 48))
        if self._welcome_size != (card_w, card_h):
            self._welcome_size = (card_w, card_h)
            card.configure(width=card_w, height=card_h)
        form_w = max(400, min(560, card_w - 120))
        if hasattr(self, "welcome_form") and self.welcome_form.winfo_exists():
            self.welcome_form.columnconfigure(0, minsize=form_w)
        if hasattr(self, "welcome_title") and self.welcome_title.winfo_exists():
            self.welcome_title.configure(wraplength=max(280, form_w - 24))
        if hasattr(self, "welcome_subtitle") and self.welcome_subtitle.winfo_exists():
            self.welcome_subtitle.configure(wraplength=max(280, form_w - 24))

    def on_start_welcome(self):
        """Save the name only when it is not blank, then open categories."""
        name = self.name_var.get().strip()
        if not name:
            # Conditional check: an empty or all-space name is rejected.
            self.name_error.configure(text="Please enter your name.")
            self.name_entry.focus_set()
            return
        self.player_name = name
        self.name_error.configure(text="")
        self.show_categories()

    # ------------------------------------------------------------------
    # Category screen
    # ------------------------------------------------------------------

    def show_categories(self):
        """Four clickable cards. The chosen card is stored for the quiz."""
        self.clear_screen()
        self.screen_name = "category"
        self.title("Smart Quiz Challenge — Choose a Category")
        self.category_cards = {}

        screen = tk.Frame(self.container, bg=COLORS["bg"])
        screen.grid(row=0, column=0, sticky="nsew")
        screen.rowconfigure(2, weight=1)
        screen.columnconfigure(0, weight=1)

        nav = tk.Frame(screen, bg=COLORS["bg"])
        nav.grid(row=0, column=0, sticky="ew", padx=32, pady=(22, 0))
        nav.columnconfigure(1, weight=1)

        back = self.make_button(nav, "Back", self.show_welcome, primary=False)
        back.grid(row=0, column=0, sticky="w")

        heading = tk.Label(
            nav,
            text="Choose a Category",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=FONTS["section"],
        )
        heading.grid(row=0, column=1)

        self.greeting = tk.Label(
            screen,
            text=f"Hello, {self.player_name}",
            bg=COLORS["bg"],
            fg=COLORS["accent_soft"],
            font=FONTS["body"],
        )
        self.greeting.grid(row=1, column=0, pady=(12, 0))

        board = tk.Frame(screen, bg=COLORS["bg"])
        board.grid(row=2, column=0, sticky="nsew", padx=32, pady=16)
        board.columnconfigure(0, weight=1)
        board.columnconfigure(1, weight=1)
        board.rowconfigure(0, weight=1)
        board.rowconfigure(1, weight=1)

        for index, name in enumerate(CATEGORY_ORDER):
            details = CATEGORY_DETAILS[name]
            row = index // 2
            column = index % 2
            self._build_category_card(board, name, details, row, column)

        footer = tk.Frame(screen, bg=COLORS["bg"])
        footer.grid(row=3, column=0, sticky="ew", padx=32, pady=(0, 24))
        footer.columnconfigure(0, weight=1)

        self.category_error = tk.Label(
            footer,
            text="",
            bg=COLORS["bg"],
            fg=COLORS["wrong"],
            font=FONTS["small"],
            anchor="w",
        )
        self.category_error.grid(row=0, column=0, sticky="w")

        self.selected_label = tk.Label(
            footer,
            text="Selected: none",
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=FONTS["body"],
            anchor="w",
        )
        self.selected_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        start = self.make_button(footer, "Start Quiz", self.on_start_quiz, primary=True)
        start.grid(row=0, column=1, rowspan=2, sticky="e", ipadx=12)

    def _build_category_card(self, parent, name, details, row, column):
        frame = tk.Frame(
            parent,
            bg=COLORS["card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            cursor="hand2",
        )
        frame.grid(row=row, column=column, sticky="nsew", padx=10, pady=10)

        badge = tk.Label(
            frame,
            text=details["tag"],
            bg=COLORS["accent"],
            fg=COLORS["white"],
            font=FONTS["body_bold"],
            width=4,
            height=2,
        )
        badge.grid(row=0, column=0, rowspan=2, padx=(18, 12), pady=18, sticky="w")

        title = tk.Label(
            frame,
            text=name,
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=FONTS["body_bold"],
            anchor="w",
        )
        title.grid(row=0, column=1, sticky="sw", pady=(18, 0), padx=(0, 16))

        blurb = tk.Label(
            frame,
            text=details["blurb"],
            bg=COLORS["card"],
            fg=COLORS["muted"],
            font=FONTS["small"],
            anchor="w",
            justify="left",
            wraplength=280,
        )
        blurb.grid(row=1, column=1, sticky="nw", pady=(2, 18), padx=(0, 16))
        frame.columnconfigure(1, weight=1)

        self.category_cards[name] = {
            "frame": frame,
            "badge": badge,
            "labels": [title, blurb],
        }
        self._bind_category(frame, name)
        self._paint_category(name, hover=False)

    def _bind_category(self, widget, name):
        """Make the whole card clickable, including its labels."""
        try:
            widget.configure(cursor="hand2")
        except tk.TclError:
            pass
        widget.bind("<Button-1>", lambda _event, category=name: self.select_category(category))
        widget.bind("<Enter>", lambda _event, category=name: self._hover_category(category, True))
        widget.bind("<Leave>", lambda _event, category=name: self._hover_category(category, False))
        for child in widget.winfo_children():
            self._bind_category(child, name)

    def _hover_category(self, name, entering):
        card = self.category_cards.get(name)
        if card is None:
            return
        if not entering and self.pointer_inside(card["frame"]):
            return
        self._paint_category(name, hover=entering)

    def _paint_category(self, name, hover):
        info = self.category_cards[name]
        selected = name == self.selected_category
        if selected:
            background = COLORS["selected"]
            border = COLORS["accent"]
            thickness = 2
        elif hover:
            background = COLORS["card_hover"]
            border = COLORS["accent"]
            thickness = 1
        else:
            background = COLORS["card"]
            border = COLORS["border"]
            thickness = 1
        info["frame"].configure(
            bg=background,
            highlightbackground=border,
            highlightthickness=thickness,
        )
        for label in info["labels"]:
            label.configure(bg=background)

    def select_category(self, name):
        """Remember the category and highlight its card."""
        self.selected_category = name
        self.category_error.configure(text="")
        self.selected_label.configure(text=f"Selected: {name}", fg=COLORS["accent_soft"])
        for category_name in self.category_cards:
            self._paint_category(category_name, hover=False)

    def on_start_quiz(self):
        """Shuffle the chosen category and open the first question."""
        if not self.selected_category:
            self.category_error.configure(text="Please choose a category.")
            return

        self.category = self.selected_category
        # A new list is shuffled for every game. The bank itself is not changed.
        self.quiz_questions = prepare_quiz(self.category)
        self.question_index = 0
        self.score = 0
        self.answer_log = []
        self.answered = False
        self.show_question()

    # ------------------------------------------------------------------
    # Quiz screen
    # ------------------------------------------------------------------

    def show_question(self):
        """Show one question, four options, the score, and a fresh 20 second timer."""
        self.clear_screen()
        self.screen_name = "quiz"
        self.answered = False
        self.current_question = self.quiz_questions[self.question_index]
        total = len(self.quiz_questions)
        self.title(f"Smart Quiz Challenge — {self.category}")

        screen = tk.Frame(self.container, bg=COLORS["bg"])
        screen.grid(row=0, column=0, sticky="nsew")
        screen.columnconfigure(0, weight=1)
        screen.rowconfigure(5, weight=1)

        top = tk.Frame(screen, bg=COLORS["bg"])
        top.grid(row=0, column=0, sticky="ew", padx=32, pady=(18, 6))
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)
        top.columnconfigure(2, weight=1)

        self.name_banner = tk.Label(
            top,
            text=self.player_name,
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=FONTS["body_bold"],
            anchor="w",
        )
        self.name_banner.grid(row=0, column=0, sticky="w")

        self.score_label = tk.Label(
            top,
            text=f"Score: {self.score}",
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=FONTS["small"],
            anchor="w",
        )
        self.score_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        category_label = tk.Label(
            top,
            text=self.category,
            bg=COLORS["bg"],
            fg=COLORS["accent_soft"],
            font=FONTS["body_bold"],
        )
        category_label.grid(row=0, column=1)

        self.question_counter = tk.Label(
            top,
            text=f"Question {self.question_index + 1} of {total}",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=FONTS["body"],
        )
        self.question_counter.grid(row=1, column=1, pady=(2, 0))

        exit_button = self.make_button(top, "Exit", self.confirm_exit, primary=False)
        exit_button.grid(row=0, column=2, sticky="e")

        timer_box = tk.Frame(top, bg=COLORS["bg"])
        timer_box.grid(row=1, column=2, sticky="e", pady=(4, 0))
        tk.Label(
            timer_box,
            text="TIME  ",
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=FONTS["small"],
        ).pack(side="left")
        self.timer_label = tk.Label(
            timer_box,
            text=self._clock_text(TIMER_SECONDS),
            bg=COLORS["bg"],
            fg=COLORS["accent_soft"],
            font=FONTS["timer"],
        )
        self.timer_label.pack(side="left")

        progress_row = tk.Frame(screen, bg=COLORS["bg"])
        progress_row.grid(row=1, column=0, sticky="ew", padx=32, pady=(8, 0))
        progress_row.columnconfigure(0, weight=1)

        self.progress_text = tk.Label(
            progress_row,
            text="0% complete",
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=FONTS["small"],
        )
        self.progress_text.grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.progress = ProgressBar(progress_row, height=12)
        self.progress.grid(row=1, column=0, sticky="ew")

        question_card = tk.Frame(
            screen,
            bg=COLORS["card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        question_card.grid(row=2, column=0, sticky="ew", padx=32, pady=(16, 8))
        question_card.columnconfigure(0, weight=1)

        self.question_label = tk.Label(
            question_card,
            text=self.current_question["question"],
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=FONTS["question"],
            anchor="w",
            justify="left",
            wraplength=760,
        )
        self.question_label.grid(row=0, column=0, sticky="ew", padx=22, pady=20)

        options = tk.Frame(screen, bg=COLORS["bg"])
        options.grid(row=3, column=0, sticky="ew", padx=32)
        options.columnconfigure(0, weight=1)

        letters = "ABCD"
        self.option_rows = []
        for index, option_text in enumerate(self.current_question["options"]):
            self._build_option(options, index, letters[index], option_text)

        # Row 4 sits under the options. Extra window height stays below the buttons.
        footer = tk.Frame(screen, bg=COLORS["bg"])
        footer.grid(row=4, column=0, sticky="ew", padx=32, pady=(8, 12))
        spacer = tk.Frame(screen, bg=COLORS["bg"])
        spacer.grid(row=5, column=0, sticky="nsew")
        footer.columnconfigure(0, weight=1)

        self.feedback = tk.Label(
            footer,
            text="",
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=FONTS["body_bold"],
            anchor="w",
            justify="left",
            wraplength=640,
        )
        self.feedback.grid(row=0, column=0, sticky="w")

        next_text = "View Result" if self.question_index == total - 1 else "Next Question"
        self.next_button = self.make_button(footer, next_text, self.on_next, primary=True)
        self.next_button.grid(row=0, column=1, sticky="e", padx=(16, 0))
        self.next_enabled = False
        self._set_next_enabled(False)

        # Questions already finished. The bar moves forward after this one is answered.
        self.update_progress(self.question_index)
        self.update_idletasks()
        self._fit_quiz_text()
        self.start_timer()

    def _build_option(self, parent, index, letter, option_text):
        row = tk.Frame(
            parent,
            bg=COLORS["card_alt"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            cursor="hand2",
        )
        row.grid(row=index, column=0, sticky="ew", pady=5)

        badge = tk.Label(
            row,
            text=letter,
            bg=COLORS["accent"],
            fg=COLORS["white"],
            font=FONTS["body_bold"],
            width=3,
        )
        badge.pack(side="left", padx=(12, 10), pady=12)

        label = tk.Label(
            row,
            text=option_text,
            bg=COLORS["card_alt"],
            fg=COLORS["text"],
            font=FONTS["option"],
            anchor="w",
            justify="left",
            wraplength=680,
        )
        label.pack(side="left", fill="x", expand=True, padx=(0, 14), pady=12)

        record = {"frame": row, "badge": badge, "label": label, "text": option_text}
        self.option_rows.append(record)

        for widget in (row, badge, label):
            widget.bind("<Button-1>", lambda _event, choice=index: self.select_answer(choice))
            widget.bind("<Enter>", lambda _event, item=record: self._hover_option(item, True))
            widget.bind("<Leave>", lambda _event, item=record: self._hover_option(item, False))

    def _hover_option(self, item, entering):
        if self.answered:
            return
        if not entering and self.pointer_inside(item["frame"]):
            return
        if entering:
            self._style_option(item, COLORS["card_hover"], COLORS["accent"], COLORS["accent"], COLORS["white"], COLORS["text"])
        else:
            self._style_option(item, COLORS["card_alt"], COLORS["border"], COLORS["accent"], COLORS["white"], COLORS["text"])

    def _style_option(self, item, background, border, badge_bg, badge_fg, text_fg):
        item["frame"].configure(bg=background, highlightbackground=border, highlightthickness=1)
        item["badge"].configure(bg=badge_bg, fg=badge_fg)
        item["label"].configure(bg=background, fg=text_fg)

    def _fit_quiz_text(self):
        if not hasattr(self, "question_label") or not self.question_label.winfo_exists():
            return
        width = max(320, self.winfo_width() - 180)
        self.question_label.configure(wraplength=width)
        for row in self.option_rows:
            row["label"].configure(wraplength=max(220, width - 80))
        if hasattr(self, "feedback") and self.feedback.winfo_exists():
            self.feedback.configure(wraplength=max(220, self.winfo_width() - 340))

    def _set_next_enabled(self, enabled):
        """Next stays quiet until an answer, or a timeout, has been recorded."""
        self.next_enabled = enabled
        if enabled:
            self.next_button.configure(bg=COLORS["accent"], fg=COLORS["white"], cursor="hand2")
            self.next_button.normal_bg = COLORS["accent"]
            self.next_button.hover_bg = COLORS["accent_hover"]
        else:
            self.next_button.configure(bg=COLORS["card_alt"], fg=COLORS["muted"], cursor="arrow")
            self.next_button.normal_bg = COLORS["card_alt"]
            self.next_button.hover_bg = COLORS["card_alt"]

    def _clock_text(self, seconds):
        return f"00:{max(0, seconds):02d}"

    def _paint_timer(self):
        self.displayed_time = self.time_left
        if not hasattr(self, "timer_label") or not self.timer_label.winfo_exists():
            return
        self.timer_label.configure(text=self._clock_text(self.time_left))
        if self.time_left <= 5:
            color = COLORS["warning"]
        else:
            color = COLORS["accent_soft"]
        self.timer_label.configure(fg=color)

    def start_timer(self):
        """Begin a new 20 second countdown for the current question."""
        self.cancel_timer()
        self.time_left = TIMER_SECONDS
        self._tick()

    def _tick(self):
        """Update the clock once per second until it reaches zero."""
        if not self._alive() or self.screen_name != "quiz" or self.answered:
            return
        self._paint_timer()
        if self.time_left <= 0:
            self.handle_timeout()
            return
        self.time_left -= 1
        self.timer_job = self.after(1000, self._tick)

    def _resume_tick(self):
        """Continue a clock that was paused by the exit dialog."""
        if not self._alive() or self.answered or self.screen_name != "quiz":
            return
        self.time_left -= 1
        self._tick()

    def select_answer(self, index):
        """Check the chosen option once. Further clicks on this question do nothing."""
        if self.answered or self.screen_name != "quiz":
            return
        if index < 0 or index >= len(self.option_rows):
            return

        # Lock the question before awarding a mark so a second click cannot add another.
        self.answered = True
        self.cancel_timer()

        chosen = self.option_rows[index]["text"]
        correct = self.current_question["answer"]
        is_correct = chosen == correct

        if is_correct:
            self.score += 1
            self.feedback.configure(text="Correct Answer!", fg=COLORS["correct"])
            self.play_sound("correct")
        else:
            self.feedback.configure(
                text=f"Incorrect Answer!    Correct answer: {correct}",
                fg=COLORS["wrong"],
            )
            self.play_sound("wrong")

        self._record_answer(chosen, correct, is_correct)
        self._show_answer_colors(index, correct)
        self.score_label.configure(text=f"Score: {self.score}")
        self.update_progress(self.question_index + 1)
        self._set_next_enabled(True)

    def handle_timeout(self):
        """A missed question scores zero and then moves on by itself."""
        if self.answered or not self._alive() or self.screen_name != "quiz":
            return
        self.answered = True
        self.cancel_timer()
        self._paint_timer()

        correct = self.current_question["answer"]
        self.feedback.configure(
            text=f"Time's up! The correct answer is: {correct}",
            fg=COLORS["warning"],
        )
        self.play_sound("timeout")
        # No option was selected, and no mark is added.
        self._record_answer(None, correct, False)
        self._show_answer_colors(None, correct)
        self.update_progress(self.question_index + 1)
        self._set_next_enabled(True)
        self.advance_job = self.after(TIMEOUT_PAUSE_MS, self.goto_next)

    def _record_answer(self, selected, correct, is_correct):
        """Store one result per question. Wrong answers add no points."""
        self.answer_log.append(
            {
                "selected": selected,
                "answer": correct,
                "is_correct": is_correct,
            }
        )

    def _show_answer_colors(self, chosen_index, correct_text):
        """Color the correct option green. A wrong choice is marked red."""
        for index, item in enumerate(self.option_rows):
            if item["text"] == correct_text:
                self._style_option(
                    item,
                    COLORS["correct_bg"],
                    COLORS["correct"],
                    COLORS["correct"],
                    COLORS["white"],
                    COLORS["text"],
                )
            elif index == chosen_index:
                self._style_option(
                    item,
                    COLORS["wrong_bg"],
                    COLORS["wrong"],
                    COLORS["wrong"],
                    COLORS["white"],
                    COLORS["text"],
                )
            else:
                self._style_option(
                    item,
                    COLORS["card_alt"],
                    COLORS["border"],
                    COLORS["card_hover"],
                    COLORS["muted"],
                    COLORS["muted"],
                )

    def update_progress(self, answered_count):
        """Move the bar after a question has been answered or skipped."""
        total = len(self.quiz_questions)
        if total <= 0:
            percent = 0
        else:
            percent = (answered_count / total) * 100
        if hasattr(self, "progress") and self.progress.winfo_exists():
            self.progress.set_percent(percent)
            self.progress_text.configure(text=f"{round(percent)}% complete")

    def on_next(self):
        if not self.next_enabled:
            return
        self.goto_next()

    def goto_next(self):
        """Open the next question, or the result screen after the last one."""
        if not self._alive():
            return
        self.cancel_jobs()
        self.question_index += 1
        if self.question_index >= len(self.quiz_questions):
            self.show_result()
        else:
            self.show_question()

    # ------------------------------------------------------------------
    # Result screen
    # ------------------------------------------------------------------

    def show_result(self):
        """Score is counted from the answer log so a question cannot be marked twice."""
        self.clear_screen()
        self.screen_name = "result"
        self.title("Smart Quiz Challenge — Result")

        total = len(self.quiz_questions)
        # Loop over the log. Each correct answer contributes 1. Wrong answers contribute 0.
        correct = sum(1 for item in self.answer_log if item["is_correct"])
        if correct > total:
            correct = total
        incorrect = total - correct
        percentage = calculate_percentage(correct, total)
        message = performance_message(percentage)
        self.score = correct

        self.result_summary = {
            "name": self.player_name,
            "category": self.category,
            "total": total,
            "correct": correct,
            "incorrect": incorrect,
            "score": correct,
            "percentage": percentage,
            "message": message,
        }

        screen = tk.Frame(self.container, bg=COLORS["bg"])
        screen.grid(row=0, column=0, sticky="nsew")
        screen.columnconfigure(0, weight=1)
        screen.columnconfigure(2, weight=1)
        screen.rowconfigure(0, weight=1)

        card = tk.Frame(
            screen,
            bg=COLORS["card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        card.grid(row=0, column=1, sticky="n", pady=36, padx=20)
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        tk.Label(
            card,
            text="QUIZ RESULT",
            bg=COLORS["card"],
            fg=COLORS["accent_soft"],
            font=FONTS["chip"],
        ).grid(row=0, column=0, columnspan=2, pady=(28, 8))

        self.result_message = tk.Label(
            card,
            text=message,
            bg=COLORS["card"],
            fg=message_color(message),
            font=FONTS["section"],
        )
        self.result_message.grid(row=1, column=0, columnspan=2)

        percent_label = tk.Label(
            card,
            text=f"{percentage}%",
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=FONTS["hero"],
        )
        percent_label.grid(row=2, column=0, columnspan=2, pady=(0, 6))

        self.result_name = tk.Label(
            card,
            text=self.player_name,
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=FONTS["body_bold"],
            wraplength=460,
            justify="center",
        )
        self.result_name.grid(row=3, column=0, columnspan=2)

        tk.Label(
            card,
            text=self.category,
            bg=COLORS["card"],
            fg=COLORS["muted"],
            font=FONTS["body"],
        ).grid(row=4, column=0, columnspan=2, pady=(2, 16))

        rows = [
            ("Player", self.player_name),
            ("Category", self.category),
            ("Total Questions", str(total)),
            ("Correct Answers", str(correct)),
            ("Incorrect Answers", str(incorrect)),
            ("Final Score", f"{correct} / {total}"),
            ("Percentage", f"{percentage}%"),
        ]
        self.stat_values = {}
        for index, (caption, value) in enumerate(rows):
            grid_row = 5 + index
            value_color = COLORS["text"]
            if caption == "Correct Answers":
                value_color = COLORS["correct"]
            elif caption == "Incorrect Answers":
                value_color = COLORS["wrong"]
            elif caption == "Percentage":
                value_color = message_color(message)

            tk.Label(
                card,
                text=caption,
                bg=COLORS["card"],
                fg=COLORS["muted"],
                font=FONTS["body"],
                anchor="w",
            ).grid(row=grid_row, column=0, sticky="w", padx=(36, 24), pady=4)

            value_label = tk.Label(
                card,
                text=value,
                bg=COLORS["card"],
                fg=value_color,
                font=FONTS["body_bold"],
                anchor="e",
                justify="right",
                wraplength=280,
            )
            value_label.grid(row=grid_row, column=1, sticky="e", padx=(12, 36), pady=4)
            self.stat_values[caption] = value_label

        actions = tk.Frame(card, bg=COLORS["card"])
        actions.grid(row=13, column=0, columnspan=2, pady=(22, 28))

        play_again = self.make_button(actions, "Play Again", self.play_again, primary=True)
        play_again.pack(side="left", padx=8, ipadx=8)

        exit_button = self.make_button(actions, "Exit", self.confirm_exit, primary=False)
        exit_button.pack(side="left", padx=8, ipadx=8)

        self.update_idletasks()
        self._fit_result_text()

    def _fit_result_text(self):
        if self.screen_name != "result":
            return
        if hasattr(self, "result_name") and self.result_name.winfo_exists():
            wrap = max(260, min(520, self.winfo_width() - 280))
            self.result_name.configure(wraplength=wrap)
        player = self.stat_values.get("Player") if hasattr(self, "stat_values") else None
        category = self.stat_values.get("Category") if hasattr(self, "stat_values") else None
        value_wrap = max(180, min(320, self.winfo_width() // 3))
        for label in (player, category):
            if label is not None and label.winfo_exists():
                label.configure(wraplength=value_wrap)

    def play_again(self):
        """Return to the welcome screen and drop the previous score."""
        self.score = 0
        self.question_index = 0
        self.answer_log = []
        self.quiz_questions = []
        self.category = ""
        self.selected_category = ""
        self.answered = False
        self.current_question = None
        self.result_summary = {}
        self.show_welcome()

    def confirm_exit(self):
        """Ask before closing. The timer pauses so the screen cannot change behind the dialog."""
        was_quiz = self.screen_name == "quiz"
        was_answered = self.answered
        shown = self.displayed_time
        advance_pending = self.advance_job is not None
        self.cancel_jobs()

        should_exit = messagebox.askyesno(
            "Exit Quiz",
            "Are you sure you want to exit Smart Quiz Challenge?",
            parent=self,
        )
        if should_exit:
            self.destroy()
            return
        if not self._alive():
            return

        # The player chose to stay. Put the clock back only if this question is still open.
        if was_quiz and self.screen_name == "quiz" and not was_answered:
            self.time_left = shown
            self._paint_timer()
            self.timer_job = self.after(1000, self._resume_tick)
        elif was_quiz and self.screen_name == "quiz" and was_answered and advance_pending:
            self.advance_job = self.after(TIMEOUT_PAUSE_MS, self.goto_next)


if __name__ == "__main__":
    QuizApp().mainloop()
