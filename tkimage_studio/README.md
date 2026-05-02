# TkImage Studio

Outil de gestion, annotation et prétraitement d'images pour projets de Machine Learning.

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

## Structure

```
tkimage_studio/
├── main.py              # Point d'entrée
├── app.py               # Logique principale
├── requirements.txt
├── assets/
│   ├── icons/
│   └── themes/
├── data/
│   ├── input_images/
│   ├── output_images/
│   ├── annotations/
│   └── labels/
└── src/
    ├── ui/
    │   ├── main_window.py
    │   ├── menu_bar.py
    │   ├── top_toolbar.py
    │   ├── left_toolbar.py
    │   ├── image_viewer.py
    │   ├── right_panel.py
    │   └── status_panel.py
    ├── core/
    └── utils/
        └── constants.py
```

## Fonctionnalités (Version 1)

- Ouvrir une image ou un dossier d'images
- Navigation avec slider et flèches clavier
- Zoom avant / arrière / ajustement
- Filtres : niveaux de gris, flou, netteté, contraste, luminosité, inversion, autocontraste
- Segmentation : seuillage, masque binaire
- Transformations : resize, crop, rotation, compression
- Annotations : note /5, classe
- Export JSON / CSV
- Interface modulaire et redimensionnable

## Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| Ctrl+O | Ouvrir une image |
| Ctrl+D | Ouvrir un dossier |
| Ctrl+S | Enregistrer |
| Ctrl+Z | Annuler |
| Ctrl+Y | Rétablir |
| ← → | Image précédente / suivante |
| + / - | Zoom avant / arrière |
| Ctrl+Q | Quitter |
