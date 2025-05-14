# Jeu de Ping Pong

Un jeu de ping pong dynamique avec bonus et système de service, développé avec Pygame.

## Binôme

Florian Henry-Labordère
Adrien Rognier 
(103)

## Modules à installer

Pour exécuter ce jeu, vous aurez besoin des modules suivants :

```
pygame
```

## Indications de démarrage

### Avec Thonny

Pour exécuter le jeu avec l'éditeur Thonny :

1. Ouvrez Thonny
2. Allez dans Outils > Gérer les paquets
3. Recherchez "pygame" et cliquez sur "Installer"
4. Ouvrez le fichier src/main.py
5. Cliquez sur le bouton "Exécuter" (triangle vert) ou appuyez sur F5

### Avec Conda

Si vous utilisez Conda, vous pouvez créer un environnement dédié et installer Pygame :

```bash
# Créer un nouvel environnement
conda create -n pingpong python=3.9

# Activer l'environnement
conda activate pingpong

# Installer Pygame
pip install pygame

# Lancer le jeu
python src/main.py
```


### Contrôles principaux

- **Joueur 1 (gauche)** : Z (monter) et S (descendre)
- **Joueur 2 (droite)** : Flèche haut (monter) et Flèche bas (descendre)
- **F** : Activer/désactiver le mode plein écran
- **Souris** : Navigation dans les menus 

## Améliorations

### Écran d'accueil
- Sélection du nombre de points à atteindre pour gagner: 5, 11 ou 21 points
- Bouton START pour lancer la partie
- "Commandes" pour afficher les contrôles
- Mode SOLO pour jouer contre l'ordinateur
- Accès à la BOUTIQUE pour personnaliser le jeu

### Mode Solo
- Jouez contre l'intelligence artificielle
- La raquette adverse suit automatiquement la position de la balle

### Système de jeu
- Table de jeu verte avec ligne centrale et bordure
- Joueur 1 (gauche) en rouge et Joueur 2 (droite) en bleu
- Système de service alternant tous les 2 points
- Indication visuelle du serveur actuel
- Rebond des balles avec accélération progressive
- Mode plein écran disponible (touche F)
- Menu pause accessible pendant la partie

### Système de bonus
Plusieurs bonus peuvent apparaître simultanément sur la table et se déplacer dans différentes directions:

1. **Force x2** (premier sprite)
   - Accélère la balle lors de la prochaine frappe
   - Effet immédiat, sans durée

2. **Ralentir adversaire** (deuxième sprite)
   - Ralentit la raquette adverse de 40%
   - Durée: 5 secondes

3. **Grande raquette** (troisième sprite)
   - Augmente la taille de votre raquette de 50%
   - Durée: 15 secondes

4. **Multi-balle** (quatrième sprite)
   - Génère jusqu'à deux balles supplémentaires
   - Les balles supplémentaires restent en jeu jusqu'à ce qu'un point soit marqué

### Boutique
- Personnalisez votre expérience de jeu avec la monnaie gagnée
- Différents skins pour la balle: normale, flamme, électrique, glace
- Designs de raquettes: classique, laser, feu, pixel
- Couleurs de fond: vert, bleu, nuit, futuriste
- Styles visuels: moderne, rétro, néon, cartoon

### Affichage du score
- Score central en haut de l'écran
- Affichage des bonus actifs
- Indication du nombre de points à atteindre

### Système de cagnotte
- Une cagnotte augmente de 100 euros à chaque nouvelle partie
- Visible sur les écrans de jeu et de fin de partie

### Écran de fin de partie
- Affichage du gagnant
- Score final
- Options pour recommencer une partie ou retourner au menu

## Structure du projet

```
pingpong/
├── README.md        # Ce fichier
├── src/
│   ├── main.py      # Code principal du jeu
│   └── assets/
│       └── bonus.png # Image contenant les sprites de bonus
``` 
