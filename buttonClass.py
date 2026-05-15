import pgzrun
import pygame
import os

#Parameter
WIDTH  = 1200
HEIGHT = 800

TITLE = "SpaceBusiness"
creditMsg = "Game developed by:\nShahin Youssef Baydoun\n Moralische Unterstützung:\nAlinchen Bienchen :)\ntest"

#Buttons im Menübereich
menuLibrary = {"menu_items": ["Start New Game", "Continue Game", "Settings", "Credits", "Quit"],
               "new_items": ["Back", "Easy", "Medium", "Hard"],
               "continue_items": ["Back", "Save 1", "Save 2", "Save 3"],
               "settings_items": ["Back", "Audio", "Video", "Controls"],
               "credits_items": ["Back"]}

#-------------------------------------------
#Parent Classe Für die Menü Szenen
class MenuSzene():
    def __init__(self, items: str, buttons:str, draw_bg:str, title:str, text: str = ""):
        self.items = menuLibrary[items]
        self.buttons = []
        self.draw_bg = draw_bg
        self.title = title
        self.text = text
        self.setup()
    
    def setup(self):
        start_y = 250

        for i, text in enumerate(self.items):
            rect = pygame.Rect(0, 0, 300, 50)
            rect.center = (WIDTH // 2, start_y + i * 70)

            surface = pygame.Surface((300, 50), pygame.SRCALPHA)
            pygame.draw.rect(surface, (0, 0, 255, 100), (0, 0, 300, 50), border_radius=15)

            self.buttons.append((text, rect, surface))

    def draw(self):
        bliting_bg(self.draw_bg)
        screen.draw.text(
            self.title,
            center=(WIDTH // 2, 120),
            fontsize=60,
            color="white",
            owidth=3,
            ocolor="red"
        )

        for text, rect, surface in self.buttons:
            screen.blit(surface, rect.topleft)

            screen.draw.text(
                text,
                center=rect.center,
                fontsize=30,
                color="white"
            )

        if self.text != "":
            lines = self.text.split('\n')
            start_y = 200 + len(self.buttons) * 70 + 50 # Startpunkt unter den Buttons
            for i, line in enumerate(lines):
                fontsize = 20 if i % 2 == 0 else 50  # Gerade Zeilen größer, ungerade kleiner
                screen.draw.text(
                    line,
                    center=(WIDTH // 2, start_y + i * 50),
                    fontsize=fontsize,
                    color="white",
                    owidth=2.5,
                    ocolor="black"
                )
    
#Szene Hauptmenü
class Menu(MenuSzene):
    def __init__(self):
        super().__init__("menu_items", "menu_buttons", "bg_menu.jpg", TITLE)
    
    def on_mouse_down(self, pos):
        global menu

        for text, rect, surface in self.buttons:
            if rect.collidepoint(pos):
                if text == "Start New Game":
                    menu = NewGame()
                elif text == "Continue Game":
                    menu = ContinueGame()
                elif text == "Settings":
                    menu = Settings()
                elif text == "Credits":
                    menu = Credits()
                elif text == "Quit":
                    pygame.quit()
                    exit()

#Szene Neues Spiel
class NewGame(MenuSzene):
    def __init__(self):
        super().__init__("new_items", "new_buttons", "bg_new.jpg", "Start New Game")
    
    def on_mouse_down(self, pos):
        global menu

        for text, rect, surface in self.buttons:
            if rect.collidepoint(pos):
                if text == "Back":
                    menu = Menu()
                elif text in ["Easy", "Medium", "Hard"]:
                    print(f"Starting new game on {text} difficulty...")

#Szene Spiel fortsetzen
class ContinueGame(MenuSzene):
    def __init__(self):
        super().__init__("continue_items", "continue_buttons", "bg_continue.jpg", "Continue Game")

    def on_mouse_down(self, pos):
        global menu

        for text, rect, surface in self.buttons:
            if rect.collidepoint(pos):
                if text == "Back":
                    menu = Menu()
                elif text.startswith("Save"):
                    print(f"Continuing game from {text}...")

#Szene Einstellungen
class Settings(MenuSzene):
    def __init__(self):
        super().__init__("settings_items", "settings_buttons", "bg_settings.jpg", "Settings")

    def on_mouse_down(self, pos):
        global menu

        for text, rect, surface in self.buttons:
            if rect.collidepoint(pos):
                if text == "Back":
                    menu = Menu()
                elif text == "Audio":
                    print("Adjusting audio settings...")
                elif text == "Video":
                    print("Adjusting video settings...")
                elif text == "Controls":
                    print("Adjusting control settings...")

#Szene Credits [ Me ;) ]
class Credits(MenuSzene):
    def __init__(self):
        super().__init__("credits_items", "credits_buttons", "bg_menu.jpg", "Credits", creditMsg)
    
    def on_mouse_down(self, pos):
        global menu

        for text, rect, surface in self.buttons:
            if rect.collidepoint(pos):
                if text == "Back":
                    menu = Menu()

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

#Funktion die automatisch die Hintergrundbilder aus der Liste zentriert auf den Bildschirm blitet
def bliting_bg(img: str):
    bg = backgrounds[img]
    screen.blit(bg, ((WIDTH-bg.get_width()) // 2, (HEIGHT-bg.get_height()) // 2))

#setzt die buttonkollision für die szenen um
def on_mouse_down(pos):
    menu.on_mouse_down(pos)

#-------------------------------------------
#Startet mit dem Hauptmenü
menu = Menu()

#initiale draw funktion die die aktuelle Szene zeichnet
def draw():
    screen.clear()
    menu.draw()

#frames
def update():
    pass

#go
pgzrun.go()