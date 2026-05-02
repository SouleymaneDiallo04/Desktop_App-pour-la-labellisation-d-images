# ============================================================
#  TkImage Studio — ia_panel.py  v1.6
#  Extension IA — Mistral API
# ============================================================
import tkinter as tk
from tkinter import messagebox
import threading
import json
import urllib.request
import urllib.error
import base64
import os

from src.utils.constants import COLORS, FONTS


class IAPanel(tk.Toplevel):
    """
    Fenêtre IA indépendante :
    - Configuration clé API Mistral + modèle
    - Choix de tâche
    - Prompt personnalisé
    - Bouton Générer
    - Zone de réponse scrollable
    - Bouton Copier le code
    """

    MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
    MISTRAL_MODELS = [
        "mistral-small-latest",
        "mistral-medium-latest",
        "mistral-large-latest",
        "open-mistral-7b",
    ]

    TASKS = [
        ("🔍 Décrire l'image",
         "Décris cette image en détail : sujet principal, couleurs dominantes, composition, qualité."),
        ("🏷 Suggérer une classe",
         "Analyse cette image et propose une ou plusieurs classes pour la classer dans un dataset ML. "
         "Réponds en JSON : {\"classe\": \"...\", \"confiance\": 0.xx, \"alternatives\": [...]}"),
        ("📊 Stratégie de classement",
         "Propose une stratégie de classement pour un dataset contenant ce type d'images. "
         "Inclus les classes suggérées, les critères et un exemple de structure de dossiers."),
        ("🛠 Générer du code de prétraitement",
         "Génère du code Python avec Pillow pour prétraiter cette image "
         "(resize 224x224, normalisation, augmentation). Fournis un script complet et commenté."),
        ("🔬 Analyser la qualité",
         "Analyse la qualité technique de cette image : netteté, exposition, bruit, "
         "artefacts. Donne une note sur 10 et des recommandations."),
        ("📝 Générer des annotations",
         "Génère des annotations JSON pour cette image au format COCO simplifié, "
         "avec les objets détectés, leurs positions approximatives et catégories."),
        ("💡 Suggérer des augmentations",
         "Suggère des techniques d'augmentation de données adaptées à cette image "
         "pour entraîner un modèle ML. Génère le code Python correspondant."),
        ("✏ Prompt personnalisé", ""),
    ]

    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        self.title("TkImage Studio — Extension IA (Mistral)")
        self.geometry("720x700")
        self.minsize(600, 500)
        self.configure(bg=COLORS["bg_main"])
        self.resizable(True, True)

        # Charge la config sauvegardée
        self._config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../models/api_config.json")
        self._config = self._load_config()

        self._build()
        self._restore_config()

        # Fermeture propre
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # ════════════════════════════════════════════════════════
    #  CONSTRUCTION UI
    # ════════════════════════════════════════════════════════
    def _build(self):
        # ── Titre ────────────────────────────────────────────
        hdr = tk.Frame(self, bg=COLORS["ia_panel_hdr"], pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🤖  Extension IA — Mistral API",
                 bg=COLORS["ia_panel_hdr"], fg=COLORS["accent3"],
                 font=FONTS["title"]).pack(side="left", padx=16)

        body = tk.Frame(self, bg=COLORS["bg_main"])
        body.pack(fill="both", expand=True, padx=12, pady=8)

        # ── Section 1 : Configuration API ────────────────────
        self._section(body, "⚙  Configuration API")

        cfg_frame = tk.Frame(body, bg=COLORS["bg_panel"],
                              highlightbackground=COLORS["panel_border"],
                              highlightthickness=1)
        cfg_frame.pack(fill="x", pady=(0, 8))
        cfg_inner = tk.Frame(cfg_frame, bg=COLORS["bg_panel"], padx=10, pady=8)
        cfg_inner.pack(fill="x")

        # Clé API
        row1 = tk.Frame(cfg_inner, bg=COLORS["bg_panel"])
        row1.pack(fill="x", pady=3)
        tk.Label(row1, text="🔑 Clé API :", bg=COLORS["bg_panel"],
                 fg=COLORS["text_secondary"], font=FONTS["body"], width=12,
                 anchor="w").pack(side="left")
        self.api_key_var = tk.StringVar()
        self.entry_key = tk.Entry(row1, textvariable=self.api_key_var,
                                   show="•", width=40,
                                   bg=COLORS["btn_bg"], fg=COLORS["text_primary"],
                                   insertbackground=COLORS["accent"],
                                   relief="flat", font=FONTS["mono"],
                                   highlightthickness=1,
                                   highlightbackground=COLORS["panel_border"],
                                   highlightcolor=COLORS["accent"])
        self.entry_key.pack(side="left", fill="x", expand=True, padx=(6, 4))
        # Bouton afficher/masquer
        self._show_key = False
        self.btn_show = tk.Button(row1, text="👁", command=self._toggle_key_visibility,
                                   bg=COLORS["btn_bg"], fg=COLORS["text_secondary"],
                                   relief="flat", font=FONTS["body"],
                                   padx=6, cursor="hand2")
        self.btn_show.pack(side="left")

        # Modèle
        row2 = tk.Frame(cfg_inner, bg=COLORS["bg_panel"])
        row2.pack(fill="x", pady=3)
        tk.Label(row2, text="🧠 Modèle :", bg=COLORS["bg_panel"],
                 fg=COLORS["text_secondary"], font=FONTS["body"], width=12,
                 anchor="w").pack(side="left")
        self.model_var = tk.StringVar(value=self.MISTRAL_MODELS[0])
        model_menu = tk.OptionMenu(row2, self.model_var, *self.MISTRAL_MODELS)
        model_menu.config(bg=COLORS["btn_bg"], fg=COLORS["text_primary"],
                          activebackground=COLORS["accent"],
                          activeforeground="#fff",
                          relief="flat", borderwidth=0,
                          font=FONTS["body"], highlightthickness=0)
        model_menu["menu"].config(bg=COLORS["bg_panel"], fg=COLORS["text_primary"],
                                   activebackground=COLORS["accent"])
        model_menu.pack(side="left", padx=6)

        # Bouton sauvegarder config
        tk.Button(cfg_inner, text="💾 Sauvegarder la config",
                  command=self._save_config,
                  bg=COLORS["accent_dark"], fg="#fff",
                  relief="flat", font=FONTS["small"],
                  padx=8, pady=3, cursor="hand2"
                  ).pack(anchor="e", pady=(4, 0))

        # ── Section 2 : Tâche ────────────────────────────────
        self._section(body, "📋  Choisir une tâche")

        task_frame = tk.Frame(body, bg=COLORS["bg_panel"],
                               highlightbackground=COLORS["panel_border"],
                               highlightthickness=1)
        task_frame.pack(fill="x", pady=(0, 8))
        task_inner = tk.Frame(task_frame, bg=COLORS["bg_panel"], padx=10, pady=8)
        task_inner.pack(fill="x")

        self.task_var = tk.StringVar(value=self.TASKS[0][0])
        for i, (name, _) in enumerate(self.TASKS):
            rb = tk.Radiobutton(task_inner, text=name,
                                 variable=self.task_var, value=name,
                                 command=self._on_task_select,
                                 bg=COLORS["bg_panel"], fg=COLORS["text_primary"],
                                 selectcolor=COLORS["btn_bg"],
                                 activebackground=COLORS["bg_panel"],
                                 font=FONTS["body"], cursor="hand2")
            rb.grid(row=i//2, column=i%2, sticky="w", padx=8, pady=2)

        # ── Section 3 : Prompt ───────────────────────────────
        self._section(body, "✏  Prompt")

        prompt_frame = tk.Frame(body, bg=COLORS["bg_panel"],
                                 highlightbackground=COLORS["panel_border"],
                                 highlightthickness=1)
        prompt_frame.pack(fill="x", pady=(0, 8))
        prompt_inner = tk.Frame(prompt_frame, bg=COLORS["bg_panel"], padx=10, pady=6)
        prompt_inner.pack(fill="x")

        self.prompt_text = tk.Text(prompt_inner, height=4, wrap="word",
                                    bg=COLORS["btn_bg"], fg=COLORS["text_primary"],
                                    insertbackground=COLORS["accent"],
                                    relief="flat", font=FONTS["body"],
                                    highlightthickness=1,
                                    highlightbackground=COLORS["panel_border"],
                                    highlightcolor=COLORS["accent"])
        self.prompt_text.pack(fill="x")
        self._on_task_select()  # charge le prompt par défaut

        # Bouton inclure image
        self.include_img_var = tk.BooleanVar(value=True)
        tk.Checkbutton(prompt_inner, text="📷 Inclure l'image active (vision)",
                       variable=self.include_img_var,
                       bg=COLORS["bg_panel"], fg=COLORS["text_secondary"],
                       selectcolor=COLORS["btn_bg"],
                       activebackground=COLORS["bg_panel"],
                       font=FONTS["small"], cursor="hand2"
                       ).pack(anchor="w", pady=(4, 0))

        # ── Bouton Générer ───────────────────────────────────
        gen_row = tk.Frame(body, bg=COLORS["bg_main"])
        gen_row.pack(fill="x", pady=6)

        self.btn_generate = tk.Button(
            gen_row, text="▶  Générer la réponse",
            command=self._generate,
            bg=COLORS["accent3"], fg="#fff",
            activebackground=COLORS["accent3_dark"],
            relief="flat", font=FONTS["title"],
            padx=20, pady=8, cursor="hand2",
        )
        self.btn_generate.pack(side="left")

        self.lbl_status = tk.Label(gen_row, text="",
                                    bg=COLORS["bg_main"],
                                    fg=COLORS["text_secondary"],
                                    font=FONTS["small"])
        self.lbl_status.pack(side="left", padx=12)

        # ── Section 4 : Réponse ──────────────────────────────
        self._section(body, "💬  Réponse")

        resp_frame = tk.Frame(body, bg=COLORS["bg_panel"],
                               highlightbackground=COLORS["panel_border"],
                               highlightthickness=1)
        resp_frame.pack(fill="both", expand=True, pady=(0, 4))

        resp_inner = tk.Frame(resp_frame, bg=COLORS["bg_panel"], padx=8, pady=6)
        resp_inner.pack(fill="both", expand=True)

        scroll = tk.Scrollbar(resp_inner)
        scroll.pack(side="right", fill="y")

        self.resp_text = tk.Text(resp_inner, wrap="word",
                                  bg=COLORS["bg_canvas"],
                                  fg=COLORS["text_primary"],
                                  insertbackground=COLORS["accent"],
                                  relief="flat", font=FONTS["mono"],
                                  yscrollcommand=scroll.set,
                                  state="disabled")
        self.resp_text.pack(fill="both", expand=True)
        scroll.config(command=self.resp_text.yview)

        # Boutons actions réponse
        action_row = tk.Frame(body, bg=COLORS["bg_main"])
        action_row.pack(fill="x", pady=(0, 4))

        self.btn_copy_all = tk.Button(action_row, text="📋 Tout copier",
                                       command=lambda: self._copy_text("all"),
                                       bg=COLORS["btn_bg"], fg=COLORS["text_primary"],
                                       relief="flat", font=FONTS["small"],
                                       padx=8, pady=4, cursor="hand2")
        self.btn_copy_all.pack(side="left", padx=(0, 4))

        self.btn_copy_code = tk.Button(action_row, text="</> Copier le code",
                                        command=lambda: self._copy_text("code"),
                                        bg=COLORS["accent_dark"], fg="#fff",
                                        relief="flat", font=FONTS["small"],
                                        padx=8, pady=4, cursor="hand2")
        self.btn_copy_code.pack(side="left", padx=(0, 4))

        tk.Button(action_row, text="🗑 Effacer",
                  command=self._clear_response,
                  bg=COLORS["btn_bg"], fg=COLORS["text_muted"],
                  relief="flat", font=FONTS["small"],
                  padx=8, pady=4, cursor="hand2"
                  ).pack(side="left")

        # Appliquer label suggéré
        self.btn_apply_class = tk.Button(action_row,
                                          text="✔ Appliquer la classe suggérée",
                                          command=self._apply_suggested_class,
                                          bg=COLORS["accent2"], fg="#111",
                                          relief="flat", font=FONTS["small"],
                                          padx=8, pady=4, cursor="hand2",
                                          state="disabled")
        self.btn_apply_class.pack(side="right")

        self._suggested_class = None

    # ════════════════════════════════════════════════════════
    #  HELPERS UI
    # ════════════════════════════════════════════════════════
    def _section(self, parent, title: str):
        row = tk.Frame(parent, bg=COLORS["panel_header"], pady=4)
        row.pack(fill="x", pady=(6, 2))
        tk.Label(row, text=title, bg=COLORS["panel_header"],
                 fg=COLORS["text_secondary"], font=FONTS["subtitle"]
                 ).pack(side="left", padx=10)

    def _on_task_select(self):
        selected = self.task_var.get()
        prompt = ""
        for name, p in self.TASKS:
            if name == selected:
                prompt = p
                break
        if prompt:
            self.prompt_text.config(state="normal")
            self.prompt_text.delete("1.0", "end")
            self.prompt_text.insert("1.0", prompt)

    def _toggle_key_visibility(self):
        self._show_key = not self._show_key
        self.entry_key.config(show="" if self._show_key else "•")
        self.btn_show.config(text="🔒" if self._show_key else "👁")

    # ════════════════════════════════════════════════════════
    #  CONFIG
    # ════════════════════════════════════════════════════════
    def _load_config(self) -> dict:
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_config(self):
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            config = {
                "api_key": self.api_key_var.get(),
                "model":   self.model_var.get(),
            }
            with open(self._config_path, "w") as f:
                json.dump(config, f, indent=2)
            self.lbl_status.config(text="✅ Config sauvegardée", fg=COLORS["success"])
            self.after(2000, lambda: self.lbl_status.config(text=""))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder : {e}")

    def _restore_config(self):
        if self._config.get("api_key"):
            self.api_key_var.set(self._config["api_key"])
        if self._config.get("model") in self.MISTRAL_MODELS:
            self.model_var.set(self._config["model"])

    # ════════════════════════════════════════════════════════
    #  GÉNÉRATION
    # ════════════════════════════════════════════════════════
    def _generate(self):
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showwarning("Clé API manquante",
                "Entrez votre clé API Mistral.\n"
                "Obtenez-la sur : https://console.mistral.ai/")
            return

        prompt = self.prompt_text.get("1.0", "end").strip()
        if not prompt:
            messagebox.showwarning("Prompt vide", "Écrivez un prompt avant de générer.")
            return

        self.btn_generate.config(state="disabled", text="⏳ Génération...")
        self.lbl_status.config(text="Appel à l'API Mistral...", fg=COLORS["warning"])
        self._clear_response()

        # Lance dans un thread pour ne pas bloquer l'UI
        thread = threading.Thread(target=self._call_api,
                                   args=(api_key, prompt), daemon=True)
        thread.start()

    def _call_api(self, api_key: str, prompt: str):
        try:
            model = self.model_var.get()
            messages = []

            # Construction du message avec ou sans image
            include_img = self.include_img_var.get()
            if include_img and hasattr(self.app, "_current_img") and self.app._current_img:
                # Encode l'image en base64
                import io
                buf = io.BytesIO()
                img = self.app._current_img.copy()
                img.thumbnail((512, 512))
                img.save(buf, format="JPEG", quality=85)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

                # Vision — format Mistral multimodal
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url",
                         "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                })
                # Modèle vision
                if "vision" not in model:
                    model = "pixtral-12b-2409"
            else:
                messages.append({"role": "user", "content": prompt})

            payload = json.dumps({
                "model":       model,
                "messages":    messages,
                "max_tokens":  1024,
                "temperature": 0.3,
            }).encode("utf-8")

            req = urllib.request.Request(
                self.MISTRAL_URL,
                data=payload,
                headers={
                    "Content-Type":  "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                self.after(0, lambda: self._show_response(content))

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            try:
                err_msg = json.loads(body).get("message", body)
            except Exception:
                err_msg = body
            self.after(0, lambda: self._show_error(f"HTTP {e.code} : {err_msg}"))
        except urllib.error.URLError as e:
            self.after(0, lambda: self._show_error(
                f"Connexion impossible : {e.reason}\n"
                "Vérifiez votre connexion internet."))
        except Exception as e:
            self.after(0, lambda: self._show_error(str(e)))

    def _show_response(self, content: str):
        self.resp_text.config(state="normal")
        self.resp_text.delete("1.0", "end")
        self.resp_text.insert("1.0", content)
        self.resp_text.config(state="disabled")

        self.btn_generate.config(state="normal", text="▶  Générer la réponse")
        self.lbl_status.config(text="✅ Réponse reçue", fg=COLORS["success"])
        self.after(3000, lambda: self.lbl_status.config(text=""))

        # Tente d'extraire une classe suggérée du JSON
        self._suggested_class = None
        try:
            import re
            match = re.search(r'\{[^{}]*"classe"\s*:\s*"([^"]+)"', content)
            if match:
                self._suggested_class = match.group(1)
                self.btn_apply_class.config(
                    state="normal",
                    text=f"✔ Appliquer : « {self._suggested_class} »")
        except Exception:
            pass

    def _show_error(self, msg: str):
        self.resp_text.config(state="normal")
        self.resp_text.delete("1.0", "end")
        self.resp_text.insert("1.0", f"❌ Erreur :\n\n{msg}")
        self.resp_text.config(state="disabled")
        self.btn_generate.config(state="normal", text="▶  Générer la réponse")
        self.lbl_status.config(text="❌ Erreur", fg=COLORS["danger"])

    def _clear_response(self):
        self.resp_text.config(state="normal")
        self.resp_text.delete("1.0", "end")
        self.resp_text.config(state="disabled")
        self.btn_apply_class.config(state="disabled",
                                     text="✔ Appliquer la classe suggérée")
        self._suggested_class = None

    # ════════════════════════════════════════════════════════
    #  COPIE
    # ════════════════════════════════════════════════════════
    def _copy_text(self, mode: str):
        content = self.resp_text.get("1.0", "end").strip()
        if not content:
            return

        if mode == "code":
            # Extrait les blocs de code entre ``` ```
            import re
            blocks = re.findall(r"```(?:\w+)?\n?(.*?)```", content, re.DOTALL)
            text = "\n\n".join(blocks) if blocks else content
        else:
            text = content

        self.clipboard_clear()
        self.clipboard_append(text)
        self.lbl_status.config(text="📋 Copié !", fg=COLORS["success"])
        self.after(2000, lambda: self.lbl_status.config(text=""))

    def _apply_suggested_class(self):
        if self._suggested_class and hasattr(self.app, "set_label_badge"):
            color = self.app.label_panel.get_label_color(self._suggested_class)
            self.app.set_label_badge(self._suggested_class, color)
            self.lbl_status.config(
                text=f"✅ Classe « {self._suggested_class} » appliquée",
                fg=COLORS["success"])
