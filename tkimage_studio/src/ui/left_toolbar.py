# ============================================================
#  TkImage Studio — left_toolbar.py  v1.5
# ============================================================
import tkinter as tk
from src.utils.constants import COLORS, FONTS, BTN_COLORS


class LeftToolbar(tk.Frame):

    TOOLS = [
        # (icon, label, cmd_name)
        ("📂", "Ouvrir",      "open_image"),
        ("💾", "Sauvegarder", "save_image"),
        ("↩",  "Annuler",     "undo"),
        None,
        ("🔍", "Zoom +",      "zoom_in"),
        ("🔎", "Zoom −",      "zoom_out"),
        ("📐", "Ajuster",     "fit_to_window"),
        ("✋", "Déplacer",    "toggle_pan"),
        None,
        ("↔",  "Resize",      "resize_image"),
        ("🗜",  "Compresser",  "compress_image"),
        ("✂",  "Crop",        "crop_image"),
        ("🖱",  "Mouse Crop",  "mouse_crop"),
        ("🔄", "Rotation",    "rotate_image"),
        None,
        ("⬚",  "Sélection",   "toggle_select_region"),
        ("🎯", "Repère",      "toggle_repere"),
    ]

    TOGGLE_CMDS = {"toggle_pan", "toggle_select_region", "toggle_repere"}

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_panel"], width=130, relief="flat")
        self.app = app
        self.pack_propagate(False)
        self._states  = {}   # cmd_name → bool (actif ou non)
        self._buttons = {}   # cmd_name → tk.Button
        self._build()

    def _build(self):
        # En-tête avec dégradé simulé
        hdr = tk.Frame(self, bg=COLORS["panel_header"], pady=8)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚙  Outils",
                 bg=COLORS["panel_header"], fg=COLORS["accent"],
                 font=FONTS["subtitle"]).pack()

        scroll_frame = tk.Frame(self, bg=COLORS["bg_panel"])
        scroll_frame.pack(fill="both", expand=True, padx=6, pady=6)

        for item in self.TOOLS:
            if item is None:
                tk.Frame(scroll_frame, bg=COLORS["panel_border"], height=1
                         ).pack(fill="x", pady=5)
                continue
            icon, label, cmd_name = item
            self._make_btn(scroll_frame, icon, label, cmd_name)

    def _make_btn(self, parent, icon, label, cmd_name):
        colors = BTN_COLORS.get(cmd_name, (COLORS["btn_bg"], COLORS["text_primary"]))
        bg_normal, fg_color = colors

        is_toggle = cmd_name in self.TOGGLE_CMDS
        self._states[cmd_name] = False

        btn = tk.Button(
            parent,
            text=f"{icon}  {label}",
            command=lambda c=cmd_name: self._on_click(c),
            bg=bg_normal, fg=fg_color,
            activebackground=_lighten(bg_normal),
            activeforeground=fg_color,
            relief="flat", borderwidth=0,
            font=FONTS["btn"],
            anchor="w", padx=10, pady=6,
            cursor="hand2",
        )
        btn.pack(fill="x", pady=2)
        self._buttons[cmd_name] = btn

        # Hover
        btn.bind("<Enter>", lambda e, b=btn, c=cmd_name: b.config(
            bg=_lighten(BTN_COLORS.get(c, (COLORS["btn_bg"], ""))[0])
            if not self._states.get(c) else b.cget("bg")))
        btn.bind("<Leave>", lambda e, b=btn, c=cmd_name: b.config(
            bg=BTN_COLORS.get(c, (COLORS["btn_bg"], ""))[0]
            if not self._states.get(c) else _active_color(c)))

    def _on_click(self, cmd_name: str):
        if cmd_name in self.TOGGLE_CMDS:
            # Désactive les autres toggles
            for other in self.TOGGLE_CMDS:
                if other != cmd_name and self._states.get(other):
                    self._states[other] = False
                    btn = self._buttons.get(other)
                    if btn:
                        bg = BTN_COLORS.get(other, (COLORS["btn_bg"], ""))[0]
                        btn.config(bg=bg)

            new = not self._states.get(cmd_name, False)
            self._states[cmd_name] = new
            btn = self._buttons.get(cmd_name)
            if btn:
                btn.config(bg=_active_color(cmd_name) if new
                           else BTN_COLORS.get(cmd_name, (COLORS["btn_bg"], ""))[0])

        getattr(self.app, cmd_name, lambda: None)()

    def deactivate_all_toggles(self):
        for cmd_name in self.TOGGLE_CMDS:
            self._states[cmd_name] = False
            btn = self._buttons.get(cmd_name)
            if btn:
                try:
                    bg = BTN_COLORS.get(cmd_name, (COLORS["btn_bg"], ""))[0]
                    btn.config(bg=bg)
                except Exception:
                    pass


def _lighten(hex_color: str) -> str:
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        return f"#{min(255,r+50):02x}{min(255,g+50):02x}{min(255,b+50):02x}"
    except Exception:
        return hex_color


def _active_color(cmd_name: str) -> str:
    """Couleur quand un bouton toggle est actif (plus lumineux)."""
    colors = BTN_COLORS.get(cmd_name, (COLORS["btn_bg"], ""))
    return _lighten(_lighten(colors[0]))
