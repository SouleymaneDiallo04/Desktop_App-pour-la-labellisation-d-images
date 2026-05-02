#!/usr/bin/env python3
# ============================================================
#  TkImage Studio — main.py
#  Point d'entrée de l'application
# ============================================================
import sys
import os

# Assure que le dossier racine est dans le path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from app import App


def main():
    root = tk.Tk()

    # ── Apparence globale ────────────────────────────────────
    try:
        # Sur Windows, active le mode DPI haute résolution
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
