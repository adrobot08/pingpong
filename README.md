# Jeu de Ping Pong

Un jeu de ping pong dynamique avec bonus et système de service, développé avec Pygame.

## Fonctionnalités

### Écran d'accueil
- Sélection du nombre de points à atteindre pour gagner: 5, 11 ou 21 points
- Bouton START pour lancer la partie
- Affichage des contrôles

### Système de jeu
- Table de jeu verte avec ligne centrale et bordure
- Joueur 1 (gauche) en rouge et Joueur 2 (droite) en bleu
- Système de service alternant tous les 2 points
- Indication visuelle du serveur actuel
- Rebond des balles avec accélération progressive

### Système de bonus
Trois types de bonus apparaissent aléatoirement sur la table:

1. **Force x2** (premier sprite)
   - Accélère la balle lors de la prochaine frappe
   - Effet immédiat, sans durée

2. **Ralentir adversaire** (deuxième sprite)
   - Ralentit la raquette adverse de 40%
   - Durée: 5 secondes

3. **Grande raquette** (troisième sprite)
   - Augmente la taille de votre raquette de 50%
   - Durée: 15 secondes

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
│       └── bonus.png # Image contenant les 3 sprites de bonus
``` 