from typing import Dict

# === Constants ==============================================================
# Supported CSS units and conversion ratios for font-size parsing.

UNIT_PX = "px"
UNIT_PT = "pt"
UNIT_EM = "em"
UNIT_REM = "rem"

PT_TO_PX = 1.333  # 1pt = 1.333px
EM_BASE_PX = 16.0  # 1em = 16px default browser base

# === Named colors ===========================================================
# Basic CSS color keywords (can be extended)
NAMED_COLORS: Dict[str, str] = {
    "white": "#ffffff",
    "black": "#000000",
    "red": "#ff0000",
    "green": "#008000",
    "blue": "#0000ff",
    "yellow": "#ffff00",
    "cyan": "#00ffff",
    "magenta": "#ff00ff",
    "gray": "#808080",
    "grey": "#808080",
    "transparent": "#00000000",
}
