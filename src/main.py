import sys
import pygame
from math import cos, sin, pi
from pygame.locals import QUIT
from random import choice, randint, uniform

pygame.init()
largeur, hauteur = 800, 600
couleur_fond = (0, 100, 0)  # Vert foncé pour la table
mon_ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption('Ping Pong Game!')

# Chargement de l'image de bonus
image_bonus = pygame.image.load('src/assets/bonus.png')
# L'image contient 3 bonus côte à côte, on va la découper en 3 parties
largeur_bonus = image_bonus.get_width() // 3
sprites_bonus = [
    image_bonus.subsurface((i * largeur_bonus, 0, largeur_bonus, image_bonus.get_height()))
    for i in range(3)
]
# Redimensionnement des sprites de bonus
for i in range(len(sprites_bonus)):
    sprites_bonus[i] = pygame.transform.scale(sprites_bonus[i], (70, 50))

# États du jeu
ETAT_ACCUEIL = 0
ETAT_JEU = 1
ETAT_FIN_PARTIE = 2
etat_actuel = ETAT_ACCUEIL

# Points maximum pour la partie
points_max = 5  # Par défaut

# Polices
ma_police = pygame.font.SysFont('arial', 30)
police_titre = pygame.font.SysFont('arial', 50, bold=True)
police_menu = pygame.font.SysFont('arial', 36)

def creer_bouton(x, y, largeur, hauteur, texte, couleur=(200, 200, 200), couleur_survol=(150, 150, 150)):
    """Crée et retourne un dictionnaire représentant un bouton"""
    return {
        'rect': pygame.Rect(x, y, largeur, hauteur),
        'texte': texte,
        'couleur': couleur,
        'couleur_survol': couleur_survol,
        'est_survole': False
    }

def dessiner_bouton(bouton, surface):
    """Dessine un bouton sur la surface donnée"""
    couleur_actuelle = bouton['couleur_survol'] if bouton['est_survole'] else bouton['couleur']
    pygame.draw.rect(surface, couleur_actuelle, bouton['rect'])
    pygame.draw.rect(surface, (0, 0, 0), bouton['rect'], 2)  # Bordure
    
    texte_surface = police_menu.render(bouton['texte'], True, (0, 0, 0))
    texte_rect = texte_surface.get_rect(center=bouton['rect'].center)
    surface.blit(texte_surface, texte_rect)

def verifier_survol_bouton(bouton, pos):
    """Vérifie si la souris survole un bouton et met à jour son état"""
    bouton['est_survole'] = bouton['rect'].collidepoint(pos)
    return bouton['est_survole']

def est_bouton_clique(bouton, evenement):
    """Vérifie si un bouton est cliqué"""
    if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
        return bouton['est_survole']
    return False

# Création des boutons du menu d'accueil
bouton_5_points = creer_bouton(largeur//2 - 100, hauteur//2 - 50, 200, 50, "5 Points")
bouton_11_points = creer_bouton(largeur//2 - 100, hauteur//2 + 20, 200, 50, "11 Points")
bouton_21_points = creer_bouton(largeur//2 - 100, hauteur//2 + 90, 200, 50, "21 Points")
bouton_start = creer_bouton(largeur//2 - 100, hauteur//2 + 180, 200, 60, "START", (100, 200, 100), (50, 150, 50))

# Création des boutons de l'écran de fin de partie
bouton_recommencer = creer_bouton(largeur//2 - 220, hauteur//2 + 100, 200, 60, "RESTART", (100, 200, 100), (50, 150, 50))
bouton_accueil = creer_bouton(largeur//2 + 20, hauteur//2 + 100, 200, 60, "ACCUEIL", (200, 100, 100), (150, 50, 50))

def creer_bonus():
    """Crée et retourne un dictionnaire représentant un bonus"""
    type_bonus = choice(['vitesse', 'ralentir adversaire', 'taille'])
    
    # Angle aléatoire pour le déplacement (en radians), mais avec un angle maximal limité
    # On limite l'angle entre -45° et 45° (±π/4 radians) par rapport à l'horizontale
    angle = uniform(-pi/4, pi/4)
    
    # On choisit aléatoirement une direction horizontale (gauche ou droite)
    direction_horizontale = choice([-1, 1])
    
    # Calcul de la direction avec l'angle limité
    direction = [direction_horizontale * cos(angle), sin(angle)]
    
    # Normalisation pour s'assurer que la vitesse est constante
    magnitude = (direction[0]**2 + direction[1]**2)**0.5
    direction = [direction[0]/magnitude, direction[1]/magnitude]
    
    # Sélection du sprite selon le type de bonus
    indice_sprite = 0  # Par défaut (Force x2)
    if type_bonus == 'vitesse':
        indice_sprite = 0  # Force x2
    elif type_bonus == 'ralentir adversaire':
        indice_sprite = 1  # Ralentir
    elif type_bonus == 'taille':
        indice_sprite = 2  # Grande raquette
    
    return {
        'type': type_bonus,
        'x': randint(50, largeur - 50),
        'y': randint(50, hauteur - 50),
        'rayon': 15,
        'actif': True,
        'dernier_touche': None,  # Pour suivre quelle raquette a touché le bonus
        'direction': direction,
        'vitesse': 3,
        'indice_sprite': indice_sprite
    }

def reinitialiser_jeu():
    global pos_x, pos_y, sens, rayon, pas, pas_raquette, vitesse
    global raq_g_y, raq_d_y, partie_terminee, gagnant
    global score_gauche, score_droite, bonus, compteur_bonus
    global pas_raquette_gauche, pas_raquette_droite, bonus_actif_joueur, force_x2_actif
    global serveur_actuel, services_restants, changement_service
    global h_g, h_d

    # Réinitialisation des bonus et de leurs effets
    # Restaurer la vitesse de déplacement des raquettes à leur valeur par défaut
    pas_raquette_gauche = 8  # Utiliser la même valeur que pas_raquette définie plus bas
    pas_raquette_droite = 8
    
    # Restaurer la taille normale des raquettes
    h_g = 100
    h_d = 100
    
    # Annuler tous les bonus actifs
    bonus = None
    compteur_bonus = 0
    bonus_actif_joueur = None
    force_x2_actif = None

    pos_x = largeur // 2
    pos_y = hauteur // 2
    
    # Logique de service
    if changement_service:
        # Après avoir marqué un point, on applique vraiment le changement de serveur
        if serveur_actuel == 'gauche':
            serveur_actuel = 'droite'
        else:
            serveur_actuel = 'gauche'
        services_restants = 2  # Chaque joueur sert 2 fois, sauf le premier service du jeu
        changement_service = False
    
    # Mise à jour de la direction initiale en fonction du serveur
    if serveur_actuel == 'gauche':
        direction = 1  # La balle va vers la droite
    else:
        direction = -1  # La balle va vers la gauche
    
    # Réduire le nombre de services restants
    services_restants -= 1
    if services_restants <= 0:
        changement_service = True
    
    # Utilisation directe de sin/cos pour les angles (30°, 36°, 45°, 60°)
    angles = [(0.866, 0.5), (0.809, 0.587), (0.707, 0.707), (0.5, 0.866)]
    # Ajout des angles négatifs
    angles.extend([(x, -y) for x, y in angles])
    cos_val, sin_val = choice(angles)
    sens = [direction * cos_val, sin_val]
    
    rayon = 15
    pas = 5
    pas_raquette = 8
    vitesse = 1
    raq_g_y = hauteur // 2 - 50
    raq_d_y = hauteur // 2 - 50
    partie_terminee = False
    gagnant = None


# Initialisation des variables
score_gauche = 0
score_droite = 0

# Raquettes
l_g = 10  # largeur gauche
h_g = 100  # hauteur gauche
raq_g_x = 20
l_d = 10  # largeur droite
h_d = 100  # hauteur droite
raq_d_x = largeur - 30

# Vitesses de déplacement des raquettes
pas_raquette_gauche = 8
pas_raquette_droite = 8

# Service
serveur_actuel = 'gauche'  # Le joueur qui commence (peut être 'gauche' ou 'droite')
services_restants = 1  # Le premier serveur ne sert qu'une fois
changement_service = False  # Indique si on vient de changer de serveur

# Bonus
bonus = None
bonus_actif_joueur = None
force_x2_actif = None
compteur_bonus = 0

# Contrôles
mouv_haut_g = mouv_bas_g = mouv_haut_d = mouv_bas_d = False
partie_terminee = False

# Police
ma_police = pygame.font.SysFont('arial', 30)
texte_gauche = ma_police.render("Le Joueur Gauche a gagné!", True,
                              (255, 255, 255))
texte_droit = ma_police.render("Le Joueur Droit a gagné!", True, (255, 255, 255))

# Initialisation du jeu
reinitialiser_jeu()
horloge = pygame.time.Clock()

def afficher_ecran_accueil():
    mon_ecran.fill((30, 30, 30))
    
    titre = police_titre.render("PING PONG GAME", True, (255, 255, 255))
    mon_ecran.blit(titre, (largeur//2 - titre.get_width()//2, 100))
    
    sous_titre = ma_police.render("Sélectionnez le nombre de points pour gagner:", True, (200, 200, 200))
    mon_ecran.blit(sous_titre, (largeur//2 - sous_titre.get_width()//2, hauteur//2 - 120))
    
    # Indicateur de sélection
    if points_max == 5:
        pygame.draw.circle(mon_ecran, (255, 255, 0), (bouton_5_points['rect'].x - 20, bouton_5_points['rect'].centery), 10)
    elif points_max == 11:
        pygame.draw.circle(mon_ecran, (255, 255, 0), (bouton_11_points['rect'].x - 20, bouton_11_points['rect'].centery), 10)
    elif points_max == 21:
        pygame.draw.circle(mon_ecran, (255, 255, 0), (bouton_21_points['rect'].x - 20, bouton_21_points['rect'].centery), 10)
    
    # Affichage des boutons
    dessiner_bouton(bouton_5_points, mon_ecran)
    dessiner_bouton(bouton_11_points, mon_ecran)
    dessiner_bouton(bouton_21_points, mon_ecran)
    dessiner_bouton(bouton_start, mon_ecran)
    
    # Contrôles
    controles = ma_police.render("Contrôles: Z/S (Gauche) et Flèches (Droite)", True, (200, 200, 200))
    mon_ecran.blit(controles, (largeur//2 - controles.get_width()//2, hauteur - 50))

def afficher_ecran_fin_partie():
    mon_ecran.fill((30, 30, 30))
    
    if gagnant == "gauche":
        titre = police_titre.render("Joueur 1 a gagné!", True, (200, 100, 100))
    else:
        titre = police_titre.render("Joueur 2 a gagné!", True, (100, 100, 200))
    
    mon_ecran.blit(titre, (largeur//2 - titre.get_width()//2, 150))
    
    score_final = police_titre.render(f"{score_gauche} - {score_droite}", True, (255, 255, 255))
    mon_ecran.blit(score_final, (largeur//2 - score_final.get_width()//2, hauteur//2 - 50))
    
    dessiner_bouton(bouton_recommencer, mon_ecran)
    dessiner_bouton(bouton_accueil, mon_ecran)

while True:
    horloge.tick(60)  # Limite à 60 FPS
    
    # Gestion des événements
    for evenement in pygame.event.get():
        if evenement.type == QUIT:
            pygame.quit()
            sys.exit()
            
        position_souris = pygame.mouse.get_pos()
        
        if etat_actuel == ETAT_ACCUEIL:
            # Mise à jour de l'état des boutons
            verifier_survol_bouton(bouton_5_points, position_souris)
            verifier_survol_bouton(bouton_11_points, position_souris)
            verifier_survol_bouton(bouton_21_points, position_souris)
            verifier_survol_bouton(bouton_start, position_souris)
            
            if est_bouton_clique(bouton_5_points, evenement):
                points_max = 5
            elif est_bouton_clique(bouton_11_points, evenement):
                points_max = 11
            elif est_bouton_clique(bouton_21_points, evenement):
                points_max = 21
            elif est_bouton_clique(bouton_start, evenement):
                etat_actuel = ETAT_JEU
                reinitialiser_jeu()
                score_gauche = 0
                score_droite = 0
                
        elif etat_actuel == ETAT_FIN_PARTIE:
            # Mise à jour de l'état des boutons
            verifier_survol_bouton(bouton_recommencer, position_souris)
            verifier_survol_bouton(bouton_accueil, position_souris)
            
            if est_bouton_clique(bouton_recommencer, evenement):
                etat_actuel = ETAT_JEU
                reinitialiser_jeu()
                score_gauche = 0
                score_droite = 0
            elif est_bouton_clique(bouton_accueil, evenement):
                etat_actuel = ETAT_ACCUEIL
                
        elif etat_actuel == ETAT_JEU:
            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_s:  # S pour descendre à gauche
                    mouv_bas_g = True
                elif evenement.key == pygame.K_z:  # Z pour monter à gauche
                    mouv_haut_g = True
                elif evenement.key == pygame.K_DOWN:
                    mouv_bas_d = True
                elif evenement.key == pygame.K_UP:
                    mouv_haut_d = True
            elif evenement.type == pygame.KEYUP:
                if evenement.key == pygame.K_s:
                    mouv_bas_g = False
                elif evenement.key == pygame.K_z:
                    mouv_haut_g = False
                elif evenement.key == pygame.K_DOWN:
                    mouv_bas_d = False
                elif evenement.key == pygame.K_UP:
                    mouv_haut_d = False
    
    # Affichage en fonction de l'état
    if etat_actuel == ETAT_ACCUEIL:
        afficher_ecran_accueil()
    elif etat_actuel == ETAT_FIN_PARTIE:
        afficher_ecran_fin_partie()
    elif etat_actuel == ETAT_JEU:
        mon_ecran.fill(couleur_fond)

        # Déplacement des raquettes
        if mouv_haut_g and raq_g_y > 0:
            raq_g_y -= pas_raquette_gauche
        if mouv_bas_g and raq_g_y < hauteur - h_g:
            raq_g_y += pas_raquette_gauche
        if mouv_haut_d and raq_d_y > 0:
            raq_d_y -= pas_raquette_droite
        if mouv_bas_d and raq_d_y < hauteur - h_d:
            raq_d_y += pas_raquette_droite

        # Gestion des bonus
        if bonus is None and randint(0, 200) == 0:  # Chance d'apparition d'un bonus
            bonus = creer_bonus()

        if bonus and bonus['actif']:
            # Déplacement du bonus
            bonus['x'] += bonus['direction'][0] * bonus['vitesse']
            bonus['y'] += bonus['direction'][1] * bonus['vitesse']
            
            # Rebond sur les bords
            if bonus['x'] - bonus['rayon'] <= 0 or bonus['x'] + bonus['rayon'] >= largeur:
                bonus['direction'][0] *= -1
            if bonus['y'] - bonus['rayon'] <= 0 or bonus['y'] + bonus['rayon'] >= hauteur:
                bonus['direction'][1] *= -1
            
            # Collision avec les raquettes gauche
            if (raq_g_x <= bonus['x'] - bonus['rayon'] <= raq_g_x + l_g and 
                raq_g_y <= bonus['y'] <= raq_g_y + h_g):
                bonus['actif'] = False
                bonus['dernier_touche'] = 'gauche'
                
                if bonus['type'] == 'vitesse':
                    # Force x2 - sera appliqué au prochain coup
                    force_x2_actif = 'gauche'
                    # Pas de timer pour ce bonus, il sera désactivé après utilisation
                    bonus_actif_joueur = 'gauche'
                elif bonus['type'] == 'ralentir adversaire':
                    # Ralentir la raquette adverse pendant 5 secondes
                    # Si la raquette gauche l'attrape, on ralentit la raquette droite
                    pas_raquette_droite = pas_raquette * 0.6
                    compteur_bonus = 5 * 60  # 5 secondes à 60 FPS
                    bonus_actif_joueur = 'gauche'
                elif bonus['type'] == 'taille':
                    # Agrandir la raquette pendant 15 secondes
                    h_g = int(h_g * 1.5)
                    compteur_bonus = 15 * 60  # 15 secondes à 60 FPS
                    bonus_actif_joueur = 'gauche'
            
            # Collision avec les raquettes droite
            elif (raq_d_x <= bonus['x'] + bonus['rayon'] <= raq_d_x + l_d and 
                  raq_d_y <= bonus['y'] <= raq_d_y + h_d):
                bonus['actif'] = False
                bonus['dernier_touche'] = 'droite'
                
                if bonus['type'] == 'vitesse':
                    # Force x2 - sera appliqué au prochain coup
                    force_x2_actif = 'droite'
                    # Pas de timer pour ce bonus, il sera désactivé après utilisation
                    bonus_actif_joueur = 'droite'
                elif bonus['type'] == 'ralentir adversaire':
                    # Ralentir la raquette adverse pendant 5 secondes
                    # Si la raquette droite l'attrape, on ralentit la raquette gauche
                    pas_raquette_gauche = pas_raquette * 0.6
                    compteur_bonus = 5 * 60  # 5 secondes à 60 FPS
                    bonus_actif_joueur = 'droite'
                elif bonus['type'] == 'taille':
                    # Agrandir la raquette pendant 15 secondes
                    h_d = int(h_d * 1.5)
                    compteur_bonus = 15 * 60  # 15 secondes à 60 FPS
                    bonus_actif_joueur = 'droite'

        if compteur_bonus > 0:
            compteur_bonus -= 1
            if compteur_bonus == 0:  # Fin du bonus
                if bonus and bonus['type'] == 'ralentir adversaire':
                    # Restaurer la vitesse de déplacement des raquettes
                    pas_raquette_gauche = pas_raquette
                    pas_raquette_droite = pas_raquette
                elif bonus and bonus['type'] == 'taille':
                    # Restaurer la taille des raquettes
                    if bonus['dernier_touche'] == 'gauche':
                        h_g = int(h_g / 1.5)
                    else:
                        h_d = int(h_d / 1.5)
                bonus = None
                bonus_actif_joueur = None

        # Déplacement de la balle
        pos_x += pas * sens[0] * vitesse
        pos_y += pas * sens[1] * vitesse

        # Collisions avec les raquettes
        if (raq_g_x <= pos_x - rayon <= raq_g_x + l_g
                and raq_g_y <= pos_y <= raq_g_y + h_g):
            if sens[0] < 0:  # Ne rebondit que si la balle va vers la raquette
                sens[0] *= -1
                # Appliquer Force x2 si actif
                if force_x2_actif == 'gauche':
                    vitesse *= 2
                    force_x2_actif = None
                    # Si le joueur a utilisé son bonus Force x2, on le désactive
                    if bonus_actif_joueur == 'gauche' and (not bonus or bonus['type'] == 'vitesse'):
                        bonus_actif_joueur = None
                        bonus = None
                else:
                    # Si l'adversaire rattrape une balle accélérée par Force x2
                    if vitesse > 1.5:
                        vitesse /= 2
                    else:
                        vitesse = min(vitesse * 1.1, 2.0)
        elif (raq_d_x <= pos_x + rayon <= raq_d_x + l_d
              and raq_d_y <= pos_y <= raq_d_y + h_d):
            if sens[0] > 0:  # Ne rebondit que si la balle va vers la raquette
                sens[0] *= -1
                # Appliquer Force x2 si actif
                if force_x2_actif == 'droite':
                    vitesse *= 2
                    force_x2_actif = None
                    # Si le joueur a utilisé son bonus Force x2, on le désactive
                    if bonus_actif_joueur == 'droite' and (not bonus or bonus['type'] == 'vitesse'):
                        bonus_actif_joueur = None
                        bonus = None
                else:
                    # Si l'adversaire rattrape une balle accélérée par Force x2
                    if vitesse > 1.5:
                        vitesse /= 2
                    else:
                        vitesse = min(vitesse * 1.1, 2.0)

        # Collisions avec les murs
        if pos_y - rayon <= 0 or pos_y + rayon >= hauteur:
            sens[1] *= -1

        # Points
        if pos_x - rayon <= 0:
            score_droite += 1
            if score_droite >= points_max:
                gagnant = "droite"
                etat_actuel = ETAT_FIN_PARTIE
            else:
                reinitialiser_jeu()
        elif pos_x + rayon >= largeur:
            score_gauche += 1
            if score_gauche >= points_max:
                gagnant = "gauche"
                etat_actuel = ETAT_FIN_PARTIE
            else:
                reinitialiser_jeu()

        # Affichage
        pygame.draw.line(mon_ecran, (255, 255, 255), (largeur // 2, 0),
                         (largeur // 2, hauteur), 2)
        pygame.draw.rect(mon_ecran, (255, 255, 255), (0, 0, largeur, hauteur), 5)

        pygame.draw.rect(mon_ecran, (200, 100, 100),
                         (raq_g_x, raq_g_y, l_g, h_g))  # Rouge pastel
        pygame.draw.rect(mon_ecran, (100, 100, 200),
                         (raq_d_x, raq_d_y, l_d, h_d))  # Bleu pastel
        pygame.draw.circle(mon_ecran, (255, 255, 255), (int(pos_x), int(pos_y)),
                           rayon)

        if bonus and bonus['actif']:
            # Utiliser l'image du bonus au lieu d'un simple cercle
            sprite = sprites_bonus[bonus['indice_sprite']]
            sprite_rect = sprite.get_rect(center=(int(bonus['x']), int(bonus['y'])))
            mon_ecran.blit(sprite, sprite_rect)

        # Affichage du score
        texte_score = ma_police.render(f"{score_gauche} - {score_droite}", True,
                                      (255, 255, 255))
        mon_ecran.blit(texte_score, (largeur // 2 - texte_score.get_width() // 2, 20))
        
        # Affichage du nombre de points max
        texte_points_max = ma_police.render(f"Objectif: {points_max} points", True, (200, 200, 200))
        mon_ecran.blit(texte_points_max, (largeur // 2 - texte_points_max.get_width() // 2, hauteur - 30))
        
        # Affichage du serveur actuel
        if serveur_actuel == 'gauche':
            texte_serveur = ma_police.render("Service", True, (255, 200, 0))
            mon_ecran.blit(texte_serveur, (20, hauteur - 40))
        else:
            texte_serveur = ma_police.render("Service", True, (255, 200, 0))
            mon_ecran.blit(texte_serveur, (largeur - texte_serveur.get_width() - 20, hauteur - 40))
        
        # Affichage du nom du bonus actif
        if bonus_actif_joueur:
            nom_bonus = ""
            if force_x2_actif:
                nom_bonus = "Force x2"
            elif bonus and bonus['type'] == 'ralentir adversaire':
                nom_bonus = "Ralentir adversaire"
            elif bonus and bonus['type'] == 'taille':
                nom_bonus = "Grande raquette"
                
            texte_bonus = ma_police.render(nom_bonus, True, (255, 255, 0))
            if bonus_actif_joueur == 'gauche':
                mon_ecran.blit(texte_bonus, (largeur // 4 - texte_bonus.get_width() // 2, 20))
            else:
                mon_ecran.blit(texte_bonus, (3 * largeur // 4 - texte_bonus.get_width() // 2, 20))
    
    pygame.display.flip()
