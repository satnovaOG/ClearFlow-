import json
import os

SUBTITLE_BASE = 24
BODY_BASE = 16
SUBTITLE_WRAP_BASE = 750

FONT_SCALES = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0]

SCALE_LABELS = {
    0.75: "Pequeño",
    1.0: "Mediano",
    1.25: "Grande",
    1.5: "Muy grande",
    1.75: "Extra grande",
    2.0: "Máximo",
}

CONFIG_PATH = "config.json"


def load_preferences():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            scale = float(data.get("font_scale", 1.0))
            scale = min(FONT_SCALES, key=lambda x: abs(x - scale))
            return {"font_scale": scale}
        except (json.JSONDecodeError, ValueError, OSError):
            pass
    return {"font_scale": 1.0}


def save_preferences(prefs):
    existing = load_preferences()
    existing.update(prefs)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


def scaled_font(base_size, bold=False, scale=1.0):
    size = max(8, int(base_size * scale))
    if bold:
        return ("Arial", size, "bold")
    return ("Arial", size)


def scale_label(scale):
    return SCALE_LABELS.get(scale, "Mediano")
