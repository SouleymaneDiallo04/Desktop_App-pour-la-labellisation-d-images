# ============================================================
#  TkImage Studio — app.py  v1.6
# ============================================================
import os, json, csv, io
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageFilter, ImageOps, ImageEnhance

from src.ui.main_window  import MainWindow
from src.utils.constants import SUPPORTED_FORMATS, IMAGE_EXTENSIONS, COLORS


class App(MainWindow):

    def __init__(self, root: tk.Tk):
        super().__init__(root)
        self._image_list: list  = []
        self._current_idx: int  = 0
        self._original_img      = None
        self._current_img       = None
        self._history: list     = []
        self._redo_stack: list  = []
        self._zoom_factor       = 1.0
        self._annotations: dict = {}
        self._display_scale     = 1.0
        self._display_offset    = (0, 0)
        self._active_filter     = None
        self._repere_on         = False
        self._pan_on            = False
        self._select_on         = False
        self._ia_window         = None   # référence à la fenêtre IA

    # ════════════════════════════════════════════════════════
    #  FICHIERS
    # ════════════════════════════════════════════════════════
    def open_image(self):
        path = filedialog.askopenfilename(filetypes=SUPPORTED_FORMATS)
        if not path: return
        self._load_folder_images(os.path.dirname(path))
        idx = self._image_list.index(path) if path in self._image_list else 0
        self.navigate_to(idx)

    def open_folder(self):
        folder = filedialog.askdirectory(title="Sélectionner un dossier d'images")
        if not folder: return
        self._load_folder_images(folder)
        if self._image_list:
            self.navigate_to(0)
        else:
            messagebox.showinfo("Dossier vide", "Aucune image trouvée.")

    def _load_folder_images(self, folder: str):
        self._image_list = sorted(
            os.path.join(folder, f) for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS)
        self.image_viewer.set_slider(len(self._image_list), 0)

    def save_image(self):
        if self._current_img is None: return
        if self._image_list:
            self._current_img.save(self._image_list[self._current_idx])
            self._show_toast("Enregistré ✅")
        else:
            self.save_image_as()

    def save_image_as(self):
        if self._current_img is None: return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG","*.png"),("JPEG","*.jpg"),("All","*.*")])
        if path:
            self._current_img.save(path)
            self._show_toast(f"Enregistré : {os.path.basename(path)} ✅")

    def export_annotations(self):
        if not self._annotations:
            messagebox.showinfo("Export", "Aucune annotation à exporter."); return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON","*.json"),("CSV","*.csv")])
        if not path: return
        if path.endswith(".csv"):
            with open(path, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["fichier","chemin","classe","note","description",
                              "taille_w","taille_h","mode_couleur","poids_ko",
                              "exif_date","exif_appareil","exif_iso"]
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                for img_path, ann in self._annotations.items():
                    meta = ann.get("_meta", {})
                    w.writerow({
                        "fichier":       os.path.basename(img_path),
                        "chemin":        img_path,
                        "classe":        ann.get("class",""),
                        "note":          ann.get("note",0),
                        "description":   ann.get("desc",""),
                        "taille_w":      meta.get("w",""),
                        "taille_h":      meta.get("h",""),
                        "mode_couleur":  meta.get("mode",""),
                        "poids_ko":      meta.get("size_ko",""),
                        "exif_date":     meta.get("exif_date",""),
                        "exif_appareil": meta.get("exif_appareil",""),
                        "exif_iso":      meta.get("exif_iso",""),
                    })
        else:
            with open(path, "w", encoding="utf-8") as f:
                export_data = {
                    k: {ek: ev for ek,ev in v.items() if not ek.startswith("_")}
                    for k,v in self._annotations.items()}
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        self._show_toast("Annotations exportées ✅")

    def quit_app(self):
        if messagebox.askyesno("Quitter","Voulez-vous quitter TkImage Studio ?"):
            self.root.quit()

    # ════════════════════════════════════════════════════════
    #  NAVIGATION
    # ════════════════════════════════════════════════════════
    def navigate_to(self, idx: int):
        if not self._image_list: return
        idx = max(0, min(idx, len(self._image_list)-1))
        self._current_idx = idx
        path = self._image_list[idx]
        try:
            img = Image.open(path)
        except Exception as e:
            messagebox.showerror("Erreur", str(e)); return

        self._original_img = img.copy()
        self._current_img  = img.copy()
        self._history.clear()
        self._redo_stack.clear()
        self._zoom_factor = 1.0
        self.image_viewer.reset_pan()

        self._display_current()
        self._update_status(path)
        self.image_viewer.set_slider(len(self._image_list), idx)
        self.root.after(100, lambda: self.image_viewer.update_thumbnails(
            self._image_list, idx))

        ann = self._annotations.get(path, {})
        current_label = ann.get("class") or None
        self.label_panel.notify_image_changed(current_label)
        if current_label:
            color = self.label_panel.get_label_color(current_label)
            self.image_viewer.show_label_badge(current_label, color)
            self.status_panel.update_label_badge(current_label, color)

        self._load_exif(path, img)
        self._refresh_stats()

        self._annotations.setdefault(path, {})["_meta"] = {
            "w": img.width, "h": img.height,
            "mode": img.mode,
            "size_ko": round(os.path.getsize(path)/1024, 1),
        }

    def prev_image(self): self.navigate_to(self._current_idx-1)
    def next_image(self): self.navigate_to(self._current_idx+1)

    def delete_from_session(self):
        if not self._image_list: return
        del self._image_list[self._current_idx]
        if self._image_list:
            self.navigate_to(min(self._current_idx, len(self._image_list)-1))
        else:
            self.image_viewer.clear(); self.status_panel.clear()

    # ════════════════════════════════════════════════════════
    #  AFFICHAGE — s'adapte automatiquement au canvas
    # ════════════════════════════════════════════════════════
    def _display_current(self):
        if self._current_img is None: return
        canvas = self.image_viewer.canvas
        canvas.update_idletasks()
        cw = max(canvas.winfo_width(),  400)
        ch = max(canvas.winfo_height(), 300)
        img = self._current_img.copy()
        iw, ih = img.size
        scale = min(cw/iw, ch/ih) * self._zoom_factor
        nw = max(1, int(iw*scale))
        nh = max(1, int(ih*scale))
        self._display_scale  = scale
        self._display_offset = ((cw-nw)//2, (ch-nh)//2)
        img = img.resize((nw, nh), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        fname = os.path.basename(self._image_list[self._current_idx]) if self._image_list else ""
        self.image_viewer.display_image(tk_img, fname)
        # Redessine le badge label s'il y a une annotation
        path = self._current_path()
        if path:
            label = self._annotations.get(path, {}).get("class")
            if label:
                color = self.label_panel.get_label_color(label)
                self.image_viewer.show_label_badge(label, color)

    def _update_status(self, path: str):
        img = self._current_img
        if img is None: return
        ann = self._annotations.get(path, {})
        size_ko = round(os.path.getsize(path)/1024,1) if os.path.exists(path) else "—"
        self.status_panel.update(
            filename=os.path.basename(path),
            size=f"{img.width}×{img.height}  ({size_ko} Ko)",
            mode=img.mode,
            classe=ann.get("class","—"),
            note=ann.get("note",0),
            path=path, desc=ann.get("desc",""))

    # ════════════════════════════════════════════════════════
    #  EXIF
    # ════════════════════════════════════════════════════════
    def _load_exif(self, path: str, img: Image.Image):
        exif_data = {}
        try:
            raw = img._getexif() or {}
            from PIL.ExifTags import TAGS, GPSTAGS
            for tag_id, value in raw.items():
                exif_data[TAGS.get(tag_id, tag_id)] = value
            gps_info = exif_data.get("GPSInfo")
            if gps_info:
                gps = {GPSTAGS.get(k,k): v for k,v in gps_info.items()}
                lat = _dms_to_dd(gps.get("GPSLatitude"),  gps.get("GPSLatitudeRef","N"))
                lon = _dms_to_dd(gps.get("GPSLongitude"), gps.get("GPSLongitudeRef","E"))
                if lat and lon:
                    exif_data["_gps"] = f"{lat:.4f}, {lon:.4f}"
        except Exception:
            pass
        meta = self._annotations.get(path, {}).get("_meta", {})
        meta["exif_date"]     = exif_data.get("DateTime","")
        meta["exif_appareil"] = f"{exif_data.get('Make','')} {exif_data.get('Model','')}".strip()
        meta["exif_iso"]      = str(exif_data.get("ISOSpeedRatings",""))
        self._annotations.setdefault(path, {})["_meta"] = meta
        self.right_panel.update_exif(exif_data)

    # ════════════════════════════════════════════════════════
    #  STATS
    # ════════════════════════════════════════════════════════
    def _refresh_stats(self):
        total = len(self._image_list)
        annotated = sum(1 for a in self._annotations.values()
                        if a.get("class") and list(a.keys()) != ["_meta"])
        label_counts = self.label_panel.get_stats()
        for name in list(label_counts.keys()):
            label_counts[f"_color_{name}"] = self.label_panel.get_label_color(name)
        self.status_panel.update_stats(total, annotated, label_counts)

    # ════════════════════════════════════════════════════════
    #  UNDO / REDO
    # ════════════════════════════════════════════════════════
    def _push_history(self):
        if self._current_img:
            self._history.append(self._current_img.copy())
            self._redo_stack.clear()

    def undo(self):
        if self._history:
            self._redo_stack.append(self._current_img.copy())
            self._current_img = self._history.pop()
            self._display_current()
            self._show_toast("↩ Annulé")

    def redo(self):
        if self._redo_stack:
            self._history.append(self._current_img.copy())
            self._current_img = self._redo_stack.pop()
            self._display_current()
            self._show_toast("↪ Rétabli")

    def reset_image(self):
        if self._original_img:
            self._push_history()
            self._current_img = self._original_img.copy()
            self._zoom_factor = 1.0
            self.image_viewer.reset_pan()
            self._display_current()

    # ════════════════════════════════════════════════════════
    #  ZOOM & PAN
    # ════════════════════════════════════════════════════════
    def zoom_in(self):
        self._zoom_factor = min(self._zoom_factor*1.25, 8.0)
        self._display_current()

    def zoom_out(self):
        self._zoom_factor = max(self._zoom_factor*0.8, 0.1)
        self._display_current()

    def fit_to_window(self):
        self._zoom_factor = 1.0
        self.image_viewer.reset_pan()
        self._display_current()

    def toggle_pan(self):
        self._pan_on = not self._pan_on
        self._select_on = False
        self.image_viewer.set_pan(self._pan_on)
        self.image_viewer.set_select_region(False)
        if self._pan_on:
            self._repere_on = False
            self.image_viewer.set_repere(False)

    def toggle_select_region(self):
        self._select_on = not self._select_on
        self._pan_on = False
        self.image_viewer.set_select_region(self._select_on)
        self.image_viewer.set_pan(False)

    def on_region_selected(self, ix0, iy0, ix1, iy1):
        self._show_toast(f"⬚ Région : ({ix0},{iy0}) → ({ix1},{iy1})  {ix1-ix0}×{iy1-iy0}px")

    def toggle_repere(self):
        self._repere_on = not self._repere_on
        self.image_viewer.set_repere(self._repere_on)
        if self._repere_on:
            self._pan_on = False
            self.image_viewer.set_pan(False)

    # ════════════════════════════════════════════════════════
    #  TRANSFORMATIONS
    # ════════════════════════════════════════════════════════
    def resize_image(self):
        if self._current_img is None: return
        w = simpledialog.askinteger("Resize","Largeur (px) :",
                                    minvalue=1, maxvalue=9999, initialvalue=self._current_img.width)
        if w is None: return
        h = simpledialog.askinteger("Resize","Hauteur (px) :",
                                    minvalue=1, maxvalue=9999, initialvalue=self._current_img.height)
        if h is None: return
        self._push_history()
        self._current_img = self._current_img.resize((w,h), Image.LANCZOS)
        self._display_current()
        self._show_toast(f"Redimensionné → {w}×{h} ✅")

    def compress_image(self):
        if self._current_img is None: return
        quality = simpledialog.askinteger("Compression JPEG","Qualité (1–95) :",
                                           minvalue=1, maxvalue=95, initialvalue=75)
        if quality is None: return
        path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                             filetypes=[("JPEG","*.jpg")])
        if path:
            self._current_img.save(path,"JPEG", quality=quality, optimize=True)
            self._show_toast(f"Compressé q={quality} ✅")

    def crop_image(self):
        if self._current_img is None: return
        w, h = self._current_img.size
        left   = simpledialog.askinteger("Crop",f"Gauche  (0–{w}):", minvalue=0, maxvalue=w-1, initialvalue=0)
        top    = simpledialog.askinteger("Crop",f"Haut    (0–{h}):", minvalue=0, maxvalue=h-1, initialvalue=0)
        right  = simpledialog.askinteger("Crop",f"Droite  (1–{w}):", minvalue=1, maxvalue=w,   initialvalue=w)
        bottom = simpledialog.askinteger("Crop",f"Bas     (1–{h}):", minvalue=1, maxvalue=h,   initialvalue=h)
        if None in (left,top,right,bottom): return
        self._push_history()
        self._current_img = self._current_img.crop((left,top,right,bottom))
        self._display_current()
        self._show_toast("Recadré ✅")

    def mouse_crop(self):
        if self._current_img is None:
            self._show_toast("⚠ Ouvrez d'abord une image"); return
        self.image_viewer.set_mouse_crop(True)
        self._show_toast("🖱 Tracez un rectangle pour recadrer")

    def apply_mouse_crop(self, cx0, cy0, cx1, cy1):
        if self._current_img is None: return
        ox, oy = self._display_offset
        scale  = self._display_scale
        pan    = self.image_viewer._pan_offset
        ix0 = max(0, int((cx0-ox-pan[0])/scale))
        iy0 = max(0, int((cy0-oy-pan[1])/scale))
        ix1 = min(self._current_img.width,  int((cx1-ox-pan[0])/scale))
        iy1 = min(self._current_img.height, int((cy1-oy-pan[1])/scale))
        if ix1>ix0 and iy1>iy0:
            self._push_history()
            self._current_img = self._current_img.crop((ix0,iy0,ix1,iy1))
            self.image_viewer.reset_pan()
            self._display_current()
            self._show_toast(f"Recadré ({ix1-ix0}×{iy1-iy0}) ✅")

    def rotate_image(self):
        if self._current_img is None: return
        angle = simpledialog.askfloat("Rotation","Angle (degrés) :", initialvalue=90.0)
        if angle is None: return
        self._push_history()
        self._current_img = self._current_img.rotate(angle, expand=True)
        self._display_current()
        self._show_toast(f"Rotation {angle}° ✅")

    # ════════════════════════════════════════════════════════
    #  FILTRES
    # ════════════════════════════════════════════════════════
    FILTER_MAP = {
        "grayscale":    lambda img, p: img.convert("L").convert("RGB"),
        "blur":         lambda img, p: img.filter(ImageFilter.GaussianBlur(
                            radius=max(1, p.get("blur_radius",2)))),
        "sharpen":      lambda img, p: img.filter(ImageFilter.UnsharpMask(
                            radius=p.get("sharpen_val",2), percent=150)),
        "contrast":     lambda img, p: ImageEnhance.Contrast(img).enhance(
                            max(0.1, p.get("contrast_val",1.8))),
        "brightness":   lambda img, p: ImageEnhance.Brightness(img).enhance(
                            max(0.1, p.get("brightness_val",1.4))),
        "invert":       lambda img, p: ImageOps.invert(img.convert("RGB")),
        "autocontrast": lambda img, p: ImageOps.autocontrast(img.convert("RGB")),
    }

    def apply_filter(self, name: str):
        self._active_filter = name
        self._apply_filter_internal(name, {})
        if hasattr(self, "filter_bar"):
            self.filter_bar._set_active(name)

    def apply_filter_with_params(self, params: dict):
        if self._active_filter and self._active_filter in self.FILTER_MAP:
            self._apply_filter_internal(self._active_filter, params)
        else:
            self._show_toast("⚠ Sélectionnez d'abord un filtre dans la barre")

    def _apply_filter_internal(self, name: str, params: dict):
        if self._current_img is None: return
        fn = self.FILTER_MAP.get(name)
        if not fn: return
        self._push_history()
        try:
            self._current_img = fn(self._current_img, params)
            self._display_current()
            self._show_toast(f"Filtre « {name} » ✅")
        except Exception as e:
            messagebox.showerror("Filtre", str(e))

    # ════════════════════════════════════════════════════════
    #  SEGMENTATION — extraction ROI réelle
    # ════════════════════════════════════════════════════════
    def segmentation(self, name: str):
        if self._current_img is None: return

        if name == "extract_zone":
            self._extract_roi(); return

        self._push_history()
        img = self._current_img.convert("L")
        if name == "threshold":
            t = simpledialog.askinteger("Seuillage","Valeur (0–255):",
                                         minvalue=0, maxvalue=255, initialvalue=128)
            if t is None: return
            self._current_img = img.point(lambda p: 255 if p>t else 0).convert("RGB")
        elif name == "binary_mask":
            self._current_img = img.point(lambda p: 255 if p>127 else 0).convert("RGB")
        self._display_current()
        self._show_toast(f"Segmentation « {name} » ✅")

    def _extract_roi(self):
        """Extraction ROI : l'utilisateur trace un rectangle, puis choisit où sauvegarder."""
        if self._current_img is None: return

        # Dialogue de confirmation
        result = messagebox.askyesno(
            "Extraction ROI",
            "Tracez un rectangle sur l'image (mode Sélection).\n\n"
            "La zone sélectionnée sera extraite et sauvegardée séparément.\n\n"
            "Cliquez OK pour activer le mode sélection, puis tracez votre rectangle.")
        if not result: return

        # Active le mode sélection avec callback spécial ROI
        self._roi_extract_mode = True
        self._select_on = True
        self.image_viewer.set_select_region(True)
        self._show_toast("⬚ Tracez le rectangle ROI à extraire, puis relâchez")

    def on_region_selected(self, ix0, iy0, ix1, iy1):
        if getattr(self, "_roi_extract_mode", False):
            self._roi_extract_mode = False
            self._select_on = False
            self.image_viewer.set_select_region(False)
            self._do_save_roi(ix0, iy0, ix1, iy1)
        else:
            self._show_toast(f"⬚ Région : ({ix0},{iy0}) → ({ix1},{iy1})  {ix1-ix0}×{iy1-iy0}px")

    def _do_save_roi(self, ix0, iy0, ix1, iy1):
        if self._current_img is None or ix1<=ix0 or iy1<=iy0:
            messagebox.showwarning("ROI","Zone trop petite, recommencez."); return

        roi = self._current_img.crop((ix0, iy0, ix1, iy1))

        # Propose un nom par défaut basé sur l'image courante
        base = ""
        if self._image_list:
            stem = os.path.splitext(os.path.basename(self._image_list[self._current_idx]))[0]
            base = f"{stem}_roi_{ix0}_{iy0}_{ix1}_{iy1}.png"

        save_path = filedialog.asksaveasfilename(
            title="Enregistrer la zone extraite",
            initialfile=base,
            defaultextension=".png",
            filetypes=[("PNG","*.png"),("JPEG","*.jpg"),("All","*.*")])

        if not save_path: return

        roi.save(save_path)
        w, h = roi.size

        # Propose d'ouvrir la ROI comme image active
        if messagebox.askyesno("ROI extraite",
                               f"Zone {w}×{h} px sauvegardée :\n{save_path}\n\n"
                               "Ouvrir cette zone comme image active ?"):
            self._push_history()
            self._original_img = roi.copy()
            self._current_img  = roi.copy()
            if self._image_list:
                self._image_list.insert(self._current_idx+1, save_path)
                self._current_idx += 1
                self.image_viewer.set_slider(len(self._image_list), self._current_idx)
            self._display_current()
            self._show_toast(f"ROI {w}×{h} px extraite ✅")
        else:
            self._show_toast(f"ROI {w}×{h} px sauvegardée ✅")

    # ════════════════════════════════════════════════════════
    #  VISUALISATION 3D
    # ════════════════════════════════════════════════════════
    def visu3d(self, name: str):
        try:
            import matplotlib; matplotlib.use("TkAgg")
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            messagebox.showinfo("Visualisation 3D","Installez matplotlib :\n  pip install matplotlib"); return
        if self._current_img is None: return
        gray = np.array(self._current_img.convert("L").resize((100,100)))
        fig = plt.figure(figsize=(7,5)); fig.patch.set_facecolor("#12151F")
        ax = fig.add_subplot(111, projection="3d"); ax.set_facecolor("#12151F")
        X, Y = np.meshgrid(range(gray.shape[1]), range(gray.shape[0]))
        if name == "surface":
            ax.plot_surface(X,Y,gray,cmap="viridis",linewidth=0); ax.set_title("Surface d'intensité",color="white")
        elif name == "map":
            ax.contourf(X,Y,gray,cmap="plasma"); ax.set_title("Carte simulée",color="white")
        else:
            ax.plot_wireframe(X,Y,gray,color="#4F8EF7",linewidth=0.3); ax.set_title("Empilement de coupes",color="white")
        plt.tight_layout(); plt.show()

    # ════════════════════════════════════════════════════════
    #  IA — FENÊTRE MISTRAL
    # ════════════════════════════════════════════════════════
    def ia_analyze(self):
        self.ia_open_panel()

    def ia_open_panel(self):
        """Ouvre (ou met au premier plan) la fenêtre IA Mistral."""
        if self._ia_window and tk.Toplevel.winfo_exists(self._ia_window):
            self._ia_window.lift()
            self._ia_window.focus_force()
            return
        from src.ui.ia_panel import IAPanel
        self._ia_window = IAPanel(self)

    # ════════════════════════════════════════════════════════
    #  ANNOTATIONS
    # ════════════════════════════════════════════════════════
    def set_note(self, val: int):
        path = self._current_path()
        if path:
            self._annotations.setdefault(path,{})["note"] = val
            self._refresh_stats()

    def set_class(self, val: str):
        path = self._current_path()
        if path:
            self._annotations.setdefault(path,{})["class"] = val
            self._update_status(path)
            self._refresh_stats()

    def set_description(self, val: str):
        path = self._current_path()
        if path:
            self._annotations.setdefault(path,{})["desc"] = val

    def set_label_badge(self, label: str, color: str):
        self.image_viewer.show_label_badge(label, color)
        self.status_panel.update_label_badge(label, color)
        self.set_class(label)

    def clear_label_badge(self):
        self.image_viewer.canvas.delete("badge")
        self.status_panel.update_label_badge("", COLORS["btn_bg"])
        self.set_class("")

    # ════════════════════════════════════════════════════════
    #  STATISTIQUES
    # ════════════════════════════════════════════════════════
    def show_stats(self):
        total = len(self._image_list)
        annotated = sum(1 for a in self._annotations.values() if a.get("class"))
        notes = [a["note"] for a in self._annotations.values()
                 if isinstance(a.get("note"),int) and a["note"]>0]
        label_stats = self.label_panel.get_stats()
        lines = [
            f"📂 Total images      : {total}",
            f"✏  Images annotées   : {annotated}",
            f"⭐ Moyenne des notes  : " + (f"{sum(notes)/len(notes):.1f}/5" if notes else "—"),
            "","🏷  Répartition par label :",
        ]
        for lbl,cnt in sorted(label_stats.items(), key=lambda x:-x[1]):
            if cnt>0:
                lines.append(f"  {lbl:15s} {'█'*min(cnt,20)} {cnt}")
        if not any(v>0 for v in label_stats.values()):
            lines.append("  (aucune annotation encore)")
        messagebox.showinfo("Statistiques", "\n".join(lines))

    # ════════════════════════════════════════════════════════
    #  UTILITAIRES
    # ════════════════════════════════════════════════════════
    def _current_path(self):
        return self._image_list[self._current_idx] if self._image_list else None

    def _show_toast(self, msg: str):
        self.root.title(f"TkImage Studio  ·  {msg}")
        self.root.after(3000, lambda: self.root.title(
            "TkImage Studio – Gestion et préparation d'images"))


def _dms_to_dd(dms, ref):
    try:
        d,m,s = float(dms[0]),float(dms[1]),float(dms[2])
        dd = d + m/60 + s/3600
        return -dd if ref in ("S","W") else dd
    except Exception:
        return None
