# Fitness_score — Installation & Run

Ce document décrit l’installation complète et le lancement du projet **Fitness_score**.

---

# Prérequis

Avant de commencer, assure-toi d’avoir :

- Conda (Miniconda ou Anaconda)
- Python 3.9+
- WSL recommandé (Linux conseillé)

---

# Installation complète

## 1. Se placer dans le projet

```bash
cd Fitness_score
```

## 2. Créer l’environnement Conda

```bash
conda create -n fitness python=3.9 -y
```

## 3. Activer l’environnement

```bash
conda activate fitness
```

## 4. Installer les dépendances scientifiques (conda-forge)

```bash
conda install -c conda-forge \
numpy=1.26.4 \
scipy \
pandas \
matplotlib \
scikit-learn \
statsmodels \
biopython \
pymol-open-source \
pyqt \
pyqtchart \
pyqtwebengine \
requests \
tqdm \
openbabel \
-y
```

## 5. Installer les dépendances Python (pip)
```bash
pip install -r env/requirements_pip_clean.txt
```

---

# Lancement du projet
```bash
cd src
python Scoring_website.py
```