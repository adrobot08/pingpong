import sys
import pygame
from math import cos, sin, pi
from pygame.locals import QUIT
from random import choice, randint, uniform
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 0, 255)
GRIS = (128, 128, 128)

skin_selectionne = {
    "balle": "normale",      # "normale", "flamme", "electrique", "glace"
    "raquette": "classique", # "classique", "laser", "feu", "pixel"
    "fond": "vert",          # "vert", "bleu", "nuit", "futur"
    "style": "moderne"       # "moderne", "retro", "neon", "cartoon"
}


monnaie = 300

pygame.init()
largeur, hauteur = 800, 600
couleur_fond = (0, 100, 0)  # Vert foncé pour la table
est_plein_ecran = False
mon_ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption('Ping Pong Game!')

def basculer_plein_ecran():
    global mon_ecran, largeur, hauteur, est_plein_ecran
    est_plein_ecran = not est_plein_ecran
    if est_plein_ecran:
        mon_ecran = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        largeur, hauteur = pygame.display.get_surface().get_size()
    else:
        largeur, hauteur = 800, 600
        mon_ecran = pygame.display.set_mode((largeur, hauteur))
    
    # Mise à jour des positions des boutons
    mettre_a_jour_positions_boutons()

# Fonction pour mettre à jour les positions des boutons en fonction de la taille de l'écran
def mettre_a_jour_positions_boutons():
    global bouton_5_points, bouton_11_points, bouton_21_points, bouton_start
    global bouton_commandes, bouton_quitter, bouton_boutique, bouton_pause, bouton_solo
    global bouton_recommencer, bouton_accueil
    
    # Menu principal
    bouton_5_points['rect'] = pygame.Rect(largeur//2 - 100, hauteur//2 - 50, 200, 50)
    bouton_11_points['rect'] = pygame.Rect(largeur//2 - 100, hauteur//2 + 20, 200, 50)
    bouton_21_points['rect'] = pygame.Rect(largeur//2 - 100, hauteur//2 + 90, 200, 50)
    bouton_start['rect'] = pygame.Rect(largeur//2 - 100, hauteur//2 + 150, 200, 60)
    bouton_solo['rect'] = pygame.Rect(largeur//2 - 100, hauteur//2 + 220, 200, 50)
    bouton_commandes['rect'] = pygame.Rect(20, hauteur - 80, 200, 50)
    bouton_quitter['rect'] = pygame.Rect(largeur - 200, hauteur - 80, 200, 60)
    bouton_boutique['rect'] = pygame.Rect(20, hauteur - 140, 200, 50)
    bouton_pause['rect'] = pygame.Rect(largeur - 50, 20, 30, 30)
    
    # Écran de fin de partie
    bouton_recommencer['rect'] = pygame.Rect(largeur//2 - 220, hauteur//2 + 100, 200, 60)
    bouton_accueil['rect'] = pygame.Rect(largeur//2 + 20, hauteur//2 + 100, 200, 60)

# Remplacement par l'utilisation de chemins relatifs robustes
son_achat = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "son_achat.wav"))
son_erreur = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "son_erreur.wav"))

# Chargement de l'image de bonus
image_bonus = pygame.image.load(os.path.join(ASSETS_DIR, "bonus.png"))
# L'image contient 4 bonus côte à côte
largeur_bonus = image_bonus.get_width() // 4
sprites_bonus = [
    image_bonus.subsurface((i * largeur_bonus, 0, largeur_bonus, image_bonus.get_height()))
    for i in range(4)
]
# Redimensionnement des sprites de bonus
for i in range(len(sprites_bonus)):
    sprites_bonus[i] = pygame.transform.scale(sprites_bonus[i], (70, 50))

# Liste pour stocker plusieurs bonus actifs
bonus_actifs = []
# Temps minimum entre deux générations de bonus (en frames)
delai_entre_bonus = 60  # environ 1 seconde à 60 FPS (au lieu de 2 secondes)
compteur_delai_bonus = 0
max_bonus_simultanes = 4  # Maximum de bonus qui peuvent être présents simultanément

# Variables pour la multi-balle
multi_balles = []
max_multi_balles = 2  # Nombre maximum de balles supplémentaires simultanées

# États du jeu
ETAT_ACCUEIL = 0
ETAT_JEU = 1
ETAT_FIN_PARTIE = 2
etat_actuel = ETAT_ACCUEIL

# Points maximum pour la partie
points_max = 5  # Par défaut

mode_solo = False

# Polices
ma_police = pygame.font.SysFont('arial', 30)
police_titre = pygame.font.SysFont('arial', 50, bold=True)
police_menu = pygame.font.SysFont('arial', 36)
police_bouton_commandes = pygame.font.SysFont('arial', 24)


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
    
    # Pour le bouton pause, on garde une police spéciale
    if bouton['texte'] == "⏸":
        texte_surface = pygame.font.SysFont('arial', 30).render(bouton['texte'], True, (0, 0, 0))
    # Police plus petite pour le bouton COMMANDES
    elif bouton['texte'] == "COMMANDES":
        texte_surface = pygame.font.SysFont('arial', 28).render(bouton['texte'], True, (0, 0, 0))
    else:
        # Pour tous les autres boutons, on utilise la même police
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
bouton_start = creer_bouton(largeur//2 - 100, hauteur//2 + 150, 200, 60, "START", (100, 200, 100), (50, 150, 50))
bouton_solo = creer_bouton(largeur//2 - 100, hauteur//2 + 220, 200, 50, "SOLO", (100, 200, 250), (50, 150, 200))
bouton_commandes = creer_bouton(20, hauteur - 80, 200, 50, "COMMANDES")
bouton_quitter = creer_bouton(largeur - 200, hauteur - 80, 200, 60, "QUITTER", couleur=(200, 80, 80), couleur_survol=(150, 50, 50))
bouton_boutique = creer_bouton(20, hauteur - 140, 200, 50, "BOUTIQUE", (100, 150, 255), (50, 100, 200))
bouton_pause = creer_bouton(largeur - 50, 20, 30, 30, "⏸", (200, 0, 0), (255, 50, 50))

 

# Création des boutons de l'écran de fin de partie
bouton_recommencer = creer_bouton(largeur//2 - 220, hauteur//2 + 100, 200, 60, "RESTART", (100, 200, 100), (50, 150, 50))
bouton_accueil = creer_bouton(largeur//2 + 20, hauteur//2 + 100, 200, 60, "ACCUEIL", (200, 100, 100), (150, 50, 50))

def creer_bonus():
    """Crée et retourne un dictionnaire représentant un bonus"""
    # Ajout du type multi-balle aux types possibles
    type_bonus = choice(['vitesse', 'ralentir adversaire', 'taille', 'multi-balle'])
    
    # Angle aléatoire pour le déplacement (en radians), mais avec un angle maximal limité
    # On permet désormais des angles plus variés
    angle = uniform(-pi/3, pi/3)  # Entre -60° et 60° au lieu de -45° et 45°
    
    # On choisit aléatoirement une direction horizontale (gauche ou droite)
    direction_horizontale = choice([-1, 1])
    
    # Calcul de la direction avec l'angle limité
    direction = [direction_horizontale * cos(angle), sin(angle)]
    
    # Normalisation pour s'assurer que la vitesse est constante
    magnitude = (direction[0]**2 + direction[1]**2)**0.5
    direction = [direction[0]/magnitude, direction[1]/magnitude]
    
    # Vitesse aléatoire pour plus de diversité
    vitesse_bonus = uniform(2.5, 4.5)  # Entre 2.5 et 4.5 au lieu de fixe à 3
    
    # Sélection du sprite selon le type de bonus
    indice_sprite = 0  # Par défaut (Force x2)
    if type_bonus == 'vitesse':
        indice_sprite = 0  # Force x2
    elif type_bonus == 'ralentir adversaire':
        indice_sprite = 1  # Ralentir
    elif type_bonus == 'taille':
        indice_sprite = 2  # Grande raquette
    elif type_bonus == 'multi-balle':
        indice_sprite = 3  # Multi-balle (sprite dédié)
    
    return {
        'type': type_bonus,
        'x': randint(largeur//4, 3*largeur//4),  # Positionnement plus au centre du terrain
        'y': randint(50, hauteur - 50),
        'rayon': 15,
        'actif': True,
        'dernier_touche': None,  # Pour suivre quelle raquette a touché le bonus
        'direction': direction,
        'vitesse': vitesse_bonus,
        'indice_sprite': indice_sprite,
        'compteur': 0,  # Compteur individuel pour chaque bonus
        'duree': 0,     # Durée de l'effet (sera définie lors de l'activation)
        'joueur': None, # Joueur qui bénéficie de l'effet
    }

def creer_multi_balle():
    """Crée une balle supplémentaire avec des propriétés aléatoires"""
    # Angle aléatoire pour le déplacement
    angle = uniform(0, 2*pi)
    
    # Direction de déplacement
    sens_x = cos(angle)
    sens_y = sin(angle)
    
    # Normalisation
    magnitude = (sens_x**2 + sens_y**2)**0.5
    sens_x /= magnitude
    sens_y /= magnitude
    
    return {
        'pos_x': largeur // 2,
        'pos_y': hauteur // 2,
        'sens': [sens_x, sens_y],
        'rayon': rayon,
        'vitesse': uniform(0.8, 1.2) * pas,  # Vitesse légèrement variée
        'duree': 15 * 60,  # 15 secondes à 60 FPS
        'couleur': (randint(150, 255), randint(150, 255), randint(150, 255))  # Couleur aléatoire
    }

def reinitialiser_jeu():
    global pos_x, pos_y, sens, rayon, pas, pas_raquette, vitesse
    global raq_g_y, raq_d_y, partie_terminee, gagnant
    global score_gauche, score_droite, bonus_actifs, compteur_delai_bonus
    global pas_raquette_gauche, pas_raquette_droite, bonus_actif_joueur, force_x2_actif
    global serveur_actuel, services_restants, changement_service
    global h_g, h_d, multi_balles

    # Réinitialisation des bonus et de leurs effets
    # Restaurer la vitesse de déplacement des raquettes à leur valeur par défaut
    pas_raquette_gauche = 8  # Utiliser la même valeur que pas_raquette définie plus bas
    pas_raquette_droite = 8
    
    # Restaurer la taille normale des raquettes
    h_g = 100
    h_d = 100
    
    # Annuler tous les bonus actifs
    bonus_actifs = []
    compteur_delai_bonus = 0
    bonus_actif_joueur = None
    force_x2_actif = None

    # Vider les multi-balles
    multi_balles = []

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

faire_decompte = False

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

def afficher_menu_pause():
    en_pause = True
    bouton_reprendre = creer_bouton(largeur//2 - 125, hauteur//2 - 50, 250, 50, "REPRENDRE", (100, 200, 100), (50, 150, 50))
    bouton_quit_pause = creer_bouton(largeur//2 - 100, hauteur//2 + 20, 200, 50, "ACCUEIL", (200, 100, 100), (150, 50, 50))

    while en_pause:
        mon_ecran.fill((30, 30, 30))
        
        titre = police_titre.render("Pause", True, (255, 255, 255))
        mon_ecran.blit(titre, titre.get_rect(center=(largeur//2, 150)))
        
        dessiner_bouton(bouton_reprendre, mon_ecran)
        dessiner_bouton(bouton_quit_pause, mon_ecran)
        pygame.display.flip()

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            pos = pygame.mouse.get_pos()
            verifier_survol_bouton(bouton_reprendre, pos)
            verifier_survol_bouton(bouton_quit_pause, pos)

            if est_bouton_clique(bouton_reprendre, evenement):
                en_pause = False
                pygame.display.flip()
                global faire_decompte
                faire_decompte = True
            elif est_bouton_clique(bouton_quit_pause, evenement):
                global etat_actuel
                etat_actuel = ETAT_ACCUEIL
                en_pause = False

def afficher_ecran_accueil():
    mon_ecran.fill((30, 30, 30))
    
    # Titre centré horizontalement et positionné relativement à la hauteur
    titre = police_titre.render("PING PONG GAME", True, (255, 255, 255))
    position_titre_x = largeur // 2 - titre.get_width() // 2
    position_titre_y = hauteur * 0.15  # 15% de la hauteur de l'écran
    mon_ecran.blit(titre, (position_titre_x, position_titre_y))
    
    # Sous-titre centré horizontalement et positionné relativement
    sous_titre = ma_police.render("Sélectionnez le nombre de points pour gagner:", True, (200, 200, 200))
    position_sous_titre_x = largeur // 2 - sous_titre.get_width() // 2
    position_sous_titre_y = hauteur * 0.30  # 30% de la hauteur de l'écran
    mon_ecran.blit(sous_titre, (position_sous_titre_x, position_sous_titre_y))
    
    # Indicateur de sélection, s'aligne dynamiquement avec les boutons
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
    dessiner_bouton(bouton_commandes, mon_ecran)
    dessiner_bouton(bouton_quitter, mon_ecran)
    dessiner_bouton(bouton_boutique, mon_ecran)
    dessiner_bouton(bouton_solo, mon_ecran)


def decompte_reprise():
    for i in range(3, 0, -1):
        afficher_table_jeu()  # Redessine l'état actuel de la partie
        texte = police_titre.render(str(i), True, (255, 255, 0))
        rect = texte.get_rect(center=(largeur // 2, hauteur // 2))
        mon_ecran.blit(texte, rect)
        pygame.display.flip()
        pygame.time.delay(1000)

def afficher_table_jeu():
    # Couleur de fond selon skin sélectionné
    if skin_selectionne["fond"] == "bleu":
        couleur_fond = (0, 0, 80)
    elif skin_selectionne["fond"] == "nuit":
        couleur_fond = (10, 10, 30)
    elif skin_selectionne["fond"] == "futur":
        couleur_fond = (10, 150, 200)  # Couleur bleu "futuriste" plus vive
    else:
        couleur_fond = (0, 100, 0)
    mon_ecran.fill(couleur_fond)

    pygame.draw.line(mon_ecran, BLANC, (largeur // 2, 0), (largeur // 2, hauteur), 2)
    pygame.draw.rect(mon_ecran, BLANC, (0, 0, largeur, hauteur), 5)

    # Raquettes
    if skin_selectionne["raquette"] == "laser":
        pygame.draw.rect(mon_ecran, (255, 0, 255), (raq_g_x, raq_g_y, l_g, h_g))
        pygame.draw.rect(mon_ecran, (0, 255, 255), (raq_d_x, raq_d_y, l_d, h_d))
    elif skin_selectionne["raquette"] == "feu":
        pygame.draw.rect(mon_ecran, (255, 69, 0), (raq_g_x, raq_g_y, l_g, h_g))
        pygame.draw.rect(mon_ecran, (255, 140, 0), (raq_d_x, raq_d_y, l_d, h_d))
    elif skin_selectionne["raquette"] == "pixel":
        pygame.draw.rect(mon_ecran, (100, 100, 100), (raq_g_x, raq_g_y, l_g, h_g))
        pygame.draw.rect(mon_ecran, (150, 150, 150), (raq_d_x, raq_d_y, l_d, h_d))
    else:
        pygame.draw.rect(mon_ecran, (200, 100, 100), (raq_g_x, raq_g_y, l_g, h_g))
        pygame.draw.rect(mon_ecran, (100, 100, 200), (raq_d_x, raq_d_y, l_d, h_d))

    # Balle
    if skin_selectionne["balle"] == "flamme":
        pygame.draw.circle(mon_ecran, (255, 140, 0), (int(pos_x), int(pos_y)), rayon + 3)
        pygame.draw.circle(mon_ecran, (255, 69, 0), (int(pos_x), int(pos_y)), rayon)
        pygame.draw.circle(mon_ecran, (255, 255, 0), (int(pos_x), int(pos_y)), rayon // 2)
    elif skin_selectionne["balle"] == "electrique":
        pygame.draw.circle(mon_ecran, (0, 255, 255), (int(pos_x), int(pos_y)), rayon + 3)
        pygame.draw.circle(mon_ecran, (0, 200, 255), (int(pos_x), int(pos_y)), rayon)
    elif skin_selectionne["balle"] == "glace":
        pygame.draw.circle(mon_ecran, (200, 240, 255), (int(pos_x), int(pos_y)), rayon)
        pygame.draw.circle(mon_ecran, (180, 220, 255), (int(pos_x), int(pos_y)), rayon - 3)
    else:
        pygame.draw.circle(mon_ecran, BLANC, (int(pos_x), int(pos_y)), rayon)
        
    # Dessiner les multi-balles
    for balle in multi_balles:
        pygame.draw.circle(mon_ecran, balle['couleur'], (int(balle['pos_x']), int(balle['pos_y'])), balle['rayon'])

    # Afficher tous les bonus actifs
    for bonus in bonus_actifs:
        if bonus['actif']:
            sprite = sprites_bonus[bonus['indice_sprite']]
            sprite_rect = sprite.get_rect(center=(int(bonus['x']), int(bonus['y'])))
            mon_ecran.blit(sprite, sprite_rect)

    # Score
    texte_score = ma_police.render(f"{score_gauche} - {score_droite}", True, BLANC)
    mon_ecran.blit(texte_score, (largeur // 2 - texte_score.get_width() // 2, 20))

    # Points max
    texte_points_max = ma_police.render(f"Objectif: {points_max} points", True, (200, 200, 200))
    mon_ecran.blit(texte_points_max, (largeur // 2 - texte_points_max.get_width() // 2, hauteur - 30))

    # Serveur
    texte_serveur = ma_police.render("Service", True, (255, 200, 0))
    if serveur_actuel == 'gauche':
        mon_ecran.blit(texte_serveur, (20, hauteur - 40))
    else:
        mon_ecran.blit(texte_serveur, (largeur - texte_serveur.get_width() - 20, hauteur - 40))

    # Bonus actifs pour chaque joueur
    bonus_gauche = [b for b in bonus_actifs if not b['actif'] and b['joueur'] == 'gauche' and b['compteur'] > 0]
    bonus_droite = [b for b in bonus_actifs if not b['actif'] and b['joueur'] == 'droite' and b['compteur'] > 0]
    
    # Affichage des bonus actifs pour le joueur gauche
    y_offset = 20
    for bonus in bonus_gauche:
        nom_bonus = ""
        if bonus['type'] == 'vitesse' and force_x2_actif == 'gauche':
            nom_bonus = "Force x2"
        elif bonus['type'] == 'ralentir adversaire':
            nom_bonus = "Ralentir adversaire"
        elif bonus['type'] == 'taille':
            nom_bonus = "Grande raquette"
        elif bonus['type'] == 'multi-balle':
            nom_bonus = "Multi-balle"
            
        if nom_bonus:
            texte_bonus = ma_police.render(nom_bonus, True, (255, 255, 0))
            mon_ecran.blit(texte_bonus, (largeur // 4 - texte_bonus.get_width() // 2, y_offset))
            y_offset += 30
    
    # Affichage des bonus actifs pour le joueur droit
    y_offset = 20
    for bonus in bonus_droite:
        nom_bonus = ""
        if bonus['type'] == 'vitesse' and force_x2_actif == 'droite':
            nom_bonus = "Force x2"
        elif bonus['type'] == 'ralentir adversaire':
            nom_bonus = "Ralentir adversaire"
        elif bonus['type'] == 'taille':
            nom_bonus = "Grande raquette"
        elif bonus['type'] == 'multi-balle':
            nom_bonus = "Multi-balle"
            
        if nom_bonus:
            texte_bonus = ma_police.render(nom_bonus, True, (255, 255, 0))
            mon_ecran.blit(texte_bonus, (3 * largeur // 4 - texte_bonus.get_width() // 2, y_offset))
            y_offset += 30
    
    # Afficher le nombre de balles en jeu
    if len(multi_balles) > 0:
        texte_balles = ma_police.render(f"Balles: {len(multi_balles) + 1}", True, (255, 200, 100))
        mon_ecran.blit(texte_balles, (largeur // 2 - texte_balles.get_width() // 2, 60))

def afficher_boutique():
    global skin_selectionne, monnaie

    articles = [
        {"nom": "fond bleu", "type": "fond", "valeur": "bleu", "prix": 100},
        {"nom": "raquette laser", "type": "raquette", "valeur": "laser", "prix": 120},
        {"nom": "balle flamme", "type": "balle", "valeur": "flamme", "prix": 90},
        {"nom": "style retro", "type": "style", "valeur": "retro", "prix": 80},
        {"nom": "balle electrique", "type": "balle", "valeur": "electrique", "prix": 150},
        {"nom": "balle de glace", "type": "balle", "valeur": "glace", "prix": 140},
        {"nom": "raquette de feu", "type": "raquette", "valeur": "feu", "prix": 130},
        {"nom": "raquette pixel", "type": "raquette", "valeur": "pixel", "prix": 110},
        {"nom": "fond nuit", "type": "fond", "valeur": "nuit", "prix": 100},
        {"nom": "fond futuriste", "type": "fond", "valeur": "futur", "prix": 160},
        {"nom": "style neon", "type": "style", "valeur": "neon", "prix": 120},
        {"nom": "style cartoon", "type": "style", "valeur": "cartoon", "prix": 100},
    ]

    largeur_carte = 300
    hauteur_carte = 100
    espacement = 20
    start_y = 150
    scroll_y = 0
    vitesse_scroll = 20
    article_en_apercu = None
    articles_achetes = set([k + "_" + v for k, v in skin_selectionne.items()])
    
    # Liste des rectangles pour chaque article (pour faciliter la détection des clics)
    rectangles_articles = []

    def dessiner_article(surface, article, x, y):
        rect = pygame.Rect(x, y, largeur_carte, hauteur_carte)
        pygame.draw.rect(surface, (50, 50, 120), rect)
        pygame.draw.rect(surface, BLANC, rect, 3)
        nom = ma_police.render(article["nom"], True, BLANC)
        prix = ma_police.render(f"Prix: {article['prix']} €", True, (255, 215, 0))
        surface.blit(nom, (x + 10, y + 10))
        surface.blit(prix, (x + 10, y + 50))
        if skin_selectionne[article["type"]] == article["valeur"]:
            check = ma_police.render("Équipé", True, (0, 255, 0))
            surface.blit(check, (x + largeur_carte - 110, y + 35))

    def dessiner_apercu(article):
        apercu_rect = pygame.Rect(largeur - 350, hauteur // 2 - 100, 300, 180)
        pygame.draw.rect(mon_ecran, (40, 40, 100), apercu_rect)
        pygame.draw.rect(mon_ecran, BLANC, apercu_rect, 2)
        mon_ecran.blit(ma_police.render("Aperçu :", True, BLANC), (apercu_rect.x + 10, apercu_rect.y + 10))
        mon_ecran.blit(ma_police.render(article["nom"], True, (255, 255, 0)), (apercu_rect.x + 10, apercu_rect.y + 50))
        valeur = article["valeur"]

        if article["type"] == "balle":
            couleur = {"flamme": (255, 69, 0), "electrique": (0, 255, 255), "glace": (100, 200, 255)}.get(valeur, BLANC)
            pygame.draw.circle(mon_ecran, couleur, (apercu_rect.centerx, apercu_rect.y + 120), 15)
        elif article["type"] == "raquette":
            couleur = {"laser": (255, 0, 255), "feu": (255, 100, 0), "pixel": (100, 255, 100)}.get(valeur, BLANC)
            pygame.draw.rect(mon_ecran, couleur, (apercu_rect.centerx - 5, apercu_rect.y + 100, 10, 50))
        elif article["type"] == "fond":
            couleur = {"bleu": (0, 0, 80), "nuit": (10, 10, 30), "futur": (10, 150, 200)}.get(valeur, (0, 100, 0))
            pygame.draw.rect(mon_ecran, couleur, (apercu_rect.x + 200, apercu_rect.y + 120, 60, 30))
        elif article["type"] == "style":
            texte = {"neon": "Effet néon !", "cartoon": "Look cartoon !"}.get(valeur, "Style spécial")
            retro_txt = ma_police.render(texte, True, (180, 180, 180))
            mon_ecran.blit(retro_txt, (apercu_rect.x + 10, apercu_rect.y + 100))
    
    # Approche simple - utiliser des articles fixes
    carte_x = largeur // 2 - largeur_carte // 2  # Position X fixe pour tous les articles
    
    afficher = True
    while afficher:
        mon_ecran.fill((25, 25, 60))
        mon_ecran.blit(police_titre.render("BOUTIQUE", True, BLANC), (largeur // 2 - 150, 50))
        mon_ecran.blit(ma_police.render(f"Monnaie: {monnaie} €", True, (255, 255, 0)), (largeur - 240, 20))
        
        # Recalculer les rectangles à chaque frame pour le scrolling
        rectangles_articles = []
        
        # Afficher directement les articles (sans surface intermédiaire)
        for i, article in enumerate(articles):
            # Position à l'écran de l'article (avec scroll)
            y_ecran = start_y + (i * (hauteur_carte + espacement)) + scroll_y
            
            # Vérifier si l'article est visible à l'écran
            if start_y - hauteur_carte <= y_ecran <= hauteur:
                # Dessiner l'article directement sur l'écran
                rect = pygame.Rect(carte_x, y_ecran, largeur_carte, hauteur_carte)
                # Stocker le rectangle et l'article pour la détection des clics
                rectangles_articles.append((rect, article))
                
                pygame.draw.rect(mon_ecran, (50, 50, 120), rect)
                pygame.draw.rect(mon_ecran, BLANC, rect, 3)
                
                nom = ma_police.render(article["nom"], True, BLANC)
                prix = ma_police.render(f"Prix: {article['prix']} €", True, (255, 215, 0))
                mon_ecran.blit(nom, (carte_x + 10, y_ecran + 10))
                mon_ecran.blit(prix, (carte_x + 10, y_ecran + 50))
                
                if skin_selectionne[article["type"]] == article["valeur"]:
                    check = ma_police.render("Équipé", True, (0, 255, 0))
                    mon_ecran.blit(check, (carte_x + largeur_carte - 110, y_ecran + 35))
                
        if article_en_apercu:
            dessiner_apercu(article_en_apercu)

        info_sortie = ma_police.render("Clique droit: aperçu | Touche pour quitter", True, GRIS)
        mon_ecran.blit(info_sortie, info_sortie.get_rect(center=(largeur // 2, hauteur - 40)))

        pygame.display.flip()

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evenement.type == pygame.KEYDOWN:
                afficher = False
            elif evenement.type == pygame.MOUSEBUTTONDOWN:
                if evenement.button == 4:  # Scroll vers le haut
                    scroll_y = min(scroll_y + vitesse_scroll, 0)
                elif evenement.button == 5:  # Scroll vers le bas
                    max_scroll = -(len(articles) * (hauteur_carte + espacement) - (hauteur - start_y - 50))
                    scroll_y = max(scroll_y - vitesse_scroll, max_scroll)
                else:
                    # Vérification directe des clics sur les rectangles
                    mouse_pos = evenement.pos
                    for rect, article in rectangles_articles:
                        if rect.collidepoint(mouse_pos):
                            if evenement.button == 3:  # Clic droit
                                article_en_apercu = article
                            elif evenement.button == 1:  # Clic gauche
                                type_article = article["type"]
                                valeur_article = article["valeur"]
                                identifiant = f"{type_article}_{valeur_article}"

                                if skin_selectionne.get(type_article) == valeur_article:
                                    skin_selectionne[type_article] = (
                                        "normale" if type_article in ["balle", "raquette"]
                                        else "vert" if type_article == "fond"
                                        else "moderne"
                                    )
                                elif identifiant in articles_achetes:
                                    skin_selectionne[type_article] = valeur_article
                                elif monnaie >= article["prix"]:
                                    monnaie -= article["prix"]
                                    skin_selectionne[type_article] = valeur_article
                                    articles_achetes.add(identifiant)
                                    son_achat.play()
                                else:
                                    son_erreur.play()
                            break  # Sortir de la boucle dès qu'un article est cliqué

def afficher_commandes():
    afficher = True
    while afficher:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evenement.type == pygame.KEYDOWN or evenement.type == pygame.MOUSEBUTTONDOWN:
                afficher = False  # Quitter la page avec un clic ou une touche

        mon_ecran.fill(NOIR)
        titre = ma_police.render("Commandes du jeu", True, BLANC)
        mon_ecran.blit(titre, titre.get_rect(center=(largeur // 2, 100)))

        touches_j1 = [
            "Joueur 1 :",
            "- z : monter",
            "- S : descendre"
        ]

        touches_j2 = [
            "Joueur 2 :",
            "- Flèche Haut : monter",
            "- Flèche Bas : descendre"
        ]

        for i, ligne in enumerate(touches_j1):
            texte = ma_police.render(ligne, True, BLANC)
            mon_ecran.blit(texte, (100, 200 + i * 40))

        for i, ligne in enumerate(touches_j2):
            texte = ma_police.render(ligne, True, BLANC)
            mon_ecran.blit(texte, (largeur // 2 + 50, 200 + i * 40))

        info_sortie = ma_police.render("Appuie sur une touche ou clique pour revenir au menu", True, GRIS)
        mon_ecran.blit(info_sortie, info_sortie.get_rect(center=(largeur // 2, 500)))

        pygame.display.flip()


def afficher_ecran_fin_partie():
    global monnaie
    static_gain_applique = False  # Variable statique pour suivre si le gain a déjà été appliqué
    
    # Ajouter l'attribut statique s'il n'existe pas
    if not hasattr(afficher_ecran_fin_partie, 'gain_applique'):
        afficher_ecran_fin_partie.gain_applique = False
    
    # Ajouter 100 euros de monnaie seulement si ce n'est pas déjà fait
    if not afficher_ecran_fin_partie.gain_applique:
        monnaie += 100
        afficher_ecran_fin_partie.gain_applique = True
    
    mon_ecran.fill((30, 30, 30))
    
    if gagnant == "gauche":
        titre = police_titre.render("Joueur 1 a gagné!", True, (200, 100, 100))
    else:
        titre = police_titre.render("Joueur 2 a gagné!", True, (100, 100, 200))
    
    mon_ecran.blit(titre, (largeur//2 - titre.get_width()//2, 150))
    
    score_final = police_titre.render(f"{score_gauche} - {score_droite}", True, (255, 255, 255))
    mon_ecran.blit(score_final, (largeur//2 - score_final.get_width()//2, hauteur//2 - 50))
    
    # Afficher le montant gagné
    texte_monnaie = ma_police.render(f"+ 100 € gagnés!", True, (255, 215, 0))
    mon_ecran.blit(texte_monnaie, (largeur//2 - texte_monnaie.get_width()//2, hauteur//2 + 20))
    
    dessiner_bouton(bouton_recommencer, mon_ecran)
    dessiner_bouton(bouton_accueil, mon_ecran)

while True:
    horloge.tick(60)  # Limite à 60 FPS
       
    # Affichage en fonction de l'état
    if etat_actuel == ETAT_ACCUEIL:
        afficher_ecran_accueil()
    elif etat_actuel == ETAT_FIN_PARTIE:
        afficher_ecran_fin_partie()
    if faire_decompte:
        decompte_reprise()
        faire_decompte = False
    elif etat_actuel == ETAT_JEU:
        # Utilisons la fonction afficher_table_jeu qui gère déjà correctement tous les skins
        afficher_table_jeu()

        # Déplacement des raquettes
        if mouv_haut_g and raq_g_y > 0:
            raq_g_y -= pas_raquette_gauche
        if mouv_bas_g and raq_g_y < hauteur - h_g:
            raq_g_y += pas_raquette_gauche
        if mouv_haut_d and raq_d_y > 0:
            raq_d_y -= pas_raquette_droite
        if mouv_bas_d and raq_d_y < hauteur - h_d:
            raq_d_y += pas_raquette_droite
        
        if mode_solo:
            if pos_y < raq_d_y + h_d // 2 and raq_d_y > 0:
                raq_d_y -= pas_raquette_droite
            elif pos_y > raq_d_y + h_d // 2 and raq_d_y + h_d < hauteur:
                raq_d_y += pas_raquette_droite

        
        # Affichage
        afficher_table_jeu()
        
        # Bouton pause
        dessiner_bouton(bouton_pause, mon_ecran)

        # Gestion des bonus - possibilité d'avoir plusieurs bonus
        compteur_delai_bonus -= 1 if compteur_delai_bonus > 0 else 0
        
        # Probabilité d'apparition d'un nouveau bonus
        if compteur_delai_bonus <= 0 and randint(0, 100) < 8 and len(bonus_actifs) < max_bonus_simultanes:  # 8% de chance au lieu de 5%
            bonus_actifs.append(creer_bonus())
            compteur_delai_bonus = delai_entre_bonus - randint(0, 30)  # Plus de variation aléatoire
        
        # Mise à jour de tous les bonus actifs
        bonus_a_supprimer = []
        
        for i, bonus in enumerate(bonus_actifs):
            if bonus['actif']:
                # Déplacement du bonus
                bonus['x'] += bonus['direction'][0] * bonus['vitesse']
                bonus['y'] += bonus['direction'][1] * bonus['vitesse']
                
                # Rebond sur les bords
                if bonus['x'] - bonus['rayon'] <= 0 or bonus['x'] + bonus['rayon'] >= largeur:
                    bonus['direction'][0] *= -1
                if bonus['y'] - bonus['rayon'] <= 0 or bonus['y'] + bonus['rayon'] >= hauteur:
                    bonus['direction'][1] *= -1
                
                # Collision avec la raquette gauche
                if (raq_g_x <= bonus['x'] - bonus['rayon'] <= raq_g_x + l_g and 
                    raq_g_y <= bonus['y'] <= raq_g_y + h_g):
                    bonus['actif'] = False
                    bonus['joueur'] = 'gauche'
                    
                    if bonus['type'] == 'vitesse':
                        # Force x2 - sera appliqué au prochain coup
                        force_x2_actif = 'gauche'
                        # Pas de timer pour ce bonus, il sera désactivé après utilisation
                    elif bonus['type'] == 'ralentir adversaire':
                        # Ralentir la raquette adverse pendant 5 secondes
                        pas_raquette_droite = pas_raquette * 0.6
                        bonus['compteur'] = 5 * 60  # 5 secondes à 60 FPS
                        bonus['duree'] = 5 * 60
                    elif bonus['type'] == 'taille':
                        # Agrandir la raquette pendant 15 secondes
                        h_g = int(h_g * 1.5)
                        bonus['compteur'] = 15 * 60  # 15 secondes à 60 FPS
                        bonus['duree'] = 15 * 60
                    elif bonus['type'] == 'multi-balle' and len(multi_balles) < max_multi_balles:
                        # Ajouter une balle supplémentaire si on n'a pas atteint le maximum
                        nouvelle_balle = creer_multi_balle()
                        multi_balles.append(nouvelle_balle)
                        # Ajouter un effet visuel - un cercle qui s'agrandit rapidement autour de la nouvelle balle
                        for r in range(5, 30, 5):
                            pygame.draw.circle(mon_ecran, nouvelle_balle['couleur'], 
                                              (int(nouvelle_balle['pos_x']), int(nouvelle_balle['pos_y'])), r, 2)
                            pygame.display.flip()
                            pygame.time.delay(30)
                        bonus['compteur'] = 3 * 60  # 3 secondes de délai avant de pouvoir réutiliser
                        bonus['duree'] = 3 * 60
                
                # Collision avec la raquette droite
                elif (raq_d_x <= bonus['x'] + bonus['rayon'] <= raq_d_x + l_d and 
                      raq_d_y <= bonus['y'] <= raq_d_y + h_d):
                    bonus['actif'] = False
                    bonus['joueur'] = 'droite'
                    
                    if bonus['type'] == 'vitesse':
                        # Force x2 - sera appliqué au prochain coup
                        force_x2_actif = 'droite'
                        # Pas de timer pour ce bonus, il sera désactivé après utilisation
                    elif bonus['type'] == 'ralentir adversaire':
                        # Ralentir la raquette adverse pendant 5 secondes
                        pas_raquette_gauche = pas_raquette * 0.6
                        bonus['compteur'] = 5 * 60  # 5 secondes à 60 FPS
                        bonus['duree'] = 5 * 60
                    elif bonus['type'] == 'taille':
                        # Agrandir la raquette pendant 15 secondes
                        h_d = int(h_d * 1.5)
                        bonus['compteur'] = 15 * 60  # 15 secondes à 60 FPS
                        bonus['duree'] = 15 * 60
                    elif bonus['type'] == 'multi-balle' and len(multi_balles) < max_multi_balles:
                        # Ajouter une balle supplémentaire si on n'a pas atteint le maximum
                        nouvelle_balle = creer_multi_balle()
                        multi_balles.append(nouvelle_balle)
                        # Ajouter un effet visuel - un cercle qui s'agrandit rapidement autour de la nouvelle balle
                        for r in range(5, 30, 5):
                            pygame.draw.circle(mon_ecran, nouvelle_balle['couleur'], 
                                              (int(nouvelle_balle['pos_x']), int(nouvelle_balle['pos_y'])), r, 2)
                            pygame.display.flip()
                            pygame.time.delay(30)
                        bonus['compteur'] = 3 * 60  # 3 secondes de délai avant de pouvoir réutiliser
                        bonus['duree'] = 3 * 60
            else:
                # Si le bonus est capturé et a un effet temporel, décompter sa durée
                if bonus['compteur'] > 0:
                    bonus['compteur'] -= 1
                    
                    # L'effet du bonus est terminé
                    if bonus['compteur'] <= 0:
                        if bonus['type'] == 'ralentir adversaire':
                            if bonus['joueur'] == 'gauche':
                                pas_raquette_droite = pas_raquette
                            else:
                                pas_raquette_gauche = pas_raquette
                        elif bonus['type'] == 'taille':
                            if bonus['joueur'] == 'gauche':
                                h_g = int(h_g / 1.5)
                            else:
                                h_d = int(h_d / 1.5)
                        
                        # Marquer ce bonus pour suppression
                        bonus_a_supprimer.append(i)
                else:
                    # Si le bonus est utilisé (comme Force x2) et n'a plus d'effet actif
                    if bonus['type'] == 'vitesse' and force_x2_actif != bonus['joueur']:
                        bonus_a_supprimer.append(i)
        
        # Supprimer les bonus terminés (en parcourant la liste en ordre décroissant)
        for i in sorted(bonus_a_supprimer, reverse=True):
            del bonus_actifs[i]

        # Déplacement de la balle
        pos_x += pas * sens[0] * vitesse
        pos_y += pas * sens[1] * vitesse
        
        # Déplacement et gestion des multi-balles
        balles_a_supprimer = []
        for i, balle in enumerate(multi_balles):
            # Déplacement
            balle['pos_x'] += balle['vitesse'] * balle['sens'][0]
            balle['pos_y'] += balle['vitesse'] * balle['sens'][1]
            
            # Gestion des rebonds sur les murs
            if balle['pos_y'] - balle['rayon'] <= 0 or balle['pos_y'] + balle['rayon'] >= hauteur:
                balle['sens'][1] *= -1
                
            # Collision avec les raquettes
            if (raq_g_x <= balle['pos_x'] - balle['rayon'] <= raq_g_x + l_g and 
                raq_g_y <= balle['pos_y'] <= raq_g_y + h_g and balle['sens'][0] < 0):
                balle['sens'][0] *= -1
            elif (raq_d_x <= balle['pos_x'] + balle['rayon'] <= raq_d_x + l_d and 
                  raq_d_y <= balle['pos_y'] <= raq_d_y + h_d and balle['sens'][0] > 0):
                balle['sens'][0] *= -1
                
            # Décompte de la durée
            balle['duree'] -= 1
            if balle['duree'] <= 0:
                balles_a_supprimer.append(i)
            
            # Points si la balle sort (pas de réinitialisation du jeu)
            if balle['pos_x'] - balle['rayon'] <= 0:
                score_droite += 1
                balles_a_supprimer.append(i)
                if score_droite >= points_max:
                    gagnant = "droite"
                    etat_actuel = ETAT_FIN_PARTIE
            elif balle['pos_x'] + balle['rayon'] >= largeur:
                score_gauche += 1
                balles_a_supprimer.append(i)
                if score_gauche >= points_max:
                    gagnant = "gauche"
                    etat_actuel = ETAT_FIN_PARTIE
                
        # Supprimer les balles qui ont expiré ou sont sorties
        for i in sorted(balles_a_supprimer, reverse=True):
            del multi_balles[i]

        # Collisions avec les raquettes
        if (raq_g_x <= pos_x - rayon <= raq_g_x + l_g
                and raq_g_y <= pos_y <= raq_g_y + h_g):
            if sens[0] < 0:  # Ne rebondit que si la balle va vers la raquette
                sens[0] *= -1
                # Appliquer Force x2 si actif
                if force_x2_actif == 'gauche':
                    vitesse *= 2
                    force_x2_actif = None
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
                # Ajouter 100 à la monnaie (sera traité en variable globale dans afficher_ecran_fin_partie)
                etat_actuel = ETAT_FIN_PARTIE
            else:
                reinitialiser_jeu()
        elif pos_x + rayon >= largeur:
            score_gauche += 1
            if score_gauche >= points_max:
                gagnant = "gauche"
                # Ajouter 100 à la monnaie (sera traité en variable globale dans afficher_ecran_fin_partie)
                etat_actuel = ETAT_FIN_PARTIE
            else:
                reinitialiser_jeu()

    # Gestion des événements
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        position_souris = pygame.mouse.get_pos()
        
        if etat_actuel == ETAT_ACCUEIL:
            # Mise à jour de l'état des boutons
            verifier_survol_bouton(bouton_5_points, position_souris)
            verifier_survol_bouton(bouton_11_points, position_souris)
            verifier_survol_bouton(bouton_21_points, position_souris)
            verifier_survol_bouton(bouton_start, position_souris)
            verifier_survol_bouton(bouton_commandes, position_souris)
            verifier_survol_bouton(bouton_quitter, position_souris)
            verifier_survol_bouton(bouton_boutique, position_souris)
            verifier_survol_bouton(bouton_solo, position_souris)
            
            
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
                # Réinitialiser le suivi du gain pour la prochaine partie
                if hasattr(afficher_ecran_fin_partie, 'gain_applique'):
                    afficher_ecran_fin_partie.gain_applique = False
            elif est_bouton_clique(bouton_commandes, evenement):
                afficher_commandes()
            elif est_bouton_clique(bouton_quitter, evenement):
                pygame.quit()
                sys.exit()
            elif est_bouton_clique(bouton_boutique, evenement):
                afficher_boutique()
            elif est_bouton_clique(bouton_solo, evenement):
                mode_solo = True
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
                # Réinitialiser le suivi du gain pour la prochaine partie
                afficher_ecran_fin_partie.gain_applique = False
            elif est_bouton_clique(bouton_accueil, evenement):
                etat_actuel = ETAT_ACCUEIL
                # Réinitialiser le suivi du gain pour la prochaine partie
                afficher_ecran_fin_partie.gain_applique = False

        elif etat_actuel == ETAT_JEU:
            verifier_survol_bouton(bouton_pause, position_souris)
            if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
                if est_bouton_clique(bouton_pause, evenement):
                    afficher_menu_pause()
            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_s:  # S pour descendre à gauche
                    mouv_bas_g = True
                elif evenement.key == pygame.K_z:  # Z pour monter à gauche
                    mouv_haut_g = True
                elif evenement.key == pygame.K_DOWN:
                    mouv_bas_d = True
                elif evenement.key == pygame.K_UP:
                    mouv_haut_d = True
                elif evenement.key == pygame.K_f:  # Touche F pour basculer en plein écran
                    basculer_plein_ecran()
            elif evenement.type == pygame.KEYUP:
                if evenement.key == pygame.K_s:
                    mouv_bas_g = False
                elif evenement.key == pygame.K_z:
                    mouv_haut_g = False
                elif evenement.key == pygame.K_DOWN:
                    mouv_bas_d = False
                elif evenement.key == pygame.K_UP:
                    mouv_haut_d = False

    pygame.display.flip()