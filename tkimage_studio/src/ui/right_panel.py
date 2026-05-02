# ============================================================
#  TkImage Studio — right_panel.py  v1.4
#  Panneau droit : Paramètres traitement + EXIF + IA
# ============================================================
import tkinter as tk
from src.utils.constants import COLORS, FONTS


class RightPanel(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["ia_panel_bg"], width=210, relief="flat")
        self.app = app
        self.pack_propagate(False)
        self._build()

    def _build(self):
        # ── En-tête ─────────────────────────────────────────
        hdr = tk.Frame(self, bg=COLORS["ia_panel_hdr"], pady=5)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Paramètres & Infos",
                 bg=COLORS["ia_panel_hdr"], fg=COLORS["accent3"],
                 font=FONTS["subtitle"]).pack(side="left", padx=10)
        self.toggle_btn = tk.Button(hdr, text="👁", command=self._toggle,
                                     bg=COLORS["ia_panel_hdr"], fg=COLORS["text_secondary"],
                                     activebackground=COLORS["ia_panel_hdr"],
                                     relief="flat", borderwidth=0,
                                     cursor="hand2", font=FONTS["body"])
        self.toggle_btn.pack(side="right", padx=6)

        self.body = tk.Frame(self, bg=COLORS["ia_panel_bg"])
        self.body.pack(fill="both", expand=True)
        self._visible = True

        # ── 1. Paramètres de traitement ──────────────────────
        self._section_hdr(self.body, "⚙ Paramètres de traitement")

        params_frame = tk.Frame(self.body, bg=COLORS["ia_panel_bg"])
        params_frame.pack(fill="x", padx=8, pady=(0, 6))

        # Flou — rayon
        self._param_slider(params_frame, "Flou (rayon)", 0, 10, 2, "blur_radius")
        # Contraste
        self._param_slider(params_frame, "Contraste", 0, 30, 10, "contrast_val")
        # Luminosité
        self._param_slider(params_frame, "Luminosité", 0, 30, 10, "brightness_val")
        # Netteté
        self._param_slider(params_frame, "Netteté", 0, 10, 2,  "sharpen_val")
        # Seuillage
        self._param_slider(params_frame, "Seuil seg.", 0, 255, 128, "threshold_val")

        # Bouton appliquer avec paramètres
        tk.Button(params_frame, text="▶ Appliquer le filtre actif",
                  command=self._apply_with_params,
                  bg=COLORS["accent"], fg="#fff", relief="flat",
                  font=FONTS["small"], padx=6, pady=4, cursor="hand2"
                  ).pack(fill="x", pady=(6, 0))

        tk.Frame(self.body, bg=COLORS["panel_border"], height=1).pack(fill="x", padx=6, pady=6)

        # ── 2. Métadonnées EXIF ──────────────────────────────
        self._section_hdr(self.body, "📷 Métadonnées EXIF")

        exif_frame = tk.Frame(self.body, bg=COLORS["bg_panel"],
                               relief="flat", padx=6, pady=6)
        exif_frame.pack(fill="x", padx=8, pady=(0, 6))

        self._exif_labels = {}
        for key in ["Date", "Appareil", "Objectif", "ISO", "Exposition", "GPS"]:
            row = tk.Frame(exif_frame, bg=COLORS["bg_panel"])
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{key} :", bg=COLORS["bg_panel"],
                     fg=COLORS["text_secondary"], font=FONTS["small"],
                     width=9, anchor="w").pack(side="left")
            val = tk.Label(row, text="—", bg=COLORS["bg_panel"],
                           fg=COLORS["text_primary"], font=FONTS["small"],
                           anchor="w", wraplength=120, justify="left")
            val.pack(side="left", fill="x", expand=True)
            self._exif_labels[key] = val

        tk.Frame(self.body, bg=COLORS["panel_border"], height=1).pack(fill="x", padx=6, pady=6)

        # ── 3. Mode IA ───────────────────────────────────────
        self._section_hdr(self.body, "🤖 Mode IA / API")

        ia_frame = tk.Frame(self.body, bg=COLORS["ia_panel_bg"])
        ia_frame.pack(fill="x", padx=8, pady=(0, 6))

        self._section(ia_frame, "🏷 Classe suggérée")
        self.lbl_class = tk.Label(ia_frame, text="—",
                                   bg=COLORS["ia_panel_bg"], fg=COLORS["accent"],
                                   font=FONTS["subtitle"])
        self.lbl_class.pack(anchor="w", padx=6, pady=(0, 4))

        self._section(ia_frame, "🔖 Tags")
        self.lbl_tags = tk.Label(ia_frame, text="—",
                                  bg=COLORS["ia_panel_bg"], fg=COLORS["text_primary"],
                                  font=FONTS["small"], wraplength=180, justify="left")
        self.lbl_tags.pack(anchor="w", padx=6, pady=(0, 4))

        self._section(ia_frame, "⭐ Score")
        self.lbl_score = tk.Label(ia_frame, text="—",
                                   bg=COLORS["ia_panel_bg"], fg=COLORS["accent2"],
                                   font=FONTS["subtitle"])
        self.lbl_score.pack(anchor="w", padx=6, pady=(0, 4))

        tk.Button(ia_frame, text="🤖 Analyser l'image",
                  command=lambda: getattr(self.app, "ia_analyze", lambda: None)(),
                  bg=COLORS["accent3"], fg="#fff",
                  activebackground="#D4783A", relief="flat",
                  font=FONTS["btn"], padx=8, pady=5, cursor="hand2"
                  ).pack(fill="x", pady=(4, 0))

    # ════════════════════════════════════════════════════════
    #  HELPERS UI
    # ════════════════════════════════════════════════════════
    def _section_hdr(self, parent, title):
        f = tk.Frame(parent, bg=COLORS["panel_header"], pady=3)
        f.pack(fill="x")
        tk.Label(f, text=title, bg=COLORS["panel_header"],
                 fg=COLORS["text_secondary"], font=FONTS["small"]
                 ).pack(side="left", padx=8)

    def _section(self, parent, title):
        tk.Label(parent, text=title, bg=COLORS["ia_panel_bg"],
                 fg=COLORS["text_secondary"], font=FONTS["small"]
                 ).pack(anchor="w", pady=(4, 1))

    def _param_slider(self, parent, label, from_, to, default, attr):
        row = tk.Frame(parent, bg=COLORS["ia_panel_bg"])
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, bg=COLORS["ia_panel_bg"],
                 fg=COLORS["text_secondary"], font=FONTS["small"],
                 width=12, anchor="w").pack(side="left")
        var = tk.IntVar(value=default)
        setattr(self, f"_{attr}_var", var)
        val_lbl = tk.Label(row, textvariable=var, bg=COLORS["ia_panel_bg"],
                            fg=COLORS["accent"], font=FONTS["small"], width=3)
        val_lbl.pack(side="right")
        slider = tk.Scale(row, from_=from_, to=to, orient="horizontal",
                           variable=var, showvalue=False,
                           bg=COLORS["ia_panel_bg"], fg=COLORS["text_primary"],
                           troughcolor=COLORS["slider_trough"],
                           activebackground=COLORS["accent"],
                           highlightthickness=0, sliderrelief="flat", relief="flat",
                           length=90)
        slider.pack(side="left", fill="x", expand=True, padx=4)

    # ════════════════════════════════════════════════════════
    #  ACTIONS
    # ════════════════════════════════════════════════════════
    def _apply_with_params(self):
        params = {
            "blur_radius":    self._blur_radius_var.get(),
            "contrast_val":   self._contrast_val_var.get() / 10.0,
            "brightness_val": self._brightness_val_var.get() / 10.0,
            "sharpen_val":    self._sharpen_val_var.get(),
            "threshold_val":  self._threshold_val_var.get(),
        }
        if hasattr(self.app, "apply_filter_with_params"):
            self.app.apply_filter_with_params(params)

    def _toggle(self):
        if self._visible:
            self.body.pack_forget()
            self._visible = False
            self.toggle_btn.config(text="👁‍🗨")
        else:
            self.body.pack(fill="both", expand=True)
            self._visible = True
            self.toggle_btn.config(text="👁")

    # ════════════════════════════════════════════════════════
    #  MISE À JOUR EXIF
    # ════════════════════════════════════════════════════════
    def update_exif(self, exif_data: dict):
        mapping = {
            "Date":       exif_data.get("DateTime") or exif_data.get("DateTimeOriginal", "—"),
            "Appareil":   f"{exif_data.get('Make','—')} {exif_data.get('Model','')}".strip(),
            "Objectif":   exif_data.get("LensModel", "—"),
            "ISO":        str(exif_data.get("ISOSpeedRatings", "—")),
            "Exposition": exif_data.get("ExposureTime", "—"),
            "GPS":        exif_data.get("_gps", "—"),
        }
        for key, val in mapping.items():
            if key in self._exif_labels:
                self._exif_labels[key].config(text=str(val) if val else "—")

    def clear_exif(self):
        for lbl in self._exif_labels.values():
            lbl.config(text="—")

    def update_ia(self, class_=None, tags=None, score=None):
        if class_: self.lbl_class.config(text=class_)
        if tags:   self.lbl_tags.config(text=", ".join(tags) if isinstance(tags, list) else tags)
        if score is not None: self.lbl_score.config(text=f"{score:.1%}")
