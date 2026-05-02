# ============================================================
#  TkImage Studio — image_viewer.py  v1.4
#  Zone centrale : canvas + pan + sélection région + miniatures
# ============================================================
import tkinter as tk
from src.utils.constants import COLORS, FONTS


class ImageViewer(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_viewer"], relief="flat")
        self.app = app
        # Modes
        self._mouse_crop_active  = False
        self._select_region_active = False
        self._repere_active      = False
        self._pan_active         = False
        # État pan
        self._pan_start          = None
        self._pan_offset         = [0, 0]   # décalage courant [dx, dy]
        # État crop / sélection
        self._crop_start         = None
        self._image_center       = (0, 0)   # centre d'affichage de l'image
        self._build()

    # ════════════════════════════════════════════════════════
    #  CONSTRUCTION
    # ════════════════════════════════════════════════════════
    def _build(self):
        # En-tête
        hdr = tk.Frame(self, bg=COLORS["panel_header"], pady=5)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Visualisation centrale",
                 bg=COLORS["panel_header"], fg=COLORS["accent"],
                 font=FONTS["subtitle"]).pack(side="left", padx=12)

        # Mode actif
        self.lbl_mode = tk.Label(hdr, text="",
                                  bg=COLORS["panel_header"],
                                  fg=COLORS["accent3"], font=FONTS["small"])
        self.lbl_mode.pack(side="right", padx=6)

        self.lbl_name = tk.Label(hdr, text="",
                                  bg=COLORS["panel_header"],
                                  fg=COLORS["text_secondary"], font=FONTS["small"])
        self.lbl_name.pack(side="right", padx=12)

        # Canvas
        canvas_frame = tk.Frame(self, bg=COLORS["bg_canvas"])
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=(6, 4))

        self.canvas = tk.Canvas(canvas_frame, bg=COLORS["bg_canvas"],
                                 relief="flat", borderwidth=0,
                                 highlightthickness=1,
                                 highlightbackground=COLORS["panel_border"])
        self.canvas.pack(fill="both", expand=True)
        self._draw_placeholder()

        # Bindings
        self.canvas.bind("<Motion>",         self._on_motion)
        self.canvas.bind("<ButtonPress-1>",  self._on_press)
        self.canvas.bind("<B1-Motion>",      self._on_drag)
        self.canvas.bind("<ButtonRelease-1>",self._on_release)
        self.canvas.bind("<MouseWheel>",     self._on_mousewheel)
        self.canvas.bind("<ButtonPress-2>",  self._start_pan)   # clic milieu
        self.canvas.bind("<B2-Motion>",      self._do_pan)
        self.canvas.bind("<Configure>",      self._on_resize)

        # ── Miniatures ───────────────────────────────────────
        self.thumb_frame = tk.Frame(self, bg=COLORS["bg_viewer"], height=64)
        self.thumb_frame.pack(fill="x", padx=10, pady=(0, 4))
        self.thumb_frame.pack_propagate(False)

        self.thumb_canvas = tk.Canvas(self.thumb_frame,
                                       bg=COLORS["bg_viewer"],
                                       height=60, highlightthickness=0)
        self.thumb_scroll = tk.Scrollbar(self.thumb_frame, orient="horizontal",
                                          command=self.thumb_canvas.xview)
        self.thumb_canvas.configure(xscrollcommand=self.thumb_scroll.set)
        self.thumb_scroll.pack(side="bottom", fill="x")
        self.thumb_canvas.pack(fill="both", expand=True)

        self.thumb_inner = tk.Frame(self.thumb_canvas, bg=COLORS["bg_viewer"])
        self.thumb_canvas.create_window((0, 0), window=self.thumb_inner, anchor="nw")
        self.thumb_inner.bind("<Configure>",
            lambda e: self.thumb_canvas.configure(
                scrollregion=self.thumb_canvas.bbox("all")))

        self._thumb_refs = []    # garde les PhotoImage en mémoire
        self._thumb_btns = []    # boutons miniatures

        # ── Slider navigation ────────────────────────────────
        slider_frame = tk.Frame(self, bg=COLORS["bg_viewer"], pady=4)
        slider_frame.pack(fill="x", padx=10, pady=(0, 6))

        tk.Label(slider_frame, text="Navigation :",
                 bg=COLORS["bg_viewer"], fg=COLORS["text_secondary"],
                 font=FONTS["small"]).pack(side="left")

        self.btn_prev = tk.Button(slider_frame, text="◀",
            command=lambda: getattr(self.app, "prev_image", lambda: None)(),
            bg=COLORS["btn_bg"], fg=COLORS["text_primary"],
            relief="flat", font=FONTS["btn"], padx=6, cursor="hand2")
        self.btn_prev.pack(side="left", padx=4)

        self.slider_var = tk.IntVar(value=0)
        self.slider = tk.Scale(slider_frame, from_=0, to=0,
                                orient="horizontal", variable=self.slider_var,
                                command=self._on_slider_change,
                                bg=COLORS["bg_viewer"], fg=COLORS["text_primary"],
                                troughcolor=COLORS["slider_trough"],
                                activebackground=COLORS["accent"],
                                highlightthickness=0, sliderrelief="flat",
                                relief="flat", showvalue=False)
        self.slider.pack(fill="x", padx=4, side="left", expand=True)

        self.btn_next = tk.Button(slider_frame, text="▶",
            command=lambda: getattr(self.app, "next_image", lambda: None)(),
            bg=COLORS["btn_bg"], fg=COLORS["text_primary"],
            relief="flat", font=FONTS["btn"], padx=6, cursor="hand2")
        self.btn_next.pack(side="left", padx=4)

        self.lbl_count = tk.Label(slider_frame, text="0 / 0",
                                   bg=COLORS["bg_viewer"],
                                   fg=COLORS["text_secondary"], font=FONTS["small"])
        self.lbl_count.pack(side="right", padx=6)

    # ════════════════════════════════════════════════════════
    #  API PUBLIQUE
    # ════════════════════════════════════════════════════════
    def display_image(self, tk_image, filename=""):
        self.canvas.delete("all")
        self.canvas.update_idletasks()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        dx, dy = self._pan_offset
        cx = w // 2 + dx
        cy = h // 2 + dy
        self._image_center = (cx, cy)
        self.canvas.create_image(cx, cy, anchor="center", image=tk_image, tags="img")
        self.canvas.image = tk_image
        self.lbl_name.config(text=filename)

    def show_label_badge(self, label: str, color: str):
        self.canvas.delete("badge")
        w = self.canvas.winfo_width()
        self.canvas.create_rectangle(w-130, 8, w-8, 30,
                                      fill=color, outline="", tags="badge")
        self.canvas.create_text(w-69, 19, text=f"🏷 {label}",
                                 fill="#111" if _is_light(color) else "#fff",
                                 font=FONTS["small"], tags="badge")

    def clear(self):
        self.canvas.delete("all")
        self._pan_offset = [0, 0]
        self._draw_placeholder()
        self.lbl_name.config(text="")
        self._clear_thumbnails()

    def set_slider(self, total, current=0):
        self.slider.config(from_=0, to=max(total - 1, 0))
        self.slider_var.set(current)
        self.lbl_count.config(text=f"{current + 1} / {max(total, 1)}")

    def set_mouse_crop(self, active: bool):
        self._mouse_crop_active = active
        self._select_region_active = False
        self._pan_active = False
        self.canvas.config(cursor="crosshair" if active else "arrow")
        self.lbl_mode.config(text="✂ Mode recadrage" if active else "")

    def set_select_region(self, active: bool):
        self._select_region_active = active
        self._mouse_crop_active = False
        self._pan_active = False
        self.canvas.config(cursor="crosshair" if active else "arrow")
        self.lbl_mode.config(text="⬚ Sélection région" if active else "")

    def set_pan(self, active: bool):
        self._pan_active = active
        self._mouse_crop_active = False
        self._select_region_active = False
        self.canvas.config(cursor="fleur" if active else "arrow")
        self.lbl_mode.config(text="✋ Déplacement" if active else "")

    def set_repere(self, active: bool):
        self._repere_active = active
        self.canvas.config(cursor="tcross" if active else "arrow")
        if not active:
            self.canvas.delete("coord", "repere_lines")
        self.lbl_mode.config(text="🎯 Repère actif" if active else "")

    def reset_pan(self):
        self._pan_offset = [0, 0]

    # ── Miniatures ───────────────────────────────────────────
    def update_thumbnails(self, image_list: list, current_idx: int):
        """Génère et affiche les miniatures de toutes les images."""
        self._clear_thumbnails()
        from PIL import Image, ImageTk
        for i, path in enumerate(image_list):
            try:
                img = Image.open(path)
                img.thumbnail((56, 48))
                tk_img = ImageTk.PhotoImage(img)
                self._thumb_refs.append(tk_img)

                is_current = (i == current_idx)
                bg = COLORS["accent_dark"] if is_current else COLORS["btn_bg"]
                border = 2 if is_current else 0

                frame = tk.Frame(self.thumb_inner, bg=COLORS["accent"] if is_current else COLORS["bg_viewer"],
                                  padx=border, pady=border)
                frame.pack(side="left", padx=2, pady=4)

                btn = tk.Button(frame, image=tk_img, command=lambda idx=i: self._on_thumb_click(idx),
                                 bg=bg, relief="flat", borderwidth=0, cursor="hand2",
                                 activebackground=COLORS["accent_dark"])
                btn.pack()
                self._thumb_btns.append((frame, btn))

                # Tooltip nom fichier
                import os
                name = os.path.basename(path)
                btn.bind("<Enter>", lambda e, n=name: self.lbl_mode.config(text=n))
                btn.bind("<Leave>", lambda e: self.lbl_mode.config(text=""))
            except Exception:
                pass

    def _clear_thumbnails(self):
        for w in self.thumb_inner.winfo_children():
            w.destroy()
        self._thumb_refs.clear()
        self._thumb_btns.clear()

    def _on_thumb_click(self, idx: int):
        if hasattr(self.app, "navigate_to"):
            self.app.navigate_to(idx)

    # ════════════════════════════════════════════════════════
    #  ÉVÉNEMENTS CANVAS
    # ════════════════════════════════════════════════════════
    def _on_motion(self, event):
        # Repère
        if self._repere_active:
            self.canvas.delete("coord", "repere_lines")
            # Coordonnées image réelles
            img_x, img_y = self._canvas_to_image(event.x, event.y)
            self.canvas.create_text(
                event.x + 14, event.y - 12,
                text=f"canvas({event.x},{event.y})  img({img_x},{img_y})",
                fill=COLORS["accent"], font=FONTS["small"],
                tags="coord", anchor="w")
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            self.canvas.create_line(0, event.y, w, event.y,
                                     fill=COLORS["accent"], dash=(4, 4), tags="repere_lines")
            self.canvas.create_line(event.x, 0, event.x, h,
                                     fill=COLORS["accent"], dash=(4, 4), tags="repere_lines")

        # Dessin rectangle (crop ou sélection)
        if (self._mouse_crop_active or self._select_region_active) and self._crop_start:
            self.canvas.delete("crop_rect")
            x0, y0 = self._crop_start
            color = COLORS["accent3"] if self._mouse_crop_active else COLORS["accent"]
            self.canvas.create_rectangle(x0, y0, event.x, event.y,
                                          outline=color, width=2, dash=(5, 3),
                                          tags="crop_rect")
            # Affiche dimensions sélection
            ix0, iy0 = self._canvas_to_image(x0, y0)
            ix1, iy1 = self._canvas_to_image(event.x, event.y)
            self.lbl_mode.config(
                text=f"{'✂' if self._mouse_crop_active else '⬚'} "
                     f"{abs(ix1-ix0)}×{abs(iy1-iy0)} px")

        # Pan visuel
        if self._pan_active and self._pan_start:
            dx = event.x - self._pan_start[0]
            dy = event.y - self._pan_start[1]
            self.canvas.move("img", dx, dy)
            self.canvas.move("badge", dx, dy)
            self._pan_start = (event.x, event.y)
            self._pan_offset[0] += dx
            self._pan_offset[1] += dy

    def _on_press(self, event):
        if self._mouse_crop_active or self._select_region_active:
            self._crop_start = (event.x, event.y)
        elif self._pan_active:
            self._pan_start = (event.x, event.y)
            self.canvas.config(cursor="fleur")

    def _on_drag(self, event):
        self._on_motion(event)

    def _on_release(self, event):
        if (self._mouse_crop_active or self._select_region_active) and self._crop_start:
            x0, y0 = self._crop_start
            x1, y1 = event.x, event.y
            self.canvas.delete("crop_rect")
            self._crop_start = None

            if abs(x1 - x0) > 10 and abs(y1 - y0) > 10:
                if self._mouse_crop_active:
                    self._mouse_crop_active = False
                    self.canvas.config(cursor="arrow")
                    self.lbl_mode.config(text="")
                    if hasattr(self.app, "apply_mouse_crop"):
                        self.app.apply_mouse_crop(
                            min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1))
                elif self._select_region_active:
                    # Affiche les coordonnées image de la région
                    ix0, iy0 = self._canvas_to_image(min(x0,x1), min(y0,y1))
                    ix1, iy1 = self._canvas_to_image(max(x0,x1), max(y0,y1))
                    self.lbl_mode.config(
                        text=f"⬚ Région : ({ix0},{iy0}) → ({ix1},{iy1})  |  {ix1-ix0}×{iy1-iy0} px")
                    if hasattr(self.app, "on_region_selected"):
                        self.app.on_region_selected(ix0, iy0, ix1, iy1)

        if self._pan_active:
            self._pan_start = None

    def _start_pan(self, event):
        """Clic bouton milieu = démarrer pan."""
        self._pan_start = (event.x, event.y)

    def _do_pan(self, event):
        if self._pan_start:
            dx = event.x - self._pan_start[0]
            dy = event.y - self._pan_start[1]
            self.canvas.move("img", dx, dy)
            self.canvas.move("badge", dx, dy)
            self._pan_start = (event.x, event.y)
            self._pan_offset[0] += dx
            self._pan_offset[1] += dy

    def _on_mousewheel(self, event):
        if event.delta > 0:
            getattr(self.app, "zoom_in", lambda: None)()
        else:
            getattr(self.app, "zoom_out", lambda: None)()

    def _on_slider_change(self, value):
        if hasattr(self.app, "navigate_to"):
            self.app.navigate_to(int(value))

    def _on_resize(self, event):
        pass  # réaffichage géré par app sur zoom/navigate

    # ════════════════════════════════════════════════════════
    #  UTILITAIRES
    # ════════════════════════════════════════════════════════
    def _canvas_to_image(self, cx, cy):
        """Convertit des coordonnées canvas en coordonnées image."""
        if hasattr(self.app, "_display_scale") and hasattr(self.app, "_display_offset"):
            ox, oy = self.app._display_offset
            scale  = self.app._display_scale
            ix = max(0, int((cx - ox - self._pan_offset[0]) / scale))
            iy = max(0, int((cy - oy - self._pan_offset[1]) / scale))
            return ix, iy
        return cx, cy

    def _draw_placeholder(self):
        self.canvas.update_idletasks()
        w = max(self.canvas.winfo_width(), 400)
        h = max(self.canvas.winfo_height(), 300)
        cx, cy = w // 2, h // 2
        self.canvas.create_rectangle(cx-160, cy-100, cx+160, cy+100,
                                      outline=COLORS["panel_border"], width=2, dash=(6, 4))
        self.canvas.create_text(cx, cy-20, text="🖼",
                                 fill=COLORS["text_muted"], font=("Segoe UI", 32))
        self.canvas.create_text(cx, cy+30, text="Image active",
                                 fill=COLORS["text_muted"], font=FONTS["subtitle"])
        self.canvas.create_text(cx, cy+55,
                                 text="Ouvrir une image ou un dossier pour commencer",
                                 fill=COLORS["text_muted"], font=FONTS["small"])


def _is_light(hex_color: str) -> bool:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r * 299 + g * 587 + b * 114) / 1000 > 128
