# ============================================================
#  TkImage Studio — filter_bar.py  v1.5
# ============================================================
import tkinter as tk
from src.utils.constants import COLORS, FONTS, FILTER_BTN_COLORS


class FilterBar(tk.Frame):

    FILTERS = [
        ("⬜", "Gris",          "grayscale"),
        ("🌫", "Flou",          "blur"),
        ("🔍", "Netteté",       "sharpen"),
        ("🎨", "Contraste",     "contrast"),
        ("☀",  "Luminosité",    "brightness"),
        ("🌑", "Inversion",     "invert"),
        ("⚡", "Autocontraste", "autocontrast"),
        ("↩",  "Reset",         "reset"),
    ]

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_toolbar"], relief="flat", pady=4, padx=6)
        self.app = app
        self._active = None
        self._buttons = {}
        self._build()

    def _build(self):
        tk.Label(self, text="Filtres :",
                 bg=COLORS["bg_toolbar"], fg=COLORS["text_secondary"],
                 font=FONTS["small"]).pack(side="left", padx=(4, 8))

        for icon, label, cmd in self.FILTERS:
            bg, fg = FILTER_BTN_COLORS.get(cmd, (COLORS["btn_bg"], COLORS["text_primary"]))

            btn = tk.Button(
                self,
                text=f"{icon}\n{label}",
                command=lambda c=cmd: self._apply(c),
                bg=bg, fg=fg,
                activebackground=_lighten(bg),
                activeforeground=fg,
                relief="flat", borderwidth=0,
                font=FONTS["small"],
                padx=10, pady=3,
                cursor="hand2", width=7,
            )
            btn.pack(side="left", padx=3)
            self._buttons[cmd] = btn

            btn.bind("<Enter>", lambda e, b=btn, c=cmd:
                b.config(bg=_lighten(FILTER_BTN_COLORS.get(c,(COLORS["btn_bg"],""))[0]))
                if c != self._active else None)
            btn.bind("<Leave>", lambda e, b=btn, c=cmd:
                b.config(bg=FILTER_BTN_COLORS.get(c,(COLORS["btn_bg"],""))[0])
                if c != self._active else None)

        # Séparateur + indicateur actif
        tk.Frame(self, bg=COLORS["panel_border"], width=1
                 ).pack(side="left", fill="y", padx=8, pady=2)

        self.lbl_active = tk.Label(self, text="Aucun filtre actif",
                                    bg=COLORS["bg_toolbar"], fg=COLORS["text_muted"],
                                    font=FONTS["small"])
        self.lbl_active.pack(side="left")

    def _apply(self, cmd: str):
        if cmd == "reset":
            self._set_active(None)
            getattr(self.app, "reset_image", lambda: None)()
            return
        self._set_active(cmd)
        getattr(self.app, "apply_filter", lambda x: None)(cmd)

    def _set_active(self, cmd):
        if self._active and self._active in self._buttons:
            bg = FILTER_BTN_COLORS.get(self._active, (COLORS["btn_bg"], ""))[0]
            self._buttons[self._active].config(bg=bg)

        self._active = cmd
        if cmd and cmd in self._buttons:
            self._buttons[cmd].config(bg=_lighten(_lighten(
                FILTER_BTN_COLORS.get(cmd, (COLORS["btn_bg"], ""))[0])))
            lbl = next((l for _, l, c in self.FILTERS if c == cmd), cmd)
            self.lbl_active.config(text=f"✅ Actif : {lbl}", fg=COLORS["accent2"])
        else:
            self.lbl_active.config(text="Aucun filtre actif", fg=COLORS["text_muted"])


def _lighten(hex_color: str) -> str:
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        return f"#{min(255,r+45):02x}{min(255,g+45):02x}{min(255,b+45):02x}"
    except Exception:
        return hex_color
