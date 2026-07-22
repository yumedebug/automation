import customtkinter as ctk

_family = ""
initialized = False

FONT_HEADING_BIG = None
FONT_HEADING = None
FONT_TITLE_BOLD = None
FONT_BODY = None
FONT_BODY_BOLD = None
FONT_SMALL = None
FONT_TINY = None
FONT_MONO = None
FONT_BUTTON_RUN = None
FONT_BUTTON = None

JP_FALLBACKS = ["Noto Sans JP", "Yu Gothic UI", "Meiryo", "Hiragino Sans", "MS Gothic"]


def init_fonts():
    global initialized, _family
    global FONT_HEADING_BIG, FONT_HEADING, FONT_TITLE_BOLD
    global FONT_BODY, FONT_BODY_BOLD, FONT_SMALL, FONT_TINY
    global FONT_MONO, FONT_BUTTON_RUN, FONT_BUTTON

    if initialized:
        return

    import tkinter.font as tkfont
    available = set(tkfont.families())

    for c in JP_FALLBACKS:
        if c in available:
            _family = c
            break

    FONT_HEADING_BIG = ctk.CTkFont(family=_family, size=18, weight="bold")
    FONT_HEADING = ctk.CTkFont(family=_family, size=16, weight="bold")
    FONT_TITLE_BOLD = ctk.CTkFont(family=_family, size=13, weight="bold")
    FONT_BODY = ctk.CTkFont(family=_family, size=12)
    FONT_BODY_BOLD = ctk.CTkFont(family=_family, size=12, weight="bold")
    FONT_SMALL = ctk.CTkFont(family=_family, size=11)
    FONT_TINY = ctk.CTkFont(family=_family, size=10)
    FONT_MONO = ctk.CTkFont(family="Consolas", size=11)
    FONT_BUTTON_RUN = ctk.CTkFont(family=_family, size=13, weight="bold")
    FONT_BUTTON = ctk.CTkFont(family=_family, size=12)

    initialized = True
