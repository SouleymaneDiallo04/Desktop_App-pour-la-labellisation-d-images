# ============================================================
#  TkImage Studio — top_toolbar.py  v1.5
# ============================================================
import tkinter as tk
from src.utils.constants import COLORS, FONTS, TOP_BTN_COLORS


class TopToolbar(tk.Frame):

    BUTTONS = [
        ("📂", "Open",    "open_image"),
        ("💾", "Save",    "save_image"),
        ("↩",  "Undo",    "undo"),
        None,
        ("✂",  "Crop",    "crop_image"),
        ("🔄", "Rotate",  "rotate_image"),
        ("🔍", "Zoom +",  "zoom_in"),
        ("🔎", "Zoom −",  "zoom_out"),
        None,
        ("🤖", "IA",      "ia_analyze"),
        ("📊", "Stats",   "show_stats"),
    ]

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_toolbar"], relief="flat", pady=5, padx=6)
        self.app = app
        self._build()

    def _build(self):
        for item in self.BUTTONS:
            if item is None:
                tk.Frame(self, bg=COLORS["panel_border"], width=1
                         ).pack(side="left", fill="y", padx=6, pady=2)
                continue
            icon, label, cmd_name = item
            colors = TOP_BTN_COLORS.get(cmd_name, ("#1E2438", "#E8ECF4"))
            bg, fg = colors
            hover_bg = _lighten(bg)

            btn = tk.Button(
                self,
                text=f"{icon}  {label}",
                command=getattr(self.app, cmd_name, lambda: None),
                bg=bg, fg=fg,
                activebackground=hover_bg,
                activeforeground=fg,
                relief="flat", borderwidth=0,
                font=FONTS["icon_btn"],
                padx=12, pady=5,
                cursor="hand2",
            )
            btn.pack(side="left", padx=3)
            btn.bind("<Enter>", lambda e, b=btn, h=hover_bg: b.config(bg=h))
            btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))

        # Version à droite
        tk.Label(self, text=f"v1.5",
                 bg=COLORS["bg_toolbar"], fg=COLORS["text_muted"],
                 font=FONTS["small"]).pack(side="right", padx=12)


def _lighten(hex_color: str) -> str:
    """Éclaircit légèrement une couleur hex."""
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        r = min(255, r + 40)
        g = min(255, g + 40)
        b = min(255, b + 40)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color
