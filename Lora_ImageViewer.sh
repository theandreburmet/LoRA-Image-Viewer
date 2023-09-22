#!/bin/bash

# Chemin vers votre environnement virtuel .venv (remplacez-le par le bon chemin)
VENV_PATH=".venv"

# Activez l'environnement virtuel
source "$VENV_PATH/bin/activate"

# Exécutez le script Python
python3 Lora_Folder_Viewer.py

# Désactivez l'environnement virtuel (après avoir exécuté le script si nécessaire)
deactivate
