# Comparatif des architectures

## Tableau de synthese

| Critere                     | A. Couches        | B. Scenes+Managers  | C. ECS              |
|-----------------------------|-------------------|---------------------|----------------------|
| **Effort de migration**     | Faible            | Moyen               | Eleve                |
| **Risque de regression**    | Faible            | Moyen               | Eleve                |
| **Supprime l'etat global**  | Partiellement     | Oui                 | Oui                  |
| **Gestion des scenes**      | Non               | Oui (pile)          | Oui (pile)           |
| **Decouplage**              | Faible            | Bon (EventBus)      | Excellent (World)    |
| **Duplication entites**     | Reduite (config)  | Reduite (config)    | Eliminee (factories) |
| **Extensibilite**           | Limitee           | Bonne               | Excellente           |
| **Testabilite**             | Faible            | Bonne               | Excellente           |
| **Complexite a comprendre** | Faible            | Moyenne             | Elevee               |
| **Adapte a pygame**         | Oui               | Oui                 | Possible mais atypique |
| **Adapte a la taille du projet** | Oui          | Oui                 | Sur-dimensionne      |

## Quelle architecture choisir ?

### Choix recommande : B. Scenes + Managers

C'est le **meilleur compromis** pour ce projet car :

1. **Resout les vrais problemes** : etat global, boucles imbriquees, duplication
2. **Pattern standard** dans la communaute pygame — beaucoup de ressources et tutoriels
3. **Progressif** : on peut migrer scene par scene (menu d'abord, puis gameplay, etc.)
4. **Suffisamment structure** sans etre sur-ingenierie pour un jeu de cette taille

### Strategie de migration recommandee

Il est possible de **combiner A puis B** progressivement :

```
Phase 1 (A) : Reorganiser en packages
  → Deplacer les fichiers dans src/
  → Decouper images.py en sprite_loader
  → Creer la classe Game (remplacer le main.py procedural)
  → Eliminer la duplication (config dicts + encodeur generique)

Phase 2 (B) : Ajouter le systeme de scenes
  → Creer Scene + SceneManager
  → Convertir Menu → MenuScene
  → Convertir la boucle de jeu → GameplayScene
  → Convertir GameOver → GameOverScene
  → Convertir Marchand → MerchantScene

Phase 3 (B) : Ajouter les managers
  → Extraire CombatManager de Caracter
  → Extraire SpawnManager de main.py
  → Ajouter EventBus pour decoupler
```

Cette approche **incrementale** minimise les risques car chaque phase produit un jeu fonctionnel.
