# ============================================================
#  TkImage Studio — status_panel.py  v1.5
#  Note améliorée : étoiles grandes + tooltip + couleurs
# ============================================================
import tkinter as tk
from src.utils.constants import COLORS, FONTS


class StatusPanel(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_statusbar"], relief="flat")
        self.app = app
        self._note_val = 0
        self._build()

    def _build(self):
        # ── En-tête coloré ───────────────────────────────────
        hdr = tk.Frame(self, bg=COLORS["panel_header"], pady=5)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📋  Description, informations et statistiques",
                 bg=COLORS["panel_header"], fg=COLORS["accent"],
                 font=FONTS["subtitle"]).pack(side="left", padx=12)

        body = tk.Frame(self, bg=COLORS["bg_statusbar"])
        body.pack(fill="both", expand=True, padx=8, pady=6)

        # ══ Colonne 1 : infos image ══════════════════════════
        info_outer = tk.Frame(body, bg=COLORS["bg_panel"],
                               highlightbackground=COLORS["panel_border"],
                               highlightthickness=1)
        info_outer.pack(side="left", fill="both", expand=True, padx=(0, 4))

        info_frame = tk.Frame(info_outer, bg=COLORS["bg_panel"], padx=10, pady=8)
        info_frame.pack(fill="both", expand=True)

        self.lbl_info = tk.Label(info_frame,
            text="Fichier : —     Taille : —     Mode : —     Classe : —",
            bg=COLORS["bg_panel"], fg=COLORS["text_secondary"],
            font=FONTS["mono"], anchor="w")
        self.lbl_info.pack(fill="x")

        self.lbl_path = tk.Label(info_frame, text="📁 Chemin : —",
                                  bg=COLORS["bg_panel"], fg=COLORS["text_muted"],
                                  font=FONTS["small"], anchor="w")
        self.lbl_path.pack(fill="x", pady=(2, 0))

        # Description
        desc_row = tk.Frame(info_frame, bg=COLORS["bg_panel"])
        desc_row.pack(fill="x", pady=(6, 0))
        tk.Label(desc_row, text="📝", bg=COLORS["bg_panel"],
                 fg=COLORS["accent3"], font=FONTS["body"]).pack(side="left")
        self.desc_var = tk.StringVar()
        desc_entry = tk.Entry(desc_row, textvariable=self.desc_var,
                               bg=COLORS["btn_bg"], fg=COLORS["text_primary"],
                               insertbackground=COLORS["accent"],
                               relief="flat", font=FONTS["body"],
                               highlightthickness=1,
                               highlightbackground=COLORS["panel_border"],
                               highlightcolor=COLORS["accent"])
        desc_entry.pack(side="left", fill="x", expand=True, padx=(6, 0))
        desc_entry.bind("<Return>",   self._on_desc_change)
        desc_entry.bind("<FocusOut>", self._on_desc_change)

        # ══ Colonne 2 : stats temps réel ════════════════════
        stats_outer = tk.Frame(body, bg=COLORS["bg_panel"],
                                highlightbackground=COLORS["panel_border"],
                                highlightthickness=1, width=200)
        stats_outer.pack(side="left", fill="y", padx=4)
        stats_outer.pack_propagate(False)

        stats_frame = tk.Frame(stats_outer, bg=COLORS["bg_panel"], padx=10, pady=8)
        stats_frame.pack(fill="both", expand=True)

        tk.Label(stats_frame, text="📊 Dataset",
                 bg=COLORS["bg_panel"], fg=COLORS["info"],
                 font=FONTS["subtitle"]).pack(anchor="w")

        self.lbl_total = tk.Label(stats_frame, text="Images : —",
                                   bg=COLORS["bg_panel"], fg=COLORS["text_secondary"],
                                   font=FONTS["small"], anchor="w")
        self.lbl_total.pack(fill="x")

        self.lbl_annotated = tk.Label(stats_frame, text="Annotées : —",
                                       bg=COLORS["bg_panel"], fg=COLORS["text_secondary"],
                                       font=FONTS["small"], anchor="w")
        self.lbl_annotated.pack(fill="x")

        self.stats_classes = tk.Frame(stats_frame, bg=COLORS["bg_panel"])
        self.stats_classes.pack(fill="x", pady=(4, 0))

        # ══ Colonne 3 : NOTE ════════════════════════════════
        note_outer = tk.Frame(body, bg=COLORS["bg_panel"],
                               highlightbackground=COLORS["panel_border"],
                               highlightthickness=1)
        note_outer.pack(side="right", fill="y", padx=(4, 0))

        note_frame = tk.Frame(note_outer, bg=COLORS["bg_panel"], padx=12, pady=8)
        note_frame.pack(fill="both", expand=True)

        # Titre note
        tk.Label(note_frame, text="Note de qualité",
                 bg=COLORS["bg_panel"], fg=COLORS["warning"],
                 font=FONTS["subtitle"]).pack(anchor="center")

        # ── Étoiles grandes et cliquables ────────────────────
        stars_row = tk.Frame(note_frame, bg=COLORS["bg_panel"])
        stars_row.pack(anchor="center", pady=4)

        self._star_btns = []
        for i in range(1, 6):
            btn = tk.Button(
                stars_row,
                text="★",
                font=("Segoe UI", 20),
                fg=COLORS["text_muted"],
                bg=COLORS["bg_panel"],
                activebackground=COLORS["bg_panel"],
                activeforeground=COLORS["warning"],
                relief="flat", borderwidth=0,
                cursor="hand2",
                command=lambda v=i: self._on_star_click(v),
            )
            btn.pack(side="left", padx=1)
            # Hover : colore jusqu'à cette étoile
            btn.bind("<Enter>", lambda e, v=i: self._hover_stars(v))
            btn.bind("<Leave>", lambda e: self._hover_stars(self._note_val))
            self._star_btns.append(btn)

        # Texte note actuelle
        self.lbl_note_text = tk.Label(note_frame, text="Non noté",
                                       bg=COLORS["bg_panel"],
                                       fg=COLORS["text_muted"],
                                       font=FONTS["small"])
        self.lbl_note_text.pack(anchor="center")

        # Bouton effacer note
        self.btn_clear_note = tk.Button(
            note_frame, text="✕ Effacer",
            command=lambda: self._on_star_click(0),
            bg=COLORS["btn_bg"], fg=COLORS["text_muted"],
            relief="flat", font=FONTS["small"],
            padx=6, pady=2, cursor="hand2",
        )
        self.btn_clear_note.pack(anchor="center", pady=(2, 0))

        # ── Badge classe ──────────────────────────────────────
        tk.Frame(note_frame, bg=COLORS["panel_border"], height=1
                 ).pack(fill="x", pady=6)
        class_row = tk.Frame(note_frame, bg=COLORS["bg_panel"])
        class_row.pack(anchor="center")
        tk.Label(class_row, text="🏷",
                 bg=COLORS["bg_panel"], fg=COLORS["text_secondary"],
                 font=FONTS["body"]).pack(side="left")
        self.class_var = tk.StringVar()
        self.class_badge = tk.Label(class_row, textvariable=self.class_var,
                                     bg=COLORS["accent"], fg="#fff",
                                     font=FONTS["btn"], padx=8, pady=2)
        self.class_badge.pack(side="left", padx=4)

    # ════════════════════════════════════════════════════════
    #  ÉTOILES
    # ════════════════════════════════════════════════════════
    NOTE_LABELS = ["", "Mauvais 😞", "Passable 😐", "Correct 🙂", "Bien 😊", "Excellent ⭐"]
    NOTE_COLORS = ["", "#EF4444", "#F97316", "#F7C948", "#84CC16", "#2ECC80"]

    def _on_star_click(self, val: int):
        self._note_val = val
        self._render_stars(val)
        if hasattr(self.app, "set_note"):
            self.app.set_note(val)

    def _hover_stars(self, val: int):
        for i, btn in enumerate(self._star_btns):
            if i < val:
                color = self.NOTE_COLORS[val] if val > 0 else COLORS["text_muted"]
                btn.config(fg=color, font=("Segoe UI", 22))
            else:
                btn.config(fg=COLORS["text_muted"], font=("Segoe UI", 20))

    def _render_stars(self, val: int):
        for i, btn in enumerate(self._star_btns):
            color = self.NOTE_COLORS[val] if val > 0 else COLORS["text_muted"]
            btn.config(fg=color if i < val else COLORS["text_muted"],
                       font=("Segoe UI", 20))
        text = self.NOTE_LABELS[val] if 0 < val <= 5 else "Non noté"
        color = self.NOTE_COLORS[val] if 0 < val <= 5 else COLORS["text_muted"]
        self.lbl_note_text.config(text=text, fg=color)

    # ════════════════════════════════════════════════════════
    #  MISE À JOUR
    # ════════════════════════════════════════════════════════
    def update(self, filename="—", size="—", mode="—", classe="—",
               note=0, path="—", desc=""):
        self.lbl_info.config(
            text=f"Fichier : {filename}     Taille : {size}     Mode : {mode}")
        self.lbl_path.config(text=f"📁 {path}")
        self.class_var.set(classe if classe not in ("—", "") else "")
        self.desc_var.set(desc)
        self._note_val = int(note) if str(note).isdigit() else 0
        self._render_stars(self._note_val)

    def update_label_badge(self, label: str, color: str):
        self.class_var.set(label if label not in ("—", "") else "")
        try:
            fg = "#111" if _is_light(color) else "#fff"
            self.class_badge.config(bg=color, fg=fg)
        except Exception:
            pass

    def update_stats(self, total: int, annotated: int, label_counts: dict):
        self.lbl_total.config(text=f"🖼 Images : {total}")
        pct = f"{annotated/total*100:.0f}%" if total > 0 else "0%"
        self.lbl_annotated.config(text=f"✏ Annotées : {annotated} / {total} ({pct})")

        for w in self.stats_classes.winfo_children():
            w.destroy()

        for label, count in sorted(label_counts.items(), key=lambda x: -x[1]):
            if label.startswith("_") or count == 0:
                continue
            color = label_counts.get(f"_color_{label}", COLORS["accent"])
            row = tk.Frame(self.stats_classes, bg=COLORS["bg_panel"])
            row.pack(fill="x", pady=1)

            # Pastille
            tk.Label(row, text="●", fg=color, bg=COLORS["bg_panel"],
                     font=("Segoe UI", 8)).pack(side="left")
            tk.Label(row, text=f"{label[:10]:<10}",
                     bg=COLORS["bg_panel"], fg=COLORS["text_secondary"],
                     font=FONTS["small"]).pack(side="left")
            # Barre
            if total > 0:
                bar_w = max(3, int(count / total * 50))
                tk.Frame(row, bg=color, width=bar_w, height=6
                         ).pack(side="left", padx=(2, 4), pady=3)
            tk.Label(row, text=str(count), bg=COLORS["bg_panel"],
                     fg=COLORS["accent2"], font=FONTS["small"]).pack(side="left")

    def clear(self):
        self.update()
        self.update_stats(0, 0, {})

    # ════════════════════════════════════════════════════════
    #  CALLBACKS
    # ════════════════════════════════════════════════════════
    def _on_desc_change(self, event=None):
        if hasattr(self.app, "set_description"):
            self.app.set_description(self.desc_var.get())


def _is_light(hex_color: str) -> bool:
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        return (r*299 + g*587 + b*114)/1000 > 128
    except Exception:
        return False
