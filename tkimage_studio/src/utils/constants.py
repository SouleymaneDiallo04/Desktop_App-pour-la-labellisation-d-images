# ============================================================
#  TkImage Studio — Constants & Theme v1.5
#  Design amélioré : dégradés, couleurs par catégorie de bouton
# ============================================================

APP_TITLE   = "TkImage Studio – Gestion et préparation d'images"
APP_VERSION = "1.5.0"
APP_AUTHOR  = "Pr. Brahim BAKKAS"

# ── Palette principale (fond plus profond, contrastes plus riches) ──
COLORS = {
    # Fonds
    "bg_main":        "#12151F",   # fond global très sombre
    "bg_panel":       "#1A1E2E",   # panneaux
    "bg_toolbar":     "#0E1118",   # barre d'outils
    "bg_menubar":     "#0A0D14",   # barre de menus
    "bg_viewer":      "#0D1017",   # zone viewer
    "bg_canvas":      "#111420",   # canvas image
    "bg_statusbar":   "#0E1118",   # barre de statut

    # Accents
    "accent":         "#4F8EF7",   # bleu principal
    "accent_light":   "#7AADFF",
    "accent_dark":    "#2B6FD4",
    "accent2":        "#2ECC80",   # vert succès
    "accent2_dark":   "#1FA060",
    "accent3":        "#FF8C42",   # orange IA
    "accent3_dark":   "#CC6A20",
    "accent4":        "#A855F7",   # violet sélection
    "accent4_dark":   "#8030D0",

    # Textes
    "text_primary":   "#EDF2FF",
    "text_secondary": "#7B86A0",
    "text_muted":     "#3D4560",

    # Boutons génériques
    "btn_bg":         "#1E2438",
    "btn_hover":      "#2A3250",
    "btn_active":     "#4F8EF7",
    "btn_border":     "#2A3250",

    # Panneaux
    "panel_border":   "#1E2840",
    "panel_header":   "#141828",
    "ia_panel_bg":    "#111830",
    "ia_panel_hdr":   "#0D1428",
    "label_panel_bg": "#111828",
    "label_panel_hdr":"#0A1220",

    # Slider
    "slider_trough":  "#1E2438",
    "slider_fill":    "#4F8EF7",

    # États
    "success":        "#2ECC80",
    "warning":        "#F7C948",
    "danger":         "#EF4444",
    "danger_dark":    "#B91C1C",
    "info":           "#38BDF8",
}

# ── Couleurs par catégorie de bouton ─────────────────────────
BTN_COLORS = {
    # Fichiers  — bleu
    "open_image":    ("#1D3A6B", "#4F8EF7"),
    "save_image":    ("#1D3A6B", "#4F8EF7"),
    "undo":          ("#2A2050", "#7C6FF7"),
    # Zoom  — cyan
    "zoom_in":       ("#0F3040", "#38BDF8"),
    "zoom_out":      ("#0F3040", "#38BDF8"),
    "fit_to_window": ("#0F3040", "#38BDF8"),
    # Déplacement  — violet
    "toggle_pan":    ("#2A1550", "#A855F7"),
    # Transformations  — orange
    "resize_image":  ("#3A1E00", "#FF8C42"),
    "compress_image":("#3A1E00", "#FF8C42"),
    "crop_image":    ("#3A1E00", "#FF8C42"),
    "mouse_crop":    ("#3A1E00", "#FF8C42"),
    "rotate_image":  ("#3A1E00", "#FF8C42"),
    # Analyse  — vert
    "toggle_select_region": ("#0F3020", "#2ECC80"),
    "toggle_repere": ("#0F3020", "#2ECC80"),
}

# ── Couleurs des boutons de la barre top ──────────────────────
TOP_BTN_COLORS = {
    "open_image":  ("#4F8EF7", "#FFFFFF"),   # bleu
    "save_image":  ("#2ECC80", "#FFFFFF"),   # vert
    "undo":        ("#7C6FF7", "#FFFFFF"),   # violet
    "crop_image":  ("#FF8C42", "#FFFFFF"),   # orange
    "rotate_image":("#FF8C42", "#FFFFFF"),   # orange
    "zoom_in":     ("#38BDF8", "#111420"),   # cyan
    "zoom_out":    ("#38BDF8", "#111420"),   # cyan
    "ia_analyze":  ("#A855F7", "#FFFFFF"),   # violet IA
    "show_stats":  ("#F7C948", "#111420"),   # jaune stats
}

# ── Couleurs des boutons de filtres ───────────────────────────
FILTER_BTN_COLORS = {
    "grayscale":    ("#6B7280", "#FFFFFF"),
    "blur":         ("#0E4060", "#38BDF8"),
    "sharpen":      ("#1A3A60", "#4F8EF7"),
    "contrast":     ("#3B1D5A", "#A855F7"),
    "brightness":   ("#3A2E00", "#F7C948"),
    "invert":       ("#2D0E30", "#F74FA0"),
    "autocontrast": ("#0E3020", "#2ECC80"),
    "reset":        ("#3A0E0E", "#EF4444"),
}

# ── Labels de classification ──────────────────────────────────
LABEL_COLORS = [
    "#4F8EF7","#2ECC80","#FF8C42","#EF4444","#A855F7",
    "#F7C948","#38BDF8","#F74FA0","#84CC16","#F97316",
]
DEFAULT_LABELS = ["normal", "anomalie", "bon", "mauvais", "incertain"]
LABEL_SHORTCUTS = {str(i+1): i for i in range(9)}

# ── Typographies ─────────────────────────────────────────────
FONTS = {
    "title":    ("Segoe UI", 12, "bold"),
    "subtitle": ("Segoe UI", 10, "bold"),
    "body":     ("Segoe UI", 9),
    "small":    ("Segoe UI", 8),
    "mono":     ("Consolas",  9),
    "btn":      ("Segoe UI", 9, "bold"),
    "icon_btn": ("Segoe UI", 10, "bold"),
    "star":     ("Segoe UI", 14),
}

LEFT_PANEL_WIDTH  = 130
RIGHT_PANEL_WIDTH = 215

SUPPORTED_FORMATS = (
    ("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.gif *.webp"),
    ("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"),
    ("BMP", "*.bmp"), ("TIFF", "*.tiff *.tif"),
    ("All files", "*.*"),
)
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".gif", ".webp"}
