# 🧙‍♂️ The Quest-ionnable Heroe

> Une aventure interactive entre jeu et réflexion, développée avec passion par une équipe de jeunes héros du code.  
> Plongez dans un univers narratif où chaque choix influence votre destin !

---

## 🚀 Lancer le projet avec `uv`

### 🧩 Prérequis
Avant tout, assurez-vous d’avoir installé :

- [Python 3.13+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/)

> 💡 `uv` est un outil ultra-rapide qui remplace `pip`, `venv` et `poetry`.  
> Il gère les environnements virtuels et les dépendances automatiquement.

---

### ⚙️ Installation du projet

Clonez le dépôt :

```bash
git clone https://github.com/Sam-rst/The_Quest-ionnable_Heroe.git
cd The_Quest-ionnable_Heroe
````

Créez et activez l’environnement virtuel avec `uv` :

```bash
uv venv
```

Installez les dépendances du projet :

```bash
uv sync
```

> Cette commande installe toutes les dépendances définies dans `pyproject.toml`
> et prépare votre environnement de développement.

---

### 🧠 Lancer le jeu

Pour exécuter le projet :

```bash
uv run main.py
```

---

### 🧰 Commandes utiles

| Action                            | Commande            |
| --------------------------------- | ------------------- |
| Mettre à jour les dépendances     | `uv sync --upgrade` |
| Lister les paquets installés      | `uv pip list`       |
| Supprimer l’environnement virtuel | `uv env remove`     |
| Exécuter une commande dans l’env. | `uv run <commande>` |

---

## 📁 Structure du projet

```
The_Quest-ionnable_Heroe/
├── main.py              # Point d'entrée
├── src/
│   ├── engine/          # Moteur ECS réutilisable
│   └── game/            # Code spécifique au jeu
├── assets/
│   ├── sprites/         # Personnages, items, armes, potions
│   ├── maps/            # TMX, TSX, tilesets
│   ├── fonts/           # Polices
│   └── manifest.json    # Registre des sprites
├── saves/               # Sauvegardes (auto-générées)
└── docs/                # Documentation
```

---

## 🖥️ Compatibilité

| OS         | Compatible |
| ---------- | ---------- |
| 🪟 Windows | ✅          |
| 🐧 Linux   | ✅          |
| 🍎 macOS   | ✅          |

---

## 🤝 Équipe de développement

**✨ Réalisé par :**

| Nom | GitHub                                   | LinkedIn                                                                  |
|------|------------------------------------------|---------------------------------------------------------------------------|
| **Samuel RESSIOT** | [@Sam-rst](https://github.com/Sam-rst)   | [Samuel RESSIOT](https://www.linkedin.com/in/samuel-ressiot/)             |
| **Mateo CONSTANT** | [@RemiTS](https://github.com/mabitoski)  | Aucun                                                                    |
| **Rémi TRAN-SAMARCELLI** | Aucun                                    | [Rémi TRAN-SAMARCELLI](https://www.linkedin.com/in/r%C3%A9mi-tran-sammarcelli-389247262/) |
| **Bastien ROUPERT** | [@Comaaa](https://github.com/Comaaa)     | [Bastien ROUPERT](https://www.linkedin.com/in/bastien-roupert-a03a80228/)           |
| **Maxime PICO** | [@Syudagye](https://github.com/Syudagye) | [Maxime PICO](https://www.linkedin.com/in/maxime-pico-4853b426a/)                   |

---

## 📜 Licence

Ce projet est distribué sous la [Licence MIT](./LICENSE).

Vous êtes libres de :

* Utiliser, copier, modifier et redistribuer le code.
* L’intégrer dans vos propres projets, même commerciaux.
* Contribuer librement à son amélioration.

> ⚠️ Le logiciel est fourni "tel quel", sans garantie d’aucune sorte.
> Les auteurs ne sont pas responsables des dommages éventuels liés à son utilisation.

📄 Consultez le fichier [LICENSE](./LICENSE) pour plus de détails.

---

> *"Chaque bug est une quête, chaque commit une victoire."* ⚔️
