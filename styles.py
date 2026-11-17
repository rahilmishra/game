"""Colors and fonts for Smart Quiz Challenge.

The whole app reads its theme from this file so every screen stays consistent.
"""

# Dark navy surfaces with purple highlights.
COLORS = {
    "bg": "#0C1024",
    "card": "#161C38",
    "banner_start": "#1A1448",
    "banner_end": "#6E4DFF",
    "card_alt": "#1D2548",
    "card_hover": "#28315C",
    "selected": "#241C4E",
    "border": "#313B6B",
    "accent": "#7C5CFF",
    "accent_hover": "#9176FF",
    "accent_soft": "#C9B8FF",
    "text": "#F4F6FF",
    "muted": "#A9B3D6",
    "input_bg": "#0E1430",
    "correct": "#2FCB86",
    "correct_bg": "#123728",
    "wrong": "#FF5C78",
    "wrong_bg": "#3C1826",
    "warning": "#F6C453",
    "progress_track": "#2A335C",
    "white": "#FFFFFF",
    "excellent": "#3DDC97",
    "very_good": "#C9B8FF",
    "good": "#9EBEFF",
    "practice": "#F6C453",
}

# Segoe UI ships with Windows and fits a desktop app.
FONTS = {
    "title": ("Segoe UI", 28, "bold"),
    "stat": ("Segoe UI", 16, "bold"),
    "subtitle": ("Segoe UI", 13),
    "section": ("Segoe UI", 18, "bold"),
    "body": ("Segoe UI", 12),
    "body_bold": ("Segoe UI", 12, "bold"),
    "small": ("Segoe UI", 10),
    "button": ("Segoe UI", 12, "bold"),
    "question": ("Segoe UI", 16, "bold"),
    "option": ("Segoe UI", 12),
    "timer": ("Segoe UI", 22, "bold"),
    "hero": ("Segoe UI", 42, "bold"),
    "input": ("Segoe UI", 13),
    "chip": ("Segoe UI", 9, "bold"),
}
