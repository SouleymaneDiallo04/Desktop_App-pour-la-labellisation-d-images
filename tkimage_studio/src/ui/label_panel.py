# ============================================================
#  TkImage Studio — label_panel.py  v1.3
#  Panneau de labellisation complète
# ============================================================
import tkinter as tk
from tkinter import simpledialog, colorchooser
from src.utils.constants import COLORS, FONTS, LABEL_COLORS, DEFAULT_LABELS


class LabelPanel(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["label_panel_bg"], relief="flat")
        self.app = app
        self.labels: dict = {}          # {name: {color, shortcut, count}}
        self._btn_refs: dict = {}
        self._active_label = None       # label sélectionné dans la liste
        self._current_image_label = None  # label attribué à l'image courante
        self._build()
        self._load_defaults()

    # ════════════════════════════════════════════════════════
    #  CONSTRUCTION UI
    # ════════════════════════════════════════════════════════
    def _build(self):
        # ── En-tête ─────────────────────────────────────────
        hdr = tk.Frame(self, bg=COLORS["label_panel_hdr"], pady=5)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🏷  Labellisation",
                 bg=COLORS["label_panel_hdr"], fg=COLORS["accent2"],
                 font=FONTS["subtitle"]).pack(side="left", padx=10)
        self.lbl_total = tk.Label(hdr, text="0 annotées",
                                   bg=COLORS["label_panel_hdr"],
                                   fg=COLORS["text_secondary"],
                                   font=FONTS["small"])
        self.lbl_total.pack(side="right", padx=8)

        # ── Label image courante ─────────────────────────────
        cur_frame = tk.Frame(self, bg=COLORS["label_panel_bg"], pady=4)
        cur_frame.pack(fill="x", padx=8)
        tk.Label(cur_frame, text="Image actuelle :",
                 bg=COLORS["label_panel_bg"], fg=COLORS["text_secondary"],
                 font=FONTS["small"]).pack(anchor="w")

        badge_row = tk.Frame(cur_frame, bg=COLORS["label_panel_bg"])
        badge_row.pack(fill="x", pady=(2, 0))

        self.lbl_current = tk.Label(
            badge_row,
            text="— aucun label —",
            bg=COLORS["btn_bg"], fg=COLORS["text_muted"],
            font=FONTS["btn"], padx=8, pady=4,
            anchor="w", relief="flat",
        )
        self.lbl_current.pack(side="left", fill="x", expand=True)

        # 🗑 Bouton Effacer le label de l'image courante
        self.btn_clear = tk.Button(
            badge_row,
            text="🗑 Effacer",
            command=self.clear_current_label,
            bg=COLORS["danger"], fg="#fff",
            relief="flat", font=FONTS["small"],
            padx=6, pady=4, cursor="hand2",
        )
        self.btn_clear.pack(side="right", padx=(4, 0))
        self.btn_clear.bind("<Enter>", lambda e: self.btn_clear.config(bg="#c0392b"))
        self.btn_clear.bind("<Leave>", lambda e: self.btn_clear.config(bg=COLORS["danger"]))

        tk.Frame(self, bg=COLORS["panel_border"], height=1).pack(fill="x", padx=6, pady=4)

        # ── Barre de recherche ───────────────────────────────
        search_frame = tk.Frame(self, bg=COLORS["label_panel_bg"], pady=2)
        search_frame.pack(fill="x", padx=8)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self._refresh_list())

        self._search_entry = tk.Entry(
            search_frame,
            bg=COLORS["btn_bg"], fg=COLORS["text_muted"],
            insertbackground=COLORS["text_primary"],
            relief="flat", font=FONTS["small"],
        )
        self._search_entry.pack(fill="x")
        PLACEHOLDER = "🔍 Filtrer…"
        self._search_entry.insert(0, PLACEHOLDER)

        def on_focus_in(e):
            if self._search_entry.get() == PLACEHOLDER:
                self._search_entry.delete(0, "end")
                self._search_entry.config(fg=COLORS["text_primary"])
            self.search_var.set("")

        def on_focus_out(e):
            if not self._search_entry.get():
                self._search_entry.insert(0, PLACEHOLDER)
                self._search_entry.config(fg=COLORS["text_muted"])
                self.search_var.set("")

        def on_key(e):
            self._search_entry.after(10, lambda: self.search_var.set(
                "" if self._search_entry.get() == PLACEHOLDER
                else self._search_entry.get()
            ))

        self._search_entry.bind("<FocusIn>",   on_focus_in)
        self._search_entry.bind("<FocusOut>",  on_focus_out)
        self._search_entry.bind("<KeyRelease>", on_key)

        # ── Liste scrollable ─────────────────────────────────
        container = tk.Frame(self, bg=COLORS["label_panel_bg"])
        container.pack(fill="both", expand=True, padx=4, pady=4)

        self.canvas_list = tk.Canvas(container, bg=COLORS["label_panel_bg"],
                                      highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical",
                                  command=self.canvas_list.yview)
        self.canvas_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas_list.pack(side="left", fill="both", expand=True)

        self.list_frame = tk.Frame(self.canvas_list, bg=COLORS["label_panel_bg"])
        self.canvas_list.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.list_frame.bind("<Configure>",
            lambda e: self.canvas_list.configure(
                scrollregion=self.canvas_list.bbox("all")))

        # ── Boutons Ajouter / Supprimer label ────────────────
        btn_row = tk.Frame(self, bg=COLORS["label_panel_bg"], pady=4)
        btn_row.pack(fill="x", padx=8)

        tk.Button(btn_row, text="＋ Ajouter", command=self._add_label,
                  bg=COLORS["accent2"], fg="#111", relief="flat",
                  font=FONTS["btn"], padx=6, pady=3, cursor="hand2"
                  ).pack(side="left", padx=(0, 4))

        tk.Button(btn_row, text="✕ Supprimer", command=self._remove_active_label,
                  bg=COLORS["btn_bg"], fg=COLORS["text_secondary"],
                  relief="flat", font=FONTS["btn"],
                  padx=6, pady=3, cursor="hand2"
                  ).pack(side="left")

        # ── Info raccourcis ──────────────────────────────────
        tk.Label(self, text="Touches 1–9 : appliquer un label",
                 bg=COLORS["label_panel_bg"], fg=COLORS["text_muted"],
                 font=FONTS["small"], wraplength=200, justify="left"
                 ).pack(anchor="w", padx=8, pady=(0, 4))

    # ════════════════════════════════════════════════════════
    #  DEFAULTS
    # ════════════════════════════════════════════════════════
    def _load_defaults(self):
        for i, name in enumerate(DEFAULT_LABELS):
            color = LABEL_COLORS[i % len(LABEL_COLORS)]
            self._register_label(name, color, str(i + 1))
        self._refresh_list()

    def _register_label(self, name, color, shortcut=""):
        self.labels[name] = {"color": color, "shortcut": shortcut, "count": 0}

    # ════════════════════════════════════════════════════════
    #  GESTION LABELS
    # ════════════════════════════════════════════════════════
    def _add_label(self):
        name = simpledialog.askstring("Nouveau label", "Nom du label :")
        if not name or name in self.labels:
            return
        result = colorchooser.askcolor(
            title=f"Couleur pour « {name} »",
            color=LABEL_COLORS[len(self.labels) % len(LABEL_COLORS)])
        color = result[1] if result[1] else LABEL_COLORS[0]
        used = {v["shortcut"] for v in self.labels.values()}
        shortcut = next((str(i) for i in range(1, 10) if str(i) not in used), "")
        self._register_label(name, color, shortcut)
        self._refresh_list()

    def _remove_active_label(self):
        if self._active_label and self._active_label in self.labels:
            del self.labels[self._active_label]
            self._active_label = None
            self._refresh_list()

    def _change_color(self, name):
        result = colorchooser.askcolor(
            title=f"Couleur de « {name} »",
            color=self.labels[name]["color"])
        if result[1]:
            self.labels[name]["color"] = result[1]
            self._refresh_list()

    # ════════════════════════════════════════════════════════
    #  AFFICHAGE LISTE
    # ════════════════════════════════════════════════════════
    def _refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        self._btn_refs.clear()
        query = self.search_var.get().lower()

        for name, info in self.labels.items():
            if query and query not in name.lower():
                continue
            self._make_label_row(name, info)
        self._update_total()

    def _make_label_row(self, name, info):
        color    = info["color"]
        shortcut = info["shortcut"]
        count    = info["count"]
        is_active   = (name == self._active_label)
        is_assigned = (name == self._current_image_label)

        row_bg = COLORS["btn_hover"] if is_active else COLORS["btn_bg"]

        row = tk.Frame(self.list_frame, bg=row_bg, pady=3, padx=4, cursor="hand2")
        row.pack(fill="x", pady=2, padx=2)

        # Pastille couleur
        dot = tk.Label(row, text="●", fg=color, bg=row_bg,
                       font=("Segoe UI", 14), cursor="hand2")
        dot.pack(side="left", padx=(4, 2))
        dot.bind("<Button-1>", lambda e, n=name: self._change_color(n))

        # Nom
        lbl = tk.Label(row, text=name, bg=row_bg, fg=COLORS["text_primary"],
                       font=FONTS["btn"], anchor="w")
        lbl.pack(side="left", fill="x", expand=True)

        # ✔ si c'est le label de l'image courante
        if is_assigned:
            tk.Label(row, text="✔", bg=row_bg, fg=COLORS["accent2"],
                     font=FONTS["btn"]).pack(side="left", padx=2)

        # Compteur
        tk.Label(row, text=str(count), bg=row_bg, fg=COLORS["accent2"],
                 font=FONTS["small"], width=3).pack(side="right", padx=2)

        # Raccourci
        if shortcut:
            tk.Label(row, text=f"[{shortcut}]", bg=row_bg,
                     fg=COLORS["text_muted"], font=FONTS["small"]
                     ).pack(side="right", padx=2)

        # Bouton appliquer
        apply_btn = tk.Button(
            row, text="✔ Attribuer",
            command=lambda n=name: self.apply_label(n),
            bg=color,
            fg="#111" if _is_light(color) else "#fff",
            relief="flat", font=FONTS["small"],
            padx=4, pady=1, cursor="hand2",
        )
        apply_btn.pack(side="right", padx=4)
        self._btn_refs[name] = apply_btn

        # Clic ligne = sélectionner
        for widget in (row, lbl):
            widget.bind("<Button-1>", lambda e, n=name: self._select_label(n))

        # Hover
        def on_enter(e, r=row, n=name):
            bg = COLORS["btn_active"] if n == self._active_label else COLORS["btn_hover"]
            _recolor(r, bg)

        def on_leave(e, r=row, n=name):
            bg = COLORS["btn_hover"] if n == self._active_label else COLORS["btn_bg"]
            _recolor(r, bg)

        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)

    # ════════════════════════════════════════════════════════
    #  ACTIONS PUBLIQUES
    # ════════════════════════════════════════════════════════
    def apply_label(self, name: str):
        """Attribue le label à l'image courante."""
        old = self._current_image_label

        # Décrémente l'ancien label si différent
        if old and old != name and old in self.labels:
            self.labels[old]["count"] = max(0, self.labels[old]["count"] - 1)

        self._current_image_label = name
        self._active_label = name

        if name in self.labels:
            self.labels[name]["count"] += 1

        self._refresh_list()
        self._update_current_badge(name)

        if hasattr(self.app, "set_label_badge"):
            color = self.labels.get(name, {}).get("color", COLORS["accent"])
            self.app.set_label_badge(name, color)

    def clear_current_label(self):
        """Efface le label de l'image courante."""
        if self._current_image_label:
            old = self._current_image_label
            if old in self.labels:
                self.labels[old]["count"] = max(0, self.labels[old]["count"] - 1)
            self._current_image_label = None
            self._refresh_list()

        # Réinitialise le badge
        self.lbl_current.config(
            text="— aucun label —",
            bg=COLORS["btn_bg"],
            fg=COLORS["text_muted"],
        )
        if hasattr(self.app, "set_class"):
            self.app.set_class("")
        if hasattr(self.app, "clear_label_badge"):
            self.app.clear_label_badge()

    def notify_image_changed(self, current_label: str | None):
        """
        Appelé quand on navigue vers une nouvelle image.
        Met à jour l'affichage sans modifier les compteurs.
        """
        self._current_image_label = current_label
        self._refresh_list()
        if current_label:
            self._update_current_badge(current_label)
        else:
            self.lbl_current.config(
                text="— aucun label —",
                bg=COLORS["btn_bg"],
                fg=COLORS["text_muted"],
            )

    def handle_shortcut(self, key: str) -> bool:
        for name, info in self.labels.items():
            if info["shortcut"] == key:
                self.apply_label(name)
                return True
        return False

    def increment_label(self, name: str):
        """Incrémente uniquement (appelé de l'extérieur sans double-compter)."""
        pass  # le comptage est géré dans apply_label

    def get_label_color(self, name: str) -> str:
        return self.labels.get(name, {}).get("color", COLORS["accent"])

    def get_stats(self) -> dict:
        return {n: info["count"] for n, info in self.labels.items()}

    # ════════════════════════════════════════════════════════
    #  INTERNES
    # ════════════════════════════════════════════════════════
    def _select_label(self, name: str):
        self._active_label = name
        self._refresh_list()

    def _update_current_badge(self, name: str):
        color = self.labels.get(name, {}).get("color", COLORS["accent"])
        fg = "#111" if _is_light(color) else "#fff"
        self.lbl_current.config(
            text=f"  ✔  {name}",
            bg=color, fg=fg,
        )

    def _update_total(self):
        total = sum(v["count"] for v in self.labels.values())
        self.lbl_total.config(text=f"{total} annotées")


# ── Utilitaires ──────────────────────────────────────────────
def _is_light(hex_color: str) -> bool:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r * 299 + g * 587 + b * 114) / 1000 > 128


def _recolor(frame: tk.Frame, bg: str):
    try:
        frame.config(bg=bg)
    except Exception:
        pass
    for w in frame.winfo_children():
        try:
            w.config(bg=bg)
        except Exception:
            pass
