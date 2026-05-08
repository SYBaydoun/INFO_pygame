import pgzrun
import pygame
import os

TITLE = "SpaceBusines"

WIDTH  = 1200
HEIGHT = 800

#-------------------------------------------
#Hintergrund laden und skalieren
"""
bg = pygame.image.load("images/bg_menu.jpg")
#bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

orig_width = bg.get_width()
orig_height = bg.get_height()
scale = max(WIDTH / orig_width, HEIGHT / orig_height)
new_width = int(orig_width * scale)
new_height = int(orig_height * scale)

bg = pygame.transform.smoothscale(bg, (new_width, new_height))

x = (WIDTH - new_width) // 2
y = (HEIGHT - new_height) // 2
"""

backgrounds = {}

for filename in os.listdir("images"):
    if filename.startswith("bg_"):
        path = os.path.join("images", filename)

        bg = pygame.image.load(path)

        orig_width = bg.get_width()
        orig_height = bg.get_height()

        scale = max(WIDTH / orig_width, HEIGHT / orig_height)

        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)

        bg = pygame.transform.smoothscale(bg, (new_width, new_height))

        backgrounds[filename] = bg
print(backgrounds)

#-------------------------------------------
#Menüeinträge

menu_items = ["Start New Game", "Continue Game", "Settings", "Credits", "Quit"]
# Positionen der Buttons
menu_buttons = []

#Startmenu button setup
def menu_setup():
    start_y = 250
    for i, text in enumerate(menu_items):
        rect = pygame.Rect(0, 0, 300, 50)
        rect.center = (WIDTH // 2, start_y + i * 70)

        surface = pygame.Surface((300, 50), pygame.SRCALPHA)
        surface.fill((0, 0, 255, 100))

        menu_buttons.append((text, rect, surface))
menu_setup()

#-------------------------------------------
#Funktion die automatisch die Hintergrundbilder aus der Liste zentriert auf den Bildschirm blitet
def bliting_bg(img: str):
    bg = backgrounds[img]
    screen.blit(bg, ((WIDTH-bg.get_width()) // 2, (HEIGHT-bg.get_height()) // 2))


def draw():
    #Background
    screen.clear()

    #screen.blit(bg, (0, 0))
    bliting_bg("bg_menu.jpg")

    #Titel
    screen.draw.text(
        TITLE,
        center=(WIDTH // 2, 120),
        fontsize=60,
        color="white"
    )

    #Buttons
    for text, rect, surface in menu_buttons:
        screen.blit(surface, rect.topleft)

        screen.draw.text(
            text,
            center=rect.center,
            fontsize=30,
            color="white"
        )

def on_mouse_down(pos):
    for text, rect in menu_buttons:
        if rect.collidepoint(pos):
            print("geklickt:", text)

            if text == "Quit":
                pygame.quit()
                exit()
            elif text == "Start New Game":
                pass
            elif text == "Continue Game":
                pass
            elif text == "Settings":
                pass
            elif text == "Credits":
                pass

def update():
    pass

pgzrun.go()