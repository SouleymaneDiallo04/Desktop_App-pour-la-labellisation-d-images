# ============================================================
#  TkImage Studio — main_window.py  v1.6
# ============================================================
import tkinter as tk
from tkinter import messagebox

from src.utils.constants import COLORS, FONTS, APP_TITLE, APP_VERSION, APP_AUTHOR
from src.ui.menu_bar     import build_menu
from src.ui.top_toolbar  import TopToolbar
from src.ui.left_toolbar import LeftToolbar
from src.ui.image_viewer import ImageViewer
from src.ui.right_panel  import RightPanel
from src.ui.status_panel import StatusPanel
from src.ui.label_panel  import LabelPanel
from src.ui.filter_bar   import FilterBar


class MainWindow:

    def __init__(self, root: tk.Tk):
        self.root = root
        self._configure_root()
        self._build_layout()
        self._bind_shortcuts()

    def _configure_root(self):
        self.root.title(APP_TITLE)
        self.root.geometry("1350x820")
        self.root.minsize(950, 650)
        self.root.configure(bg=COLORS["bg_main"])
        try:
            self.root.iconbitmap("assets/icons/app.ico")
        except Exception:
            pass

    def _build_layout(self):
        build_menu(self.root, self)

        self.top_toolbar = TopToolbar(self.root, self)
        self.top_toolbar.pack(fill="x", side="top")
        tk.Frame(self.root, bg=COLORS["panel_border"], height=1).pack(fill="x")

        self.filter_bar = FilterBar(self.root, self)
        self.filter_bar.pack(fill="x", side="top")
        tk.Frame(self.root, bg=COLORS["panel_border"], height=1).pack(fill="x")

        self.main_frame = tk.Frame(self.root, bg=COLORS["bg_main"])
        self.main_frame.pack(fill="both", expand=True)

        # Gauche
        self.left_toolbar = LeftToolbar(self.main_frame, self)
        self.left_toolbar.pack(side="left", fill="y", padx=(6, 0), pady=6)
        tk.Frame(self.main_frame, bg=COLORS["panel_border"], width=1
                 ).pack(side="left", fill="y", padx=3)

        # Droite
        right_col = tk.Frame(self.main_frame, bg=COLORS["bg_main"])
        right_col.pack(side="right", fill="y", padx=(0, 6), pady=6)

        self.right_panel = RightPanel(right_col, self)
        self.right_panel.pack(fill="x")

        tk.Frame(right_col, bg=COLORS["panel_border"], height=1).pack(fill="x", pady=4)

        self.label_panel = LabelPanel(right_col, self)
        self.label_panel.pack(fill="both", expand=True)

        tk.Frame(self.main_frame, bg=COLORS["panel_border"], width=1
                 ).pack(side="right", fill="y", padx=3)

        # Centre
        self.image_viewer = ImageViewer(self.main_frame, self)
        self.image_viewer.pack(side="left", fill="both", expand=True, pady=6)

        # Bas
        tk.Frame(self.root, bg=COLORS["panel_border"], height=1).pack(fill="x")
        self.status_panel = StatusPanel(self.root, self)
        self.status_panel.pack(fill="x", side="bottom", padx=6, pady=(4, 6))

    def _bind_shortcuts(self):
        self.root.bind("<Control-o>",       lambda e: self.open_image())
        self.root.bind("<Control-d>",       lambda e: self.open_folder())
        self.root.bind("<Control-s>",       lambda e: self.save_image())
        self.root.bind("<Control-z>",       lambda e: self.undo())
        # Redo — plusieurs variantes pour Windows/Linux/Mac
        self.root.bind("<Control-y>",       lambda e: self.redo())
        self.root.bind("<Control-Y>",       lambda e: self.redo())
        self.root.bind("<Control-Shift-z>", lambda e: self.redo())
        self.root.bind("<Control-Shift-Z>", lambda e: self.redo())
        self.root.bind("<Control-q>",       lambda e: self.quit_app())
        self.root.bind("<Left>",            lambda e: self.prev_image())
        self.root.bind("<Right>",           lambda e: self.next_image())
        self.root.bind("<plus>",            lambda e: self.zoom_in())
        self.root.bind("<minus>",           lambda e: self.zoom_out())
        self.root.bind("<KeyPress>",        self._on_keypress)
        # Adaptation fenêtre au redimensionnement
        self.root.bind("<Configure>",       self._on_window_resize)
        self._resize_job = None

    def _on_keypress(self, event):
        if event.char in [str(i) for i in range(1, 10)]:
            self.label_panel.handle_shortcut(event.char)

    def _on_window_resize(self, event):
        """Redimensionnement différé pour ne pas spammer _display_current."""
        if event.widget is not self.root:
            return
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(150, self._on_resize_done)

    def _on_resize_done(self):
        self._resize_job = None
        if hasattr(self, "_current_img") and self._current_img is not None:
            self._display_current()

    # ── Stubs ────────────────────────────────────────────────
    def open_image(self):            pass
    def open_folder(self):           pass
    def save_image(self):            pass
    def save_image_as(self):         pass
    def export_annotations(self):    pass
    def quit_app(self):              self.root.quit()
    def undo(self):                  pass
    def redo(self):                  pass
    def delete_from_session(self):   pass
    def reset_image(self):           pass
    def apply_filter(self, name):    pass
    def segmentation(self, name):    pass
    def visu3d(self, name):          pass
    def zoom_in(self):               pass
    def zoom_out(self):              pass
    def fit_to_window(self):         pass
    def resize_image(self):          pass
    def compress_image(self):        pass
    def crop_image(self):            pass
    def mouse_crop(self):            pass
    def rotate_image(self):          pass
    def toggle_repere(self):         pass
    def toggle_pan(self):            pass
    def toggle_select_region(self):  pass
    def on_region_selected(self, x0, y0, x1, y1): pass
    def apply_filter_with_params(self, p):         pass
    def ia_analyze(self):            pass
    def ia_open_panel(self):         pass
    def show_stats(self):            pass
    def navigate_to(self, idx):      pass
    def prev_image(self):            pass
    def next_image(self):            pass
    def set_note(self, val):         pass
    def set_class(self, val):        pass
    def set_description(self, val):  pass
    def set_label_badge(self, l, c): pass
    def apply_mouse_crop(self, x0, y0, x1, y1): pass
    def _display_current(self):      pass

    def show_about(self):
        messagebox.showinfo("À propos",
            f"TkImage Studio\nVersion : {APP_VERSION}\n\n"
            "Outil de gestion, annotation et prétraitement\n"
            "d'images pour projets de Machine Learning.\n\n"
            f"Auteur : {APP_AUTHOR}")

    def show_help(self):
        messagebox.showinfo("Aide",
            "Raccourcis clavier :\n"
            "  Ctrl+O           — Ouvrir une image\n"
            "  Ctrl+D           — Ouvrir un dossier\n"
            "  Ctrl+S           — Enregistrer\n"
            "  Ctrl+Z           — Annuler\n"
            "  Ctrl+Y           — Rétablir\n"
            "  Ctrl+Shift+Z     — Rétablir (alternative)\n"
            "  ← →              — Image précédente / suivante\n"
            "  +  /  −          — Zoom avant / arrière\n"
            "  Molette          — Zoom sur l'image\n"
            "  1 à 9            — Appliquer un label\n"
        )
