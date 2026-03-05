from .breathwork import THEME as breathwork_theme
from .classy import THEME as classy_theme
from .cyberpunk import THEME as cyberpunk_theme

THEMES = {
    "breathwork": breathwork_theme,
    "cyberpunk": cyberpunk_theme,
    "classy": classy_theme,
}

DEFAULT_THEME = "breathwork"


def get_theme(theme_id: str) -> dict:
    return THEMES.get(theme_id, THEMES[DEFAULT_THEME])
