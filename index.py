import pgzrun
import pygame
import os

TITLE = "SpaceBusines"

WIDTH  = 1200
HEIGHT = 800

#-------------------------------------------
#Menü Klassen
class Menu:
    def __init__(self):
        self.menu_items = ["Start New Game", "Continue Game", "Settings", "Credits", "Quit"]
        self.menu_buttons = []
        self.setup()

    def setup(self):
        start_y = 250

        for i, text in enumerate(self.menu_items):
            rect = pygame.Rect(0, 0, 300, 50)
            rect.center = (WIDTH // 2, start_y + i * 70)

            surface = pygame.Surface((300, 50), pygame.SRCALPHA)
            pygame.draw.rect(surface, (0, 0, 255, 100), (0, 0, 300, 50), border_radius=15)

            self.menu_buttons.append((text, rect, surface))

    def draw(self):
        bliting_bg("bg_menu.jpg")

        screen.draw.text(
            TITLE,
            center=(WIDTH // 2, 120),
            fontsize=60,
            color="white"
        )

        for text, rect, surface in self.menu_buttons:
            screen.blit(surface, rect.topleft)

            screen.draw.text(
                text,
                center=rect.center,
                fontsize=30,
                color="white"
            )

    def on_mouse_down(self, pos):
        global menu

        for text, rect, surface in self.menu_buttons:
            if rect.collidepoint(pos):
                if text == "Quit":
                    pygame.quit()
                    exit()
                elif text == "Start New Game":
                    menu = NewGame()
                elif text == "Continue Game":
                    menu = ContinueGame()
                elif text == "Settings":
                    menu = Settings()
                elif text == "Credits":
                    menu = Credits()

class NewGame:
    def __init__(self):
        self.new_items = ["Back", "Einfach", "Normal", "Schwer"]
        self.new_buttons = []
        self.setup()
    
    def setup(self):
        start_y = 250

        for i, text in enumerate(self.new_items):
            rect = pygame.Rect(0, 0, 300, 50)
            rect.center = (WIDTH // 2, start_y + i * 70)

            surface = pygame.Surface((300, 50), pygame.SRCALPHA)
            pygame.draw.rect(surface, (0, 0, 255, 100), (0, 0, 300, 50), border_radius=15)

            self.new_buttons.append((text, rect, surface))

    def draw(self):
        bliting_bg("bg_new.jpg")
        screen.draw.text(
            "New Game",
            center=(WIDTH // 2, 120),
            fontsize=60,
            color="white"
        )
        for text, rect, surface in self.new_buttons:
            screen.blit(surface, rect.topleft)

            screen.draw.text(
                text,
                center=rect.center,
                fontsize=30,
                color="white"
            )
    def on_mouse_down(self, pos):
        global menu

        for text, rect, surface in self.new_buttons:
            if rect.collidepoint(pos):
                if text == "Back":
                    menu = Menu()
                else:
                    print(f"Selected difficulty: {text}")

class ContinueGame:
    def __init__(self):
        pass

    def draw(self):
        bliting_bg("bg_continue.jpg")

class Settings:
    def __init__(self):
        pass

    def draw(self):
        bliting_bg("bg_settings.jpg")

class Credits:
    def __init__(self):
        pass

    def draw(self):
        bliting_bg("bg_menu.jpg")
#-------------------------------------------
#Hintergrund laden und skalieren
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
#Funktion die automatisch die Hintergrundbilder aus der Liste zentriert auf den Bildschirm blitet
def bliting_bg(img: str):
    bg = backgrounds[img]
    screen.blit(bg, ((WIDTH-bg.get_width()) // 2, (HEIGHT-bg.get_height()) // 2))

menu = Menu()

def draw():
    screen.clear()
    menu.draw()

def on_mouse_down(pos):
    menu.on_mouse_down(pos)

def update():
    pass


pgzrun.go()