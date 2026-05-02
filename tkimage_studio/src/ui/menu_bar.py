# ============================================================
#  TkImage Studio — menu_bar.py  v1.6
# ============================================================
import tkinter as tk
from src.utils.constants import COLORS, FONTS


def build_menu(root, app):
    menubar = tk.Menu(root,
        bg=COLORS["bg_menubar"], fg=COLORS["text_primary"],
        activebackground=COLORS["accent"], activeforeground="#FFF",
        relief="flat", borderwidth=0, font=FONTS["body"])

    _fichier(menubar, app)
    _edition(menubar, app)
    _filtres(menubar, app)
    _segmentation(menubar, app)
    _visu3d(menubar, app)
    _ia(menubar, app)
    _apropos(menubar, app)

    root.config(menu=menubar)
    return menubar


def _sub(parent):
    return tk.Menu(parent, tearoff=0,
        bg=COLORS["bg_panel"], fg=COLORS["text_primary"],
        activebackground=COLORS["accent"], activeforeground="#FFF",
        relief="flat", borderwidth=1, font=FONTS["body"])


def _fichier(mb, app):
    m = _sub(mb)
    m.add_command(label="📂  Ouvrir une image",    command=app.open_image,        accelerator="Ctrl+O")
    m.add_command(label="📁  Ouvrir un dossier",   command=app.open_folder,       accelerator="Ctrl+D")
    m.add_separator()
    m.add_command(label="💾  Enregistrer",          command=app.save_image,        accelerator="Ctrl+S")
    m.add_command(label="💾  Enregistrer sous…",    command=app.save_image_as)
    m.add_separator()
    m.add_command(label="📤  Exporter annotations", command=app.export_annotations)
    m.add_separator()
    m.add_command(label="❌  Quitter",              command=app.quit_app,          accelerator="Ctrl+Q")
    mb.add_cascade(label="Fichier", menu=m)


def _edition(mb, app):
    m = _sub(mb)
    m.add_command(label="↩  Annuler",                 command=app.undo,              accelerator="Ctrl+Z")
    m.add_command(label="↪  Rétablir",                command=app.redo,              accelerator="Ctrl+Y / Ctrl+Shift+Z")
    m.add_separator()
    m.add_command(label="🗑  Supprimer de la session", command=app.delete_from_session)
    m.add_command(label="🔄  Réinitialiser l'image",  command=app.reset_image)
    mb.add_cascade(label="Édition", menu=m)


def _filtres(mb, app):
    m = _sub(mb)
    m.add_command(label="⬜  Niveaux de gris",  command=lambda: app.apply_filter("grayscale"))
    m.add_command(label="🌫  Flou",             command=lambda: app.apply_filter("blur"))
    m.add_command(label="🔍  Netteté",          command=lambda: app.apply_filter("sharpen"))
    m.add_command(label="🎨  Contraste",        command=lambda: app.apply_filter("contrast"))
    m.add_command(label="☀  Luminosité",        command=lambda: app.apply_filter("brightness"))
    m.add_command(label="🌑  Inversion",        command=lambda: app.apply_filter("invert"))
    m.add_command(label="⚡  Autocontraste",    command=lambda: app.apply_filter("autocontrast"))
    mb.add_cascade(label="Filtres", menu=m)


def _segmentation(mb, app):
    m = _sub(mb)
    m.add_command(label="📊  Seuillage simple",     command=lambda: app.segmentation("threshold"))
    m.add_command(label="🖤  Masque binaire",        command=lambda: app.segmentation("binary_mask"))
    m.add_command(label="✂   Extraction ROI",        command=lambda: app.segmentation("extract_zone"))
    mb.add_cascade(label="Segmentation", menu=m)


def _visu3d(mb, app):
    m = _sub(mb)
    m.add_command(label="🗺  Carte simulée",        command=lambda: app.visu3d("map"))
    m.add_command(label="📈  Surface d'intensité",  command=lambda: app.visu3d("surface"))
    m.add_command(label="📐  Empilement de coupes", command=lambda: app.visu3d("stack"))
    mb.add_cascade(label="Visualisation 3D", menu=m)


def _ia(mb, app):
    m = _sub(mb)
    m.add_command(label="🤖  Ouvrir le panneau IA", command=app.ia_open_panel)
    m.add_separator()
    m.add_command(label="🔑  Configurer clé API…",  command=app.ia_open_panel)
    mb.add_cascade(label="IA / Mistral", menu=m)


def _apropos(mb, app):
    m = _sub(mb)
    m.add_command(label="ℹ  À propos",      command=app.show_about)
    m.add_command(label="📖  Documentation", command=app.show_help)
    mb.add_cascade(label="À propos", menu=m)
