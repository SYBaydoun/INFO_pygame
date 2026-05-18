import pgzrun
import pygame
import os
import json

# öffnet das verfluchte Fenster zentriert, warum auch immer das nicht automatisch passiert
os.environ['SDL_VIDEO_CENTERED'] = '1'

#Parameter
WIDTH  = 1200
HEIGHT = 800

TITLE = "SpaceBusiness"
creditMsg = "Game developed by:\nShahin Youssef Baydoun\n Moralische Unterstützung:\nAlinchen Bienchen :)\ntest"

#Buttons im Menübereich
menuLibrary = {"menu_items": ["Start New Game", "Continue Game", "Settings", "Credits", "Quit"],
               "new_items": ["Back"],
               "continue_items": ["Back"],
               "settings_items": ["Back", "Audio", "Video", "Controls"],
               "credits_items": ["Back"]
               }

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
    def __init__(self, items: str, buttons:str, draw_bg:str, title:str, text: str = "", input: bool = False):
        self.items = menuLibrary[items]
        self.buttons = []
        self.draw_bg = draw_bg
        self.title = title
        self.text = text
        self.input = input
        self.input_text = ""
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
        start_y = 200 + len(self.buttons) * 70 + 50 # Startpunkt unter den Buttons
        if self.text != "":
            lines = self.text.split('\n')
            
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
        
        if self.input:
            input_rect = pygame.Rect(WIDTH // 2 - 200, start_y, 400, 50)
            pygame.draw.rect(screen.surface, (255, 255, 255), input_rect, border_radius=10)
            pygame.draw.rect(screen.surface, (0, 0, 0), input_rect, 3, border_radius=10)
            screen.draw.text(
                self.input_text if self.input_text else "Type here...",
                center=(WIDTH // 2, start_y + 25),
                fontsize=30,
                color="black" if self.input_text else (120, 120, 120)
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
        super().__init__("new_items", "new_buttons", "bg_new.jpg", "Start New Game", input=True)
        self.current_save_path = None
    
    def on_mouse_down(self, pos):
        for button in self.buttons:
            if button.clicked(pos):
                if button.text == "Back":
                    manager.change_scene(Menu())

#Szene Spiel fortsetzen
class ContinueGame(MenuSzene):
    def __init__(self):
        super().__init__("continue_items", "continue_buttons", "bg_continue.jpg", "Continue Game", input=True)

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
    def __init__(self):
        self.resources = {
            "electricity": {"current": 70, "max": 100},
            "metal": {"current": 40, "max": 100},
            "minerals": {"current": 85, "max": 100},
            "water": {"current": 20, "max": 100},
            "communication": {"current": 55, "max": 100},
        }
        self.money = 123456
        self.science = 67890
        
        # UI constants
        self.ui_y = HEIGHT - 50
        self.ui_spacing = 240
        
        # Icons
        self.resource_icons = {
            "electricity": chati_isometric.resource_icons["electricity"],
            "metal": chati_isometric.resource_icons["metal"],
            "minerals": chati_isometric.resource_icons["minerals"],
            "water": chati_isometric.resource_icons["water"],
            "communication": chati_isometric.resource_icons["communication"],
        }
        self.money_icon = chati_isometric.money_icon
        self.science_icon = chati_isometric.science_icon
        
        # Colors
        self.resource_colors = {
            "electricity": (255, 220, 50),
            "metal": (180, 180, 180),
            "minerals": (120, 200, 120),
            "water": (80, 160, 255),
            "communication": (200, 120, 255),
        }
    
    def draw_resource_bar(self, x, y, resource):
        bar_width = 200
        bar_height = 22
        radius = bar_height // 2

        current = self.resources[resource]["current"]
        max_v = self.resources[resource]["max"]
        ratio = current / max_v

        bg = (30, 30, 45)
        border = (255, 255, 255)
        fill = self.resource_colors[resource]
        icon = self.resource_icons[resource]

        # --- BAR BACKGROUND (capsule) ---
        pygame.draw.rect(
            screen.surface,
            bg,
            (x, y - bar_height // 2, bar_width, bar_height),
            border_radius=radius
        )

        # --- BAR FILL (capsule clipped) ---
        fill_width = int(bar_width * ratio)
        pygame.draw.rect(
            screen.surface,
            fill,
            (x, y - bar_height // 2, fill_width, bar_height),
            border_radius=radius
        )

        # --- BORDER ---
        pygame.draw.rect(
            screen.surface,
            border,
            (x, y - bar_height // 2, bar_width, bar_height),
            2,
            border_radius=radius
        )

        chati_isometric.Icon(icon, (x, y)).draw()
    
    def draw_top_stats(self):
        spacing = 80
        money_text = str(self.money)
        science_text = str(self.science)
        font_size = 36
        font = pygame.font.SysFont(None, font_size)

        money_width = font.size(money_text)[0]
        science_width = font.size(science_text)[0]
        icon_w = chati_isometric.icon_size[0]

        total_width = money_width + icon_w + spacing + icon_w + science_width
        start_x = WIDTH // 2 - total_width // 2
        y = 40

        # Money
        screen.draw.text(
            money_text,
            (start_x, y - 18),
            fontsize=font_size,
            color=(255, 220, 80)
        )
        money_icon_x = start_x + money_width + 20
        chati_isometric.Icon(self.money_icon, (money_icon_x, y)).draw()

        # Science
        science_icon_x = money_icon_x + spacing
        chati_isometric.Icon(self.science_icon, (science_icon_x, y)).draw()
        screen.draw.text(
            science_text,
            (science_icon_x + 20, y - 18),
            fontsize=font_size,
            color=(120, 220, 255)
        )
    
    def draw_resource_bars(self):
        count = len(self.resources)
        bar_width = 200
        spacing = 240
        total_width = (count - 1) * spacing + bar_width
        start_x = WIDTH // 2 - total_width // 2

        for i, resource in enumerate(self.resources.keys()):
            x = start_x + i * spacing
            self.draw_resource_bar(x, self.ui_y, resource)
    
    def draw(self):
        pass
    
    def update(self):
        pass
    
    def on_enter(self):
        pass

    def on_exit(self):
        pass
    
    def on_mouse_down(self, pos):
        pass

class GameHomeBase(GameScene):
    def __init__(self, save_path=None):
        super().__init__()
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 0.1
        self.save_path = save_path
        
        # Load save if provided
        if save_path:
            try:
                state = chati_isometric.load_save(save_path)
                self.resources = {
                    "electricity": {"current": state["resources"]["electricity"], "max": state["resource_max"]["electricity"]},
                    "metal": {"current": state["resources"]["metal"], "max": state["resource_max"]["metal"]},
                    "minerals": {"current": state["resources"]["minerals"], "max": state["resource_max"]["minerals"]},
                    "water": {"current": state["resources"]["water"], "max": state["resource_max"]["water"]},
                    "communication": {"current": state["resources"]["communication"], "max": state["resource_max"]["communication"]},
                }
                self.money = state["resources"]["money"]
                self.science = state["resources"]["science"]
            except:
                pass
    
    def draw(self):
        screen.fill((40, 40, 60))

        # Draw isometric world
        for y in reversed(range(int(self.camera_y)-20, int(self.camera_y)+20)):
            for x in reversed(range(int(self.camera_x)-20, int(self.camera_x)+20)):
                if x >= 0 and y >= 0:
                    h = chati_isometric.get_height(x, y)
                    base_x, base_y = chati_isometric.iso_to_screen(x, y, self.camera_x, self.camera_y, WIDTH, HEIGHT)

                    for level in range(int(h) + 1):
                        screen_x = base_x
                        screen_y = base_y - level * chati_isometric.HEIGHT_STEP
                        tile = chati_isometric.scaled_tiles[min(level, 3)]
                        screen.surface.blit(
                            tile,
                            (screen_x - chati_isometric.TILE_WIDTH // 2,
                            screen_y - chati_isometric.TILE_HEIGHT // 2)
                        )

        # Draw UI
        self.draw_resource_bars()
        self.draw_top_stats()
    
    def update(self):
        # Camera movement
        if keyboard.w:
            self.camera_y += self.camera_speed
            self.camera_x += self.camera_speed

        if self.camera_x - self.camera_speed >= 0 and self.camera_y - self.camera_speed >= 0:
            if keyboard.s:
                self.camera_y -= self.camera_speed
                self.camera_x -= self.camera_speed

        if self.camera_y - self.camera_speed >= 0:
            if keyboard.a:
                self.camera_x += self.camera_speed
                self.camera_y -= self.camera_speed

        if self.camera_x - self.camera_speed >= 0:
            if keyboard.d:
                self.camera_x -= self.camera_speed
                self.camera_y += self.camera_speed

class GameSketch(GameScene):
    def __init__(self, save_path=None):
        super().__init__()
        self.save_path = save_path
        
        # Load save if provided
        if save_path:
            try:
                state = chati_isometric.load_save(save_path)
                self.resources = {
                    "electricity": {"current": state["resources"]["electricity"], "max": state["resource_max"]["electricity"]},
                    "metal": {"current": state["resources"]["metal"], "max": state["resource_max"]["metal"]},
                    "minerals": {"current": state["resources"]["minerals"], "max": state["resource_max"]["minerals"]},
                    "water": {"current": state["resources"]["water"], "max": state["resource_max"]["water"]},
                    "communication": {"current": state["resources"]["communication"], "max": state["resource_max"]["communication"]},
                }
                self.money = state["resources"]["money"]
                self.science = state["resources"]["science"]
            except:
                pass
    
    def draw(self):
        bliting_bg("bg_blueprint.jpg")
        self.draw_resource_bars()
        self.draw_top_stats()
    
    def update(self):
        pass



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

# input handling for active menu input fields
def sanitize_filename(name: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ ")
    sanitized = "".join(ch for ch in name if ch in allowed).strip()
    sanitized = sanitized.replace(" ", "_")
    return sanitized[:32]


def on_key_down(key):
    scene = manager.scene
    if not getattr(scene, "input", False):
        return

    if key == pygame.K_BACKSPACE: # löscht das letzte zeichen im input feld
        scene.input_text = scene.input_text[:-1]
    elif key == pygame.K_RETURN: # eingabe befehl mit enter
        if isinstance(scene, NewGame): # erstellt json bei new game
            save_name = scene.input_text.strip()
            if save_name:
                filename = sanitize_filename(save_name)
                if filename:
                    save_folder = "saved_games"
                    os.makedirs(save_folder, exist_ok=True)
                    save_path = os.path.join(save_folder, f"{filename}.json")

                    if os.path.exists(save_path):
                        counter = 1
                        while True:
                            alt_path = os.path.join(save_folder, f"{filename}_{counter}.json")
                            if not os.path.exists(alt_path):
                                save_path = alt_path
                                break
                            counter += 1

                    save_data = {
                    "name": "test1",
                    "created": 9383,
                    "resources": {
                        "electricity": 70,
                        "metal": 40,
                        "minerals": 85,
                        "water": 20,
                        "communication": 55,
                        "money": 123456,
                        "science": 67890
                    },
                    "resource_max": {
                        "electricity": 100,
                        "metal": 100,
                        "minerals": 100,
                        "water": 100,
                        "communication": 100
                    },
                    "progress": {}
                    }

                    with open(save_path, "w", encoding="utf-8") as save_file:
                        json.dump(save_data, save_file, indent=2)

                    scene.current_save_path = save_path
                    print(f"Created save file: {save_path}")
        elif isinstance(scene, ContinueGame): # läd json bei continue game
            save_name = scene.input_text.strip()
            if save_name:
                filename = sanitize_filename(save_name)
                save_path = os.path.join("saved_games", f"{filename}.json")
                if os.path.exists(save_path):
                    print(f"Continuing game from {save_path}...")
                else:
                    print(f"No save file found for: {save_name}")
        else:
            print("Entered:", scene.input_text)
    elif key == pygame.K_SPACE: # fügt ein Leerzeichen hinzu, solange die maximale Länge von 32 Zeichen nicht überschritten wird
        if len(scene.input_text) < 32:
            scene.input_text += " "
    else: # fügt das gedrückte zeichen hinzu, solange es verfügbar ist und die maximale Länge von 32 Zeichen nicht überschritten wird
        char = pygame.key.name(key)
        if len(char) == 1 and char.isprintable():
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                char = char.upper()
            if len(scene.input_text) < 32:
                scene.input_text += char

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