import pgzrun
import pygame
import os

# öffnet das verfluchte Fenster zentriert, warum auch immer das nicht automatisch passiert
os.environ['SDL_VIDEO_CENTERED'] = '1'

#Parameter
WIDTH  = 1200
HEIGHT = 800

TITLE = "SpaceBusiness"
creditMsg = "Game developed by:\nShahin Youssef Baydoun\n Moralische Unterstützung:\nAlinchen Bienchen :)\ntest"

#Buttons im Menübereich
menuLibrary = {"menu_items": ["Start New Game", "Continue Game", "Settings", "Credits", "Quit"],
               "new_items": ["Back", "Easy", "Medium", "Hard"],
               "continue_items": ["Back", "Save 1", "Save 2", "Save 3", "Save 4", "Save 5", "Save 6", "Save 7", "Save 8", "Save 9", "Save 10"], # benötigt scroll fix !!!!!!
               "settings_items": ["Back", "Audio", "Video", "Controls"],
               "credits_items": ["Back"]}


class SceneManager():
    dauer_bewegung = 120
    dauer_ruhen = 10
    def __init__(self, start_scene):
        self.scene = start_scene
        self.scene.on_enter()

        self.transitioning = False
        self.phase = 0  # 0 idle, 1 close, 2 hold, 3 open

        self.next_scene = None
        self.t = 0
        self.speed = 1

    def change_scene(self, new_scene):
        if self.transitioning:
            return

        self.transitioning = True
        self.next_scene = new_scene
        self.phase = 1
        self.t = 0

    def update(self):
        if not self.transitioning:
            self.scene.update()
            return

        self.t += self.speed

        # --------------------
        # PHASE 1: CLOSE
        # --------------------
        if self.phase == 1:
            if self.t == 1:
                door_sound.stop()
                door_sound.play()
            if self.t >= self.dauer_bewegung: # >= damit bei einem overshoot durch eine speed die nicht perfekt passt trozdem stoppt
                if hasattr(self.scene, "on_exit"):
                    self.scene.on_exit()

                self.scene = self.next_scene
                self.scene.on_enter()

                self.phase = 2 # <- neue Phase
                self.t = 0 # <- immerwieder zurücksetzen für nächsten Phaseniteration

        # --------------------
        # PHASE 2: HOLD (geschlossen)
        # --------------------
        elif self.phase == 2:
            if self.t == self.dauer_ruhen //2:
                door_sound.stop()
            if self.t >= self.dauer_ruhen:   # <- dauer die gewartet wird bevor die türen wieder aufgehen
                self.phase = 3
                self.t = 0

        # --------------------
        # PHASE 3: OPEN
        # --------------------
        elif self.phase == 3:
            if self.t == 1:
                door_sound.play()
            if self.t >= self.dauer_bewegung:
                self.transitioning = False # transition ist vorbei
                self.phase = 0
                self.t = 0

    def draw(self):
        self.scene.draw()

        if self.transitioning:
            self.draw_doors()

    def on_mouse_down(self, pos):
        if self.transitioning:
            return

        if hasattr(self.scene, "on_mouse_down"):
            self.scene.on_mouse_down(pos)

    def draw_doors(self):
        duration = 60

        # CLOSE animation
        if self.phase == 1:
            progress = min(self.t / duration, 1)

        # HOLD (fully closed)
        elif self.phase == 2:
            progress = 1

        # OPEN animation
        else:  # phase 3
            progress = 1 - min(self.t / duration, 1)

        # smoothstep
        progress = progress * progress * (3 - 2 * progress)

        top_h = door_top.get_height()
        bottom_h = door_bottom.get_height()

        top_y = -top_h + top_h * progress
        bottom_y = HEIGHT - bottom_h * progress

        screen.blit(door_top, (0, top_y))
        screen.blit(door_bottom, (0, bottom_y))

class Button():
    def __init__(self, text, center):
        #inhalt
        self.text = text

        #position und größe
        self.width = 300
        self.height = 50
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = center

        # Animationen
        #-> transparenz des buttons
        self.alpha = 140
        self.target_alpha = 140

        #-> transparenz des glows
        self.glow_alpha = 0
        self.target_glow = 0

        #-> vertikale verschiebung des buttons
        self.offset_y = 0
        self.target_offset_y = 0

    def update(self):
        mouse_pos = pygame.mouse.get_pos()

        hovered = self.rect.collidepoint(mouse_pos)

        if hovered:
            self.target_alpha = 220
            self.target_glow = 180
            self.target_offset_y = -3
        else:
            self.target_alpha = 140
            self.target_glow = 0
            self.target_offset_y = 0

        speed = 0.12

        self.alpha += (self.target_alpha - self.alpha) * speed
        self.glow_alpha += (self.target_glow - self.glow_alpha) * speed
        self.offset_y += (self.target_offset_y - self.offset_y) * speed

    def draw(self):
        x = self.rect.x
        y = self.rect.y + self.offset_y

        width = self.width
        height = self.height

        #button
        button_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        pygame.draw.rect(
            button_surface,
            (25, 35, 70, int(self.alpha)),
            (0, 0, width, height),
            border_radius=15
        )

        # Outline
        pygame.draw.rect(
            button_surface,
            (120, 170, 255, min(int(self.glow_alpha), 120)),
            (0, 0, width, height),
            width=4,
            border_radius=15
        )
        screen.blit(button_surface, (x, y))

        #text
        screen.draw.text(
            self.text,
            center=(self.rect.centerx, self.rect.centery + self.offset_y),
            fontsize=30,
            color="white"
        )

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

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

            button = Button(
                text,
                (WIDTH // 2, start_y + i * 70)
            )

            self.buttons.append(button)

    def draw(self):
        bliting_bg(self.draw_bg)
        screen.draw.text(
            self.title,
            center=(WIDTH // 2, 120),
            fontsize=60,
            color="white",
            owidth=3,
            ocolor="#ff7300"
        )

        for button in self.buttons:
            button.draw()

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
    def update(self):
        for button in self.buttons:
            button.update()
    
    def on_enter(self):
        pass

    def on_exit(self):
        pass
    
#Szene Hauptmenü
class Menu(MenuSzene):
    def __init__(self):
        super().__init__("menu_items", "menu_buttons", "bg_menu.jpg", TITLE)
    
    def on_mouse_down(self, pos):
        for button in self.buttons:
            if button.clicked(pos):
                if button.text == "Start New Game":
                    manager.change_scene(NewGame())
                elif button.text == "Continue Game":
                    manager.change_scene(ContinueGame())
                elif button.text == "Settings":
                    manager.change_scene(Settings())
                elif button.text == "Credits":
                    manager.change_scene(Credits())
                elif button.text == "Quit":
                    pygame.quit()
                    exit()

#Szene Neues Spiel
class NewGame(MenuSzene):
    def __init__(self):
        super().__init__("new_items", "new_buttons", "bg_new.jpg", "Start New Game")
    
    def on_mouse_down(self, pos):
        for button in self.buttons:
            if button.clicked(pos):
                if button.text == "Back":
                    manager.change_scene(Menu())
                elif button.text in ["Easy", "Medium", "Hard"]:
                    print(f"Starting new game on {button.text} difficulty...")

#Szene Spiel fortsetzen
class ContinueGame(MenuSzene):
    def __init__(self):
        super().__init__("continue_items", "continue_buttons", "bg_continue.jpg", "Continue Game")

    def on_mouse_down(self, pos):
        for button in self.buttons:
             if button.clicked(pos):
                if button.text == "Back":
                    manager.change_scene(Menu())
                elif button.text.startswith("Save"):
                    print(f"Continuing game from {button.text}...")

#Szene Einstellungen
class Settings(MenuSzene):
    def __init__(self):
        super().__init__("settings_items", "settings_buttons", "bg_settings.jpg", "Settings")

    def on_mouse_down(self, pos):
        for button in self.buttons:
             if button.clicked(pos):
                if button.text == "Back":
                    manager.change_scene(Menu())
                elif button.text == "Audio":
                    print("Adjusting audio settings...")
                elif button.text == "Video":
                    print("Adjusting video settings...")
                elif button.text == "Controls":
                    print("Adjusting control settings...")

#Szene Credits [ Me ;) ]
class Credits(MenuSzene):
    def __init__(self):
        super().__init__("credits_items", "credits_buttons", "bg_menu.jpg", "Credits", creditMsg)
    
    def on_mouse_down(self, pos):
        for button in self.buttons:
             if button.clicked(pos):
                if button.text == "Back":
                    manager.change_scene(Menu())



class GameScene():
    def __init__(self, draw_bg:str):
        self.draw_bg = draw_bg
    
    def draw(self):
        bliting_bg(self.draw_bg)

class GameHomeBase(GameScene):
    def __init__(self):
        super().__init__()

class GameSketch(GameScene):
    def __init__(self):
        super().__init__("bg_blueprint.jpg")



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

door_top = pygame.image.load("images/door_top.png")
door_bottom = pygame.image.load("images/door_bottom.png")

def scale_to_half_height_full_width(img):
    return pygame.transform.smoothscale(img, (WIDTH, HEIGHT // 2))

door_top = scale_to_half_height_full_width(door_top)
door_bottom = scale_to_half_height_full_width(door_bottom)

door_sound = pygame.mixer.Sound("sounds/door_open_close.wav")
door_sound.set_volume(0.5)

#Funktion die automatisch die Hintergrundbilder aus der Liste zentriert auf den Bildschirm blitet
def bliting_bg(img: str):
    bg = backgrounds[img]
    screen.blit(bg, ((WIDTH-bg.get_width()) // 2, (HEIGHT-bg.get_height()) // 2))

#setzt die buttonkollision für die szenen um
def on_mouse_down(pos):
    manager.on_mouse_down(pos)

#-------------------------------------------
#Startet mit dem Hauptmenü
manager = None
manager = SceneManager(Menu())

#initiale draw funktion die die aktuelle Szene zeichnet
def draw():
    screen.clear()
    manager.draw()

#frames
def update():
    manager.update()

#go
pgzrun.go()