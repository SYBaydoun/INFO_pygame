from opensimplex import OpenSimplex
import random
import pgzrun
import pygame
import os
import json
import time
from collections.abc import Callable

# öffnet das verfluchte Fenster zentriert, warum auch immer das nicht automatisch passiert
os.environ['SDL_VIDEO_CENTERED'] = '1'

# ===== GAME WINDOW CONFIGURATION =====
WIDTH  = 1200
HEIGHT = 800
TITLE = "FeiniSpaceAgency"

# ===== UI TEXT =====
creditMsg = "Game developed by:\nShahin Youssef Baydoun\nIdea by:\nMe\nGraphics by:\nMyself\nTested by:\nand I\nMoralische Unterstützung:\nAlinchen Bienchen :)\ntest"

# ===== MENU ITEM CONFIGURATION =====
menuLibrary = {"menu_items": ["Start New Game", "Continue Game", "Settings", "Credits", "Quit"],
               "new_items": ["Back"],
               "continue_items": ["Back"],
               "settings_items": ["Back", "Audio", "Video", "Controls"],
               "credits_items": ["Back"]
               }

# ===== GAME VARS =====

offset = 0 #mausrat offset
MAP_SIZE = 10
icon_size = (24, 24)
TILE_WIDTH = 128
TILE_HEIGHT = 64
OFFSET_X = WIDTH // 2 #anfangs x position isometric koordinatenursprung
OFFSET_Y = 600 #anfangs y position isometric koordinatenursprung
HEIGHT_STEP = 52 #verticales spacing <- nicht 64, damit dahinterliegende niedrigere blöcke gesehen werden können

# ===== MAP AND TILESET =====
tilemap = [[0 for x in range(MAP_SIZE)] for y in range(MAP_SIZE)]

tiles = {
    0: "surface_bottom",
    1: "surface_light",
    2: "surface_medium",
    3: "surface_dark",
}

# ===== LOAD PLACEBLE MODULS =====
solar = pygame.image.load("images/solar.png")
base = pygame.image.load("images/base.png")
rocket = pygame.image.load("images/rocket.png")
miner = pygame.image.load("images/miner.png")
antenne = pygame.image.load("images/antenne.png")

# ===== LOAD & SCALE PLANET IMAGES =====
PLANETEN_SIZE = 250
PLANET_Y_OFFSET = 100
PLANET_LOCKED_ALPHA = 130 # alphawert für gesperrte planeten

planet_kyra = pygame.image.load("images/planet03.png")
planet_maya = pygame.image.load("images/planet04.png")
planet_olga = pygame.image.load("images/planet05.png")
planet_nell = pygame.image.load("images/planet06.png")
planet_sina = pygame.image.load("images/planet08.png")
planet_cesar = pygame.image.load("images/planet09.png")

planet_kyra = pygame.transform.scale(planet_kyra, (PLANETEN_SIZE, PLANETEN_SIZE))
planet_maya = pygame.transform.scale(planet_maya, (PLANETEN_SIZE, PLANETEN_SIZE))
planet_olga = pygame.transform.scale(planet_olga, (PLANETEN_SIZE, PLANETEN_SIZE))
planet_nell = pygame.transform.scale(planet_nell, (PLANETEN_SIZE, PLANETEN_SIZE))
planet_sina = pygame.transform.scale(planet_sina, (PLANETEN_SIZE, PLANETEN_SIZE))
planet_cesar = pygame.transform.scale(planet_cesar, (PLANETEN_SIZE, PLANETEN_SIZE))

planet_maya.set_alpha(PLANET_LOCKED_ALPHA)
planet_olga.set_alpha(PLANET_LOCKED_ALPHA)
planet_nell.set_alpha(PLANET_LOCKED_ALPHA)
planet_kyra.set_alpha(PLANET_LOCKED_ALPHA)
planet_cesar.set_alpha(PLANET_LOCKED_ALPHA)

padlock = pygame.image.load("images/padlock.png")
padlock = pygame.transform.scale(padlock, (PLANETEN_SIZE // 2, PLANETEN_SIZE // 2))

# ===== LOAD & SCALE ROCKET MODULS =====
rocket_moduls = {}
for file in os.listdir("images/rocket_moduls"):
    path = os.path.join("images/rocket_moduls", file)
    modul = pygame.image.load(path)
    orig_width = modul.get_width()
    orig_height = modul.get_height()

    #bestimmt grösse je nach modul grösse
    if "_smal" in file or "steuer" in file:
        scale = [40 / orig_width]
    elif "_medium" in file:
        scale = [60 / orig_width]
    elif "medium-" in file:
        scale = [56 / orig_width ] 
    elif "trenner" in file:
        scale = [40 / orig_width, 56 / orig_width, 80 / orig_width]
    else:
        scale = [80 / orig_width]
    
    #kreirt grössen für jeden faktor, falls ein png für mehrere grössen
    for i, sc in enumerate(scale):
        modul = pygame.transform.scale(modul, (orig_width * sc, orig_height * sc))
        rocket_moduls[f"{file}{i}"] = modul

# ===== LOAD & SCALE FSA_LOGO =====
fsa_logo = pygame.image.load("images/fsa_logo_o.png")
fsa_logo = pygame.transform.scale(fsa_logo, (500, 500))
fsa_logo.set_alpha(200)

# ===== GAME STATE VARS =====
#variablen wo ders spielstand der json datei gespeichert, manipuliert und dann wieder in die json gepuscht wird beim speichern
save_path = None
save_data = {}
controlls = {}

# ===== MODULE STATS & RESOURCE CHANGES =====
stats_change_libary = {
    "solar": {"resources": {"electricity": 4, "metal": -10, "minerals": -5, "water": 0, "communication": 0, "money": -100, "science": 0},
              "resource_max": {"electricity": 4, "metal": 0, "minerals": 0, "water": 0, "communication": 0},
              },
    "base": {"resources": {"electricity": -2, "metal": -30, "minerals": -10, "water": -10, "communication": 0, "money": -200, "science": 0},
             "resource_max": {"electricity": 0, "metal": 20, "minerals": 4, "water": 5, "communication": 0},
             },
    "rocket": {"resources": {"electricity": -10, "metal": -50, "minerals": -20, "water": -50, "communication": 0, "money": -500, "science": 0},
               "resource_max": {"electricity": 0, "metal": 0, "minerals": 0, "water": 0, "communication": 0},
               },
    "miner": {"resources": {"electricity": -10, "metal": -20, "minerals": 0, "water": -10, "communication": -5, "money": -150, "science": 0},
              "resource_max": {"electricity": 0, "metal": 0, "minerals": 0, "water": 0, "communication": 0},
              "mining": {"electricity": [10,10], "metal": [20, 50], "minerals": [2, 7], "water": [10, 15], "communication": [5,5], "money": [0,0], "science": [0,0]}
              },
    "antenne": {"resources": {"electricity": -10, "metal": -20, "minerals": -10, "water": 0, "communication": 10, "money": -200, "science": 0},
              "resource_max": {"electricity": 0, "metal": 0, "minerals": 0, "water": 0, "communication": 10},
              },
}


#-------------------------------------------
#Scenen Manager
class SceneManager():
    def __init__(self, start_scene):
        self.scene = start_scene
        self.scene.on_enter()

        self.transitioning = False
        self.phase = 0  # 0 idle, 1 close, 2 hold, 3 open

        self.next_scene = None
        self.t = 0
        self.speed = 1

        # whether to show debug overlay text on screen
        self.debug_overlay = False
        self.dauer_bewegung = 120
        self.dauer_ruhen = 10

    def change_scene(self, new_scene):
        if self.transitioning:
            return

        self.transitioning = True
        self.next_scene = new_scene
        self.phase = 1
        self.t = 0

        global offset
        offset = 0

    def update(self):
        if not self.transitioning:
            self.scene.update()
            return

        self.t += self.speed

        # CLOSE
        if self.phase == 1:
            if self.t >= self.dauer_bewegung:
                if hasattr(self.scene, "on_exit"):
                    self.scene.on_exit()

                self.scene = self.next_scene
                self.scene.on_enter()

                self.phase = 2
                self.t = 0

        # HOLD
        elif self.phase == 2:
            if self.t >= self.dauer_ruhen:
                self.phase = 3
                self.t = 0

        # OPEN
        elif self.phase == 3:
            if self.t >= self.dauer_bewegung:
                self.transitioning = False
                self.phase = 0
                self.t = 0

    def draw(self):
        self.scene.draw()

        # draw debug overlay text on top of the scene when enabled
        if getattr(self, 'debug_overlay', False): # append the stats for the lines
            lines = []
            lines.append(f"Scene: {self.scene.__class__.__name__}")
            if hasattr(self.scene, 'noise'):
                lines.append(f"Seed: {getattr(self.scene.noise, '_seed', 'N/A')}")
            try:
                if isinstance(self.scene, GameHomeBase):
                    lines.append(f"Camera: {self.scene.camera_x:.2f}, {self.scene.camera_y:.2f}")
            except Exception:
                pass
            for resource_max in save_data["resource_max"]:
                lines.append(f"{resource_max}_max: {save_data["resource_max"][resource_max]}")
                lines.append(f"{resource_max}: {save_data["resources"][resource_max]}")
            lines.append(f"sateliten in LEO: {save_data["satelitenLEO"]}")
            lines.append(f"sateliten in GEO: {save_data["satelitenGEO"]}")
            for objects in stats_change_libary:
                for types in stats_change_libary[objects]:
                    lines.append(f"{objects, types}: {stats_change_libary[objects][types]}")

            y = 10
            for line in lines: #positioning of lines
                screen.draw.text(line, (10, y), fontsize=18, color="white")
                y += 20

        if self.transitioning:
            self.draw_doors()

    def on_mouse_down(self, pos, button):
        if self.transitioning:
            return

        if self.debug_overlay and button == mouse.LEFT:
            self.debug_overlay = False
            return

        # Check for scrollable UI - prioritise rocket_menu if it exists
        if button in (mouse.WHEEL_UP, mouse.WHEEL_DOWN):
            if hasattr(self.scene, 'rocket_menu') and self.scene.rocket_menu and self.scene.rocket_menu.visible:
                if self.scene.rocket_menu.scrollable_ui:
                    self.scene.rocket_menu.scrollable_ui.handle_scroll(button)
            elif hasattr(self.scene, "scrollable_ui") and self.scene.scrollable_ui:
                self.scene.scrollable_ui.handle_scroll(button)
        # normale klicks
        if button == mouse.LEFT and hasattr(self.scene, "on_mouse_down"):
            self.scene.on_mouse_down(pos, button)
        elif button == mouse.MIDDLE and hasattr(self.scene, "on_mouse_middle_down"):
            self.scene.on_mouse_middle_down(pos, button)
        elif button == mouse.RIGHT and hasattr(self.scene, "on_button_right_down"):
            self.scene.on_mouse_right_down(pos, button)
        else:
            return

    def draw_doors(self):
        duration = 60

        if self.phase == 1:
            progress = min(self.t / duration, 1)
            if self.t == 1:
                door_sound.play()
        elif self.phase == 2:
            progress = 1
        else:
            progress = 1 - min(self.t / duration, 1)
            if self.t == 1:
                door_sound.play()

        progress = progress * progress * (3 - 2 * progress)

        top_h = door_top.get_height()
        bottom_h = door_bottom.get_height()

        top_y = -top_h + top_h * progress
        bottom_y = HEIGHT - bottom_h * progress

        screen.blit(door_top, (0, top_y))
        screen.blit(door_bottom, (0, bottom_y))


#-------------------------------------------
#Inhalte die sich oft wiederholen wie Buttons, Icons, etc.

#Buttons
class Button():
    def __init__(self, text: str, center: tuple, width: int = 300, height: int = 50, border_radius: int = 15, target_alpha_a: int = 140, target_alpha_b: int = 220, r_inside: int = 25, g_inside: int = 35, b_inside: int = 70, r_outline: int = 120, g_outline: int = 170, b_outline: int = 255, tooltip_text: str | None = None):
        #inhalt
        self.text = text
        self.tooltip_text = tooltip_text

        #position und größe
        self.width = width
        self.height = height
        self.border_radius = border_radius
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = center

        # Animationen
        #-> transparenz des buttons
        self.alpha = target_alpha_a
        self.target_alpha = target_alpha_a
        self.target_alpha_a = target_alpha_a
        self.target_alpha_b = target_alpha_b

        #-> transparenz des glows
        self.glow_alpha = 0
        self.target_glow = 0

        #-> vertikale verschiebung des buttons
        self.offset_y = 0
        self.target_offset_y = 0

        # rgb werte inside und outside
        self.r_inside = r_inside
        self.g_inside = g_inside
        self.b_inside = b_inside
        self.r_outline = r_outline
        self.g_outline = g_outline
        self.b_outline = b_outline

    def update(self):
        mouse_pos = pygame.mouse.get_pos()

        hovered = self.rect.collidepoint(mouse_pos)

        if hovered:
            self.target_alpha = self.target_alpha_b
            self.target_glow = 180
            self.target_offset_y = -3
            if self.tooltip_text:
                tooltip.show(self.tooltip_text, owner=self)
        else:
            self.target_alpha = self.target_alpha_a
            self.target_glow = 0
            self.target_offset_y = 0
            if self.tooltip_text:
                tooltip.hide(owner=self)

        speed = 0.12 # speed of transitioning of hover effeect

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

        # inner
        pygame.draw.rect(
            button_surface,
            (self.r_inside, self.g_inside, self.b_inside, int(self.alpha)),
            (0, 0, width, height),
            border_radius=self.border_radius
        )

        # Outline
        pygame.draw.rect(
            button_surface,
            (self.r_outline, self.g_outline, self.b_outline, min(int(self.glow_alpha), 120)),
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
    
    def set_position(self, pos):
        self.rect.center = pos

#Button gruppe die sich scrollen lässt
class ScrollableButtons():
    def __init__(self):
        self.buttons = []
        self.upper_bound = 0
        self.lower_bound = 0
        self.offset = 0
        self.scroll_speed = 20

    def add_button(self, text):
        self.buttons.append(Button(text, (WIDTH // 2, 0)))

    def handle_scroll(self, button):
        if button == mouse.WHEEL_UP:
            self.offset = max(self.offset - self.scroll_speed, 0)

        elif button == mouse.WHEEL_DOWN:
            self.offset += self.scroll_speed

    def update(self):
        for btn in self.buttons:
            btn.update()

    def draw(self):
        for i, button in enumerate(self.buttons):
            y = self.upper_bound + i * 70 - self.offset

            # culling (nur sichtbare Buttons zeichnen)
            if self.upper_bound <= y <= self.lower_bound:
                button.set_position((WIDTH // 2, y))
                button.draw()

    def on_click(self, pos):
        for i, button in enumerate(self.buttons):
            y = self.upper_bound + i * 70 - self.offset

            if self.upper_bound <= y <= self.lower_bound:
                button.set_position((WIDTH // 2, y))
                if button.clicked(pos):
                    return button.text

        return None
    
    def update(self):
        for btn in self.buttons:
            btn.update()

#Button mit Icon statt Text
class IconButton(Button):
    def __init__(self, center: tuple, icon, text: str = "", width: int = 50, height: int = 50, border_radius: int = 25, alpha: int = 255, r_inside: int = 50, g_inside: int = 70, b_inside: int = 140):
        super().__init__(text, center, width, height, border_radius, target_alpha_a=alpha, target_alpha_b=alpha, r_inside=r_inside, g_inside=g_inside, b_inside=b_inside)
        self.icon = icon

    def draw(self):
        super().draw()

        if self.icon:
            screen.surface.blit(
                self.icon,
                (self.rect.x + 10, self.rect.centery - self.icon.get_height() // 2 + self.offset_y)
            )
    
    def update(self):
        super().update()
    
    def clicked(self, pos):
        return super().clicked(pos)
    
    def set_position(self, pos):
        super().set_position(pos)

#Icons
class Icon():
    def __init__(self, source, position, size=icon_size, bg_color=(20, 20, 35), border_color=(80, 80, 120)):
        if isinstance(source, str):
            source = images.load(source)
        self.image = pygame.transform.scale(source, size)
        self.position = position
        self.size = size
        self.bg_color = bg_color
        self.border_color = border_color

    def draw(self):
        x, y = self.position
        radius = self.size[0] // 2 + 6

        screen.draw.filled_circle((x, y), radius, self.bg_color)
        screen.draw.circle((x, y), self.size[0] // 2 + 4, self.border_color)
        screen.surface.blit(
            self.image,
            (x - self.size[0] // 2, y - self.size[1] // 2)
        )

    def set_position(self, position):
        self.position = position

    def move(self, dx, dy):
        x, y = self.position
        self.position = (x + dx, y + dy)

#Build Menu in der HomeBase Szene
class BuildMenu():
    def __init__(self, items: list[str], actions: list[Callable] | None = None):
        self.items = items
        self.actions = self._normalize_actions(actions)
        self.visible = False
        self.rect = pygame.Rect(0, 0, 240, 380)
        self.rect.topright = (WIDTH - 10, 10)
        self.buttons: list[Button] = []
        self.setup_buttons()
    def _normalize_actions(self, actions):
        if actions is None:
            return [None] * len(self.items)
        elif len(actions) < len(self.items):
            return actions + [None] * (len(self.items) - len(actions))
        else:
            return actions[:len(self.items)]

    def setup_buttons(self):
        self.buttons.clear()
        for i, text in enumerate(self.items):
            center = (
                self.rect.left + self.rect.width // 2,
                self.rect.top + 90 + i * 60
            )
            button = Button(
                text,
                center,
                width=self.rect.width - 20,
                height=44,
                border_radius=12,
                target_alpha_a=120,
                target_alpha_b=220,
                r_inside=40,
                g_inside=55,
                b_inside=70,
                r_outline=120,
                g_outline=190,
                b_outline=255
            )
            self.buttons.append(button)

    def set_items(self, items: list[str], actions: list[Callable] | None = None):
        self.items = items
        self.actions = self._normalize_actions(actions)
        self.setup_buttons()

    def add_item(self, text: str, action: Callable | None = None):
        self.items.append(text)
        self.actions.append(action)
        self.setup_buttons()

    def toggle(self):
        self.visible = not self.visible

    def open(self):
        self.visible = True

    def close(self):
        self.visible = False

    def draw(self):
        if not self.visible:
            return

        pygame.draw.rect(screen.surface, (20, 20, 30, 220), self.rect, border_radius=12)
        pygame.draw.rect(screen.surface, (140, 180, 230), self.rect, 2, border_radius=12)
        screen.draw.text(
            "Build Menu",
            (self.rect.left + 16, self.rect.top + 16),
            fontsize=26,
            color="white"
        )

        for button in self.buttons:
            button.draw()

    def update(self):
        if not self.visible:
            return

        for button in self.buttons:
            button.update()

    def handle_click(self, pos):
        if not self.visible:
            return None

        for i, button in enumerate(self.buttons):
            if button.clicked(pos):
                action = self.actions[i] if i < len(self.actions) else None
                if action:
                    action()
                return button.text

        return None

#Rocket Menu in HomeBase -> zum starten von raketen
class RocketMenu():
    def __init__(self, items: list[str | list[str]], title: str):
        self.items = items
        self.title = title
        self.visible = False
        self.rect = pygame.Rect(0, 0, 400, 300)
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.scrollable_ui = ScrollableButtons()
        self.scrollable_ui.upper_bound = HEIGHT // 2 - 50
        self.scrollable_ui.lower_bound = HEIGHT // 2 + 100

        for item in self.items:
            text = f"{item[0]} -> {item[1]}" if isinstance(item, list) else item
            self.scrollable_ui.add_button(text)
    
    def is_click_inside(self, pos):
        return self.rect.collidepoint(pos)

    def toggle(self):
        self.visible = not self.visible

    def open(self):
        self.visible = True

    def close(self):
        self.visible = False
    def draw(self):
        if not self.visible:
            return
        pygame.draw.rect(screen.surface, (0, 9, 64), self.rect, border_radius=12)
        screen.draw.text(self.title, center=(self.rect.centerx, self.rect.top + 40), fontsize=30, fontname=menu_font(), color="white")
        
        self.scrollable_ui.draw()

    def update(self):
        if not self.visible:
            return
        self.scrollable_ui.update()
    
    def on_mouse_down(self):
        if self.scrollable_ui:
            self.scrollable_ui.on_click()
    
#Tooltip leider noch nicht implementet -> kann ignoriert werden
class ToolTip():
    def __init__(self, objeckt=None, text="", font_size: int = 22, padding: int = 12, bg_color=(20, 20, 30, 220), outline_color=(140, 180, 230), text_color="white", border_radius: int = 12, offset=(16, 16)):
        self.objeckt = objeckt
        self.text = text
        self.font_size = font_size
        self.padding = padding
        self.bg_color = bg_color
        self.outline_color = outline_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.offset = offset
        self.visible = False
        self.owner = None
        self.rect = pygame.Rect(0, 0, 0, 0)

    def show(self, text=None, owner=None):
        if text is not None:
            self.text = text
        self.visible = True
        self.owner = owner

    def hide(self, owner=None):
        if owner is None or owner == self.owner:
            self.visible = False
            self.owner = None

    def set_text(self, text):
        self.text = text

    def update(self):
        if not self.visible or not self.text:
            return

        lines = self.text.split("\n")
        font = pygame.font.SysFont(None, self.font_size)
        line_height = font.get_linesize()
        widths = [font.size(line)[0] for line in lines]

        width = max(widths, default=0) + self.padding * 2
        height = len(lines) * line_height + self.padding * 2

        mouse_x, mouse_y = pygame.mouse.get_pos()
        x = mouse_x + self.offset[0]
        y = mouse_y + self.offset[1]

        if x + width > WIDTH:
            x = mouse_x - self.offset[0] - width
        if y + height > HEIGHT:
            y = mouse_y - self.offset[1] - height

        x = max(0, x)
        y = max(0, y)

        self.rect = pygame.Rect(x, y, width, height)

    def draw(self):
        if not self.visible or not self.text:
            return

        lines = self.text.split("\n")
        font = pygame.font.SysFont(None, self.font_size)
        line_height = font.get_linesize()

        tooltip_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        tooltip_surface.fill(self.bg_color)
        pygame.draw.rect(tooltip_surface, self.outline_color, tooltip_surface.get_rect(), 2, border_radius=self.border_radius)
        screen.surface.blit(tooltip_surface, self.rect.topleft)

        for i, line in enumerate(lines):
            screen.draw.text(
                line,
                (self.rect.left + self.padding, self.rect.top + self.padding + i * line_height),
                fontsize=self.font_size,
                color=self.text_color
            )


#-------------------------------------------
#Vererbende Class Für die Menü Szenen
class MenuSzene():
    def __init__(self, items:str, buttons:str, draw_bg:str, title:str, text: str = "", input: bool = False,scrollable: bool = False, scrollableItems: list[str] = []):
        self.items = menuLibrary[items]
        self.buttons = []
        self.draw_bg = draw_bg
        self.title = title
        self.text = text
        self.input = input
        self.input_text = ""
        self.scrollable = scrollable
        self.scrollableItems = scrollableItems
        self.scrollable_ui = None
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
        screen.blit(fsa_logo, (WIDTH // 2 - 250, 180))
        #screen.blit(fsa_logo, (WIDTH - 200, 10))
        screen.draw.text(
            self.title,
            center=(WIDTH // 2, 120),
            fontsize=60,
            color="white",
            owidth=3,
            ocolor="#ff7300",
            fontname=menu_font()
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
        
        if self.scrollable and self.scrollable_ui is None:
            self.scrollable_ui = ScrollableButtons()
            for item in self.scrollableItems:
                self.scrollable_ui.add_button(item)

                if self.input:
                    self.scrollable_ui.upper_bound = start_y + 100
                else:
                    self.scrollable_ui.upper_bound = start_y + 20
                self.scrollable_ui.lower_bound = min(start_y + 400, HEIGHT - 100)

                self.scrollable_ui.update()
                self.scrollable_ui.draw()

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
    
    def on_mouse_down(self, pos, button):
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
    
    def on_mouse_down(self, pos, button):
        for button in self.buttons:
            if button.clicked(pos):
                if button.text == "Back":
                    manager.change_scene(Menu())

#Szene Spiel fortsetzen
class ContinueGame(MenuSzene):
    def __init__(self):
        super().__init__("continue_items", "continue_buttons", "bg_continue.jpg", "Continue Game", input=True, scrollable=True, scrollableItems=[filename for filename in os.listdir("saved_games") if filename.endswith(".json")])

    def on_mouse_down(self, pos, button):
        for button in self.buttons:
             if button.clicked(pos):
                if button.text == "Back":
                    manager.change_scene(Menu())

        if self.scrollable_ui:
            result = self.scrollable_ui.on_click(pos)
            if result:
                manager.change_scene(GameHomeBase(save_path=os.path.join("saved_games", result)))

    def update(self):
        super().update()
        if self.scrollable_ui:
            self.scrollable_ui.update()

    def draw(self):
        super().draw()
        if self.scrollable_ui:
            self.scrollable_ui.draw()

#Szene Einstellungen
class Settings(MenuSzene):
    def __init__(self):
        super().__init__("settings_items", "settings_buttons", "bg_settings.jpg", "Settings")

    def on_mouse_down(self, pos, button):
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
    
    def on_mouse_down(self, pos, button):
        for button in self.buttons:
             if button.clicked(pos):
                if button.text == "Back":
                    manager.change_scene(Menu())


#-------------------------------------------
#Vererbende Class Für Game
class GameScene():

    def __init__(self, save_path):
        self.save_path = save_path

        if not self.save_path:
            raise ValueError("GameScene requires a valid save_path")

        global save_data
        current_global_save_path = globals().get("save_path")
        if not save_data or self.save_path != current_global_save_path:
            save_data = load_save(self.save_path)
            globals()["save_path"] = self.save_path

        self.noise = OpenSimplex(save_data["seed"])

        self.resources = {
            "electricity": {
                "current": save_data["resources"]["electricity"],
                "max": save_data["resource_max"]["electricity"]
            },

            "metal": {
                "current": save_data["resources"]["metal"],
                "max": save_data["resource_max"]["metal"]
            },

            "minerals": {
                "current": save_data["resources"]["minerals"],
                "max": save_data["resource_max"]["minerals"]
            },

            "water": {
                "current": save_data["resources"]["water"],
                "max": save_data["resource_max"]["water"]
            },

            "communication": {
                "current": save_data["resources"]["communication"],
                "max": save_data["resource_max"]["communication"]
            }
        }

        self.money = save_data["resources"]["money"]
        self.science = save_data["resources"]["science"]

        self.ui_y = HEIGHT - 50
        self.ui_rects = []

        self.resource_icons = {
            "electricity": pygame.transform.scale(images.load("icon_electricity"), icon_size),
            "metal": pygame.transform.scale(images.load("icon_metal"), icon_size),
            "minerals": pygame.transform.scale(images.load("icon_minerals"), icon_size),
            "water": pygame.transform.scale(images.load("icon_water"), icon_size),
            "communication": pygame.transform.scale(images.load("icon_communication"), icon_size),
        }

        self.money_icon = pygame.transform.scale(images.load("icon_money"), icon_size)
        self.science_icon = pygame.transform.scale(images.load("icon_science"), icon_size)

        self.left_corner_button = IconButton((40, 40), self.get_lcorner_button_icon())
        self.right_corner_button = IconButton((WIDTH - 40, 40), self.get_rcorner_button_icon())

        self.resource_colors = {
            "electricity": (255, 220, 50),
            "metal": (180, 180, 180),
            "minerals": (120, 200, 120),
            "water": (80, 160, 255),
            "communication": (200, 120, 255),
        }

        # Satellite resource generation timer
        self.satellite_resource_timer = 0
        self.satellite_resource_interval = 36000  # 10 minutes at 60 FPS

    def refresh_resources(self):
        global save_data
        self.resources["electricity"]["current"] = save_data["resources"]["electricity"]
        self.resources["electricity"]["max"] = save_data["resource_max"]["electricity"]
        self.resources["metal"]["current"] = save_data["resources"]["metal"]
        self.resources["metal"]["max"] = save_data["resource_max"]["metal"]
        self.resources["minerals"]["current"] = save_data["resources"]["minerals"]
        self.resources["minerals"]["max"] = save_data["resource_max"]["minerals"]
        self.resources["water"]["current"] = save_data["resources"]["water"]
        self.resources["water"]["max"] = save_data["resource_max"]["water"]
        self.resources["communication"]["current"] = save_data["resources"]["communication"]
        self.resources["communication"]["max"] = save_data["resource_max"]["communication"]
        self.money = save_data["resources"]["money"]
        self.science = save_data["resources"]["science"]


    def draw_resource_bar(self, x, y, resource):

        bar_width = 200
        bar_height = 22
        radius = bar_height // 2

        current = self.resources[resource]["current"]
        max_v = self.resources[resource]["max"]

        ratio = current / max_v if max_v else 0

        bg = (30, 30, 45)
        border = (255, 255, 255)
        fill = self.resource_colors[resource]

        pygame.draw.rect(
            screen.surface,
            bg,
            (x, y - bar_height // 2, bar_width, bar_height),
            border_radius=radius
        )

        fill_width = int(bar_width * ratio)

        pygame.draw.rect(
            screen.surface,
            fill,
            (x, y - bar_height // 2, fill_width, bar_height),
            border_radius=radius
        )

        pygame.draw.rect(
            screen.surface,
            border,
            (x, y - bar_height // 2, bar_width, bar_height),
            2,
            border_radius=radius
        )

        Icon(self.resource_icons[resource], (x, y)).draw()

    def draw_resource_bars(self):

        bar_width = 200
        spacing = 240

        count = len(self.resources)
        total_width = (count - 1) * spacing + bar_width

        start_x = WIDTH // 2 - total_width // 2

        for i, resource in enumerate(self.resources.keys()):
            x = start_x + i * spacing
            self.draw_resource_bar(x, self.ui_y, resource)

    def draw_top_stats(self):

        spacing = 80

        money_text = str(self.money)
        science_text = str(self.science)

        font_size = 36
        font = pygame.font.SysFont(None, font_size)

        money_width = font.size(money_text)[0]
        science_width = font.size(science_text)[0]
        icon_w = icon_size[0]

        total_width = money_width + icon_w + spacing + icon_w + science_width
        start_x = WIDTH // 2 - total_width // 2

        y = 40

        # MONEY
        screen.draw.text(
            money_text,
            (start_x, y - 18),
            fontsize=font_size,
            color=(255, 220, 80)
        )

        money_icon_x = start_x + money_width + 20
        Icon(self.money_icon, (money_icon_x, y)).draw()

        # SCIENCE
        science_icon_x = money_icon_x + spacing
        Icon(self.science_icon, (science_icon_x, y)).draw()

        screen.draw.text(
            science_text,
            (science_icon_x + 20, y - 18),
            fontsize=font_size,
            color=(120, 220, 255)
        )
    def get_lcorner_button_icon(self):
        if isinstance(self, GameHomeBase):
            return pygame.transform.scale(images.load("icon_blueprint"), (32, 32))
        return pygame.transform.scale(images.load("icon_base"), (32, 32))

    def get_lcorner_button_rect(self):
        rect = pygame.Rect(0, 0, 50, 50)
        rect.center = (40, 40)
        return rect
    def get_rcorner_button_icon(self):
        return pygame.transform.scale(images.load("icon_build"), (32, 32))
    def get_rcorner_button_rect(self):
        rect = pygame.Rect(0, 0, 50, 50)
        rect.center = (WIDTH - 40, 40)
        return rect

    def draw_corner_buttons(self):
        self.left_corner_button.icon = self.get_lcorner_button_icon()
        self.left_corner_button.draw()
        if isinstance(self, GameHomeBase):
            # draw the build menu first so the corner button stays on top
            if hasattr(self, "build_menu"):
                self.build_menu.draw()

            self.right_corner_button.icon = self.get_rcorner_button_icon()
            self.right_corner_button.draw()
            
    def draw_ui(self):
        self.draw_resource_bars()
        self.draw_top_stats()
        self.draw_corner_buttons()

    def generate_satellite_resources(self):
        """Generate resources from satellites in orbit"""
        global save_data
        
        # LEO satellite resources per satellite
        leo_resources = {
            "electricity": 0,
            "metal": 0,
            "minerals": 0,
            "water": 0,
            "communication": 0,
            "money": 30,
            "science": 10
        }
        
        # GEO satellite resources per satellite
        geo_resources = {
            "electricity": 0,
            "metal": 0,
            "minerals": 0,
            "water": 0,
            "communication": 0,
            "money": 100,
            "science": 50
        }
        
        # Process LEO satellites
        leo_count = save_data.get("satelitenLEO", 0)
        for resource, amount in leo_resources.items():
            total = amount * leo_count
            if resource in save_data["resources"]:
                save_data["resources"][resource] += total
            elif resource == "money":
                save_data["resources"]["money"] += total
            elif resource == "science":
                save_data["resources"]["science"] += total
        
        # Process GEO satellites
        geo_count = save_data.get("satelitenGEO", 0)
        for resource, amount in geo_resources.items():
            total = amount * geo_count
            if resource in save_data["resources"]:
                save_data["resources"][resource] += total
            elif resource == "money":
                save_data["resources"]["money"] += total
            elif resource == "science":
                save_data["resources"]["science"] += total
        
        print(f"Generated resources from {leo_count} LEO and {geo_count} GEO satellites")
        self.refresh_resources()

    def draw(self):
        pass

    def update(self):
        self.left_corner_button.update()
        self.right_corner_button.update()
        if hasattr(self, "build_menu"):
            self.build_menu.update()

        # Check satellite resources
        self.satellite_resource_timer += 1
        if self.satellite_resource_timer >= self.satellite_resource_interval:
            self.satellite_resource_timer = 0
            self.generate_satellite_resources()

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def on_mouse_down(self, pos, button):
        if button == mouse.LEFT and self.get_lcorner_button_rect().collidepoint(pos):
            if isinstance(self, GameHomeBase):
                manager.change_scene(GameSketch(save_path=self.save_path))
            elif isinstance(self, GameSketch):
                manager.change_scene(GameHomeBase(save_path=self.save_path))
            else:
                manager.change_scene(GameHomeBase(save_path=self.save_path))
        elif button == mouse.LEFT and self.get_rcorner_button_rect().collidepoint(pos) and isinstance(self, GameHomeBase):
            if hasattr(self, "build_menu"):
                self.build_menu.toggle()
        elif hasattr(self, "build_menu"):
            self.build_menu.handle_click(pos)

#Scene Game Base
class GameHomeBase(GameScene):

    def __init__(self, save_path: str=None):

        super().__init__(save_path)

        self.save_path = save_path

        self.camera_x = 0
        self.camera_y = 0

        self.camera_speed = 0.1

        self.scaled_tiles = {}

        self.solar_scaled = pygame.transform.scale(solar, (128, 128))
        self.base_scaled = pygame.transform.scale(base, (128, 128))
        self.rocket_scaled = pygame.transform.scale(rocket, (256, 256))
        self.miner_scaled = pygame.transform.scale(miner, (256, 256))
        self.antenne_scaled = pygame.transform.scale(antenne, (256, 256))

        self.controlls = controlls
        self.rocket_menu = None
        self.scrollable_ui = None

        self.unlocked_area = self.unlocked_area_border_floodsearch(0, 0, area=True)
        self.unlocked_area_border = self.unlocked_area_border_floodsearch(0, 0, area=False)

        for tile_id, image_name in tiles.items():

            original = images.load(image_name)

            self.scaled_tiles[tile_id] = pygame.transform.scale(
                original,
                (128, 128)
            )

        # libary mit offsets etc. für die placier funktion
        self.buildable_types = {
            "solar": {
                "label": "Solar",
                "icon": self.solar_scaled,
                "save_key": "solar",
                "offset": (-TILE_WIDTH // 2 - 10, -TILE_HEIGHT // 2 - 10)
            },
            "base": {
                "label": "Base",
                "icon": self.base_scaled,
                "save_key": "base",
                "offset": (-TILE_WIDTH // 2, -TILE_HEIGHT // 2)
            },
            "rocket": {
                "label": "Rocket",
                "icon": self.rocket_scaled,
                "save_key": "rocket",
                "offset": (-TILE_WIDTH, -TILE_HEIGHT)
            },
            "miner": {
                "label": "Miner",
                "icon": self.miner_scaled,
                "save_key": "miner",
                "offset": (-TILE_WIDTH, -TILE_HEIGHT * 7 // 4)
            },
            "antenne": {
                "label": "Antenne",
                "icon": self.antenne_scaled,
                "save_key": "antenne",
                "offset": (-TILE_WIDTH, -TILE_HEIGHT)
            },

        }

        self.placed_objects: dict[str, list[tuple[int, int]]] = self.load_saved_placements()
        self.placing: dict | None = None

        # placing movement delay (in seconds) - adjustable to control speed
        self.placing_move_delay = 0.15  # change this to adjust movement speed (e.g., 0.1 = fast, 0.5 = slow)
        self.placing_last_move_time = 0.0  # timestamp of last movement

        self.build_menu = BuildMenu(
            [entry["label"] for entry in self.buildable_types.values()],
            [lambda object_type=object_type: self.start_placement(object_type) for object_type in self.buildable_types.keys()]
        )

        self.camera_speed = 0.1

        self.scaled_tiles = {}

        self.solar_scaled = pygame.transform.scale(solar, (128, 128))
        self.base_scaled = pygame.transform.scale(base, (128, 128))
        self.rocket_scaled = pygame.transform.scale(rocket, (256, 256))
        self.miner_scaled = pygame.transform.scale(miner, (256, 256))
        self.antenne_scaled = pygame.transform.scale(antenne, (256, 256))

        self.controlls = controlls

        for tile_id, image_name in tiles.items():

            original = images.load(image_name)

            self.scaled_tiles[tile_id] = pygame.transform.scale(
                original,
                (128, 128)
            )

    def start_placement(self, object_type: str):
        self.placing = {
            "type": object_type,
            "x": int(self.camera_x),
            "y": int(self.camera_y)
        }
        self.placing_last_move_time = time.time()  # reset movement timer on new placement
        self.build_menu.close()

    def load_saved_placements(self) -> dict[str, list[tuple[int, int]]]:
        global save_data
        placements: dict[str, list[tuple[int, int]]] = {}
        for object_type, info in self.buildable_types.items():
            saved = save_data.get(info["save_key"], {}).get("extra_pos", []) if save_data else []
            placements[object_type] = [tuple(pos) for pos in saved]
        return placements

    def save_placement(self, object_type: str, x: int, y: int):
        save_key = self.buildable_types[object_type]["save_key"]

        if not module_resource_manipulation(save_key):
            return False

        global save_data

        if save_key not in save_data:
            save_data[save_key] = {"number": 0, "extra_pos": []}

        if "extra_pos" not in save_data[save_key]:
            save_data[save_key]["extra_pos"] = []
        
        if "number" not in save_data[save_key]:
            save_data[save_key]["number"] = 0

        save_data[save_key]["extra_pos"].append([x, y])
        save_data[save_key]["number"] += 1

        if "placed_objects" not in save_data:
            save_data["placed_objects"] = []
        
        save_data["placed_objects"].extend(calculate_placementspace(object_type, x, y))
        self.refresh_resources()
        return True

    def get_height(self, x: int, y: int) -> int:
        global save_data
        progress_tuples = [tuple(pos) if isinstance(pos, list) else pos for pos in save_data.get("progress", [])] if save_data else []
        
        inside_base = (
            0 <= x < MAP_SIZE and
            0 <= y < MAP_SIZE
        )

        if inside_base:
            if (x, y) in progress_tuples:
                return 0
            if (5, 5) == (x, y):
                return 1
            return 0

        n = self.noise.noise2(x * 0.03, y * 0.03)

        if n < -0.8:
            target = 0
        elif n < -0.65:
            target = 1
        elif n < -0.4:
            target = 2
        else:
            target = 3

        dx = max(0, x - (MAP_SIZE - 1))
        dy = max(0, y - (MAP_SIZE - 1))

        dist = max(dx, dy)

        if dist <= 3:

            t = dist / 3
            if (x, y) in progress_tuples:
                return 0
            else:
                return int(target * t)
        if (x, y) in progress_tuples:
                return 0
        else:
            return target
    
    #floodsearch algorythmus, der freigelegte area trackt und border
    def unlocked_area_border_floodsearch(self, x: int = 0, y: int = 0, border: list[tuple[int, int]] = None, unlocked: list[tuple[int, int]] = None, area: bool = False) -> list[tuple[int, int]]:
        # Initialize fresh lists if not provided (avoids mutable default argument bug)
        if border is None:
            border = []
        if unlocked is None:
            unlocked = [(0, 0)]
        
        current_height = self.get_height(x, y)

        if current_height != 0:
            return

        neighbors = [
            (x + 1, y),
            (x, y + 1),
            (x - 1, y),
            (x, y - 1)
        ]
        for nx, ny in neighbors:
            if self.get_height(nx, ny) != 0 and (nx, ny) not in border and nx >= 0 and ny >= 0:
                border.append((nx, ny))

            elif self.get_height(nx, ny) == 0 and (nx, ny) not in unlocked and nx >= 0 and ny >= 0:
                unlocked.append((nx, ny))
                self.unlocked_area_border_floodsearch(nx, ny, border, unlocked)
        return unlocked if area else border
    
    def check_mining(self):
        global save_data
        mining_positions = save_data.get("mining_position", []) if save_data else []
        for element in list(mining_positions):
            if element[2] <= time.time(): # prüft die ablaufzeit wann bohrung vollendet ist
                save_data["mining_position"].remove(element)
                save_data["miner"]["number"] -= 1
                save_data["miner"]["extra_pos"].remove([element[0], element[1]])
                save_data["placed_objects"].remove([element[0], element[1]])
                save_data["progress"].append([element[0], element[1]])
                
                # Remove miner from placed_objects dict for rendering
                if "miner" in self.placed_objects and (element[0], element[1]) in self.placed_objects["miner"]:
                    self.placed_objects["miner"].remove((element[0], element[1]))

                miner_return(element)

                self.refresh_resources()
                self.unlocked_area = self.unlocked_area_border_floodsearch(area=True)
                self.unlocked_area_border = self.unlocked_area_border_floodsearch()
            else:
                continue

    # isometrische rechnungen ===>
    def iso_to_screen(self, x: int, y: int) -> float:

        x -= self.camera_x
        y -= self.camera_y

        y = -y
        x = -x

        screen_x = (x - y) * (TILE_WIDTH // 2)
        screen_y = (x + y) * (TILE_HEIGHT // 2)

        screen_x += OFFSET_X
        screen_y += OFFSET_Y

        return screen_x, screen_y
    
    def screen_to_iso(self, sx: int, sy: int):
        # Remove screen offsets
        sx -= OFFSET_X
        sy -= OFFSET_Y

        # Undo the matrix transform
        x = (sx / (TILE_WIDTH / 2) + sy / (TILE_HEIGHT / 2)) / 2
        y = (sy / (TILE_HEIGHT / 2) - sx / (TILE_WIDTH / 2)) / 2

        # Undo the sign flips
        x = -x
        y = -y

        # Add camera offset back
        x += self.camera_x
        y += self.camera_y

        return x, y
    # <===

    def draw(self):
        screen.fill((40, 40, 60))

        #zeichnet tiles nur dann wenn sie sichtbar sein müssen
        for y in reversed(range(int(self.camera_y) - 20, int(self.camera_y) + 20)):
            for x in reversed(range(int(self.camera_x) - 20, int(self.camera_x) + 20)):
                if x >= 0 and y >= 0:
                    h = self.get_height(x, y)
                    base_x, base_y = self.iso_to_screen(x, y)

                    for level in range(int(h) + 1):
                        screen_x = base_x
                        screen_y = base_y - level * HEIGHT_STEP

                        tile = self.scaled_tiles[min(level, 3)]

                        screen.surface.blit(
                            tile,
                            (
                                screen_x - TILE_WIDTH // 2,
                                screen_y - TILE_HEIGHT // 2
                            )
                        )
        
        #plazierung der start solarmodul fläche
        eckpunkte = save_data["start_modul_pos"]["solar"]
        x_min, y_min, x_max, y_max = koordinaten_netz(eckpunkte)
        
        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                screen_x, screen_y = self.iso_to_screen(x, y)

                screen.surface.blit(
                    self.solar_scaled,
                    (
                        screen_x - TILE_WIDTH // 2 - 10, # -10 weil die solarzellen kleiner sind und deswegen richtig positionert werden müssen
                        screen_y - TILE_HEIGHT // 2 - 10
                    )
                )

        # draw placed objects
        for object_type, positions in self.placed_objects.items():
            if object_type not in self.buildable_types:
                continue
            info = self.buildable_types[object_type]
            icon = info["icon"]
            offset_x, offset_y = info.get("offset", (-TILE_WIDTH // 2, -TILE_HEIGHT // 2))
            for sx, sy in positions:
                h = self.get_height(sx, sy)
                screen_x, screen_y = self.iso_to_screen(sx, sy)
                screen.surface.blit(
                    icon,
                    (screen_x + offset_x, screen_y + offset_y - h * HEIGHT_STEP)
                )

        # draw preview (transparent) if placing
        if self.placing is not None:
            object_type = self.placing.get('type')
            if object_type in self.buildable_types:
                info = self.buildable_types[object_type]
                icon = info["icon"].copy()
                offset_x, offset_y = info.get("offset", (-TILE_WIDTH // 2, -TILE_HEIGHT // 2))
                px = int(self.placing['x'])
                py = int(self.placing['y'])
                screen_x, screen_y = self.iso_to_screen(px, py)
                try:
                    icon.set_alpha(120)
                except Exception:
                    pass
                screen.surface.blit(icon, (screen_x + offset_x, screen_y + offset_y))
        
        # startmodule neben solarzellen ===>
        # muss none checken weil so gespeichert wenn die rakete gestartet wird
        if save_data["start_modul_pos"]["rocket"] is not None:
            x, y = save_data["start_modul_pos"]["rocket"]
            screen_x, screen_y = self.iso_to_screen(x, y)
            screen.surface.blit(self.rocket_scaled, (screen_x - TILE_WIDTH, screen_y - TILE_HEIGHT))
        
        x, y = save_data["start_modul_pos"]["base"]
        screen_x, screen_y = self.iso_to_screen(x, y)
        screen.surface.blit(self.base_scaled, (screen_x - TILE_WIDTH // 2, screen_y - TILE_HEIGHT // 2))

        x, y = save_data["start_modul_pos"]["antenne"]
        screen_x, screen_y = self.iso_to_screen(x, y)
        screen.surface.blit(self.antenne_scaled, (screen_x - TILE_WIDTH, screen_y - TILE_HEIGHT))
        # <===

        if self.rocket_menu:
            self.rocket_menu.draw()

        self.draw_ui()

    def update(self):
        super().update()

        # placement mode handling
        if self.placing is not None:
            gm = self.controlls.get('game_base_mechanics', {})
            current_x = int(self.placing['x'])
            current_y = int(self.placing['y'])

            # move with the mapped keys using time-based delay instead of every frame
            current_time = time.time()
            if current_time - self.placing_last_move_time >= self.placing_move_delay:
                moved = False

                # ifbedingungen prüfen ob der move auf ein legales feld im algemeinen fällt, noch keine objektkollision 
                if getattr(keyboard, gm.get('left', ''), False) and ((self.placing['x'] + 1, self.placing['y']) in self.unlocked_area or (self.placing["type"] == "miner" and (self.placing['x'], self.placing['y']) in self.unlocked_area)):
                    self.placing['x'] = current_x + 1
                    moved = True
                elif getattr(keyboard, gm.get('right', ''), False) and ((self.placing['x'] - 1, self.placing['y']) in self.unlocked_area or (self.placing["type"] == "miner" and (self.placing['x'], self.placing['y']) in self.unlocked_area)):
                    self.placing['x'] = current_x - 1
                    moved = True
                elif getattr(keyboard, gm.get('up', ''), False) and ((self.placing['x'], self.placing['y'] + 1) in self.unlocked_area or (self.placing["type"] == "miner" and (self.placing['x'], self.placing['y']) in self.unlocked_area)):
                    self.placing['y'] = current_y + 1
                    moved = True
                elif getattr(keyboard, gm.get('down', ''), False) and ((self.placing['x'], self.placing['y'] - 1) in self.unlocked_area or (self.placing["type"] == "miner" and (self.placing['x'], self.placing['y']) in self.unlocked_area)):
                    self.placing['y'] = current_y - 1
                    moved = True

                if moved:
                    self.placing_last_move_time = current_time

            # place the object when pressing the place key, jetzt auch objectkollisionscheck bevor place
            if getattr(keyboard, gm.get('place', ''), False) and is_space_free(self.unlocked_area, self.unlocked_area_border, self.placing['type'], self.placing['x'], self.placing['y']):
                object_type = self.placing['type']
                x = int(self.placing['x'])
                y = int(self.placing['y'])
                if object_type == "miner" and object_type in self.buildable_types and (x, y) in self.unlocked_area_border:
                    if self.save_placement(object_type, x, y):
                        self.placed_objects.setdefault(object_type, []).append((x, y))
                        global save_data
                        save_data["mining_position"].append([x, y, time.time() + 10 * self.get_height(x, y), self.get_height(x, y)])  # Example: 10 seconds mining time
                        self.placing = None
                elif object_type in self.buildable_types and object_type != "miner":
                    if self.save_placement(object_type, x, y):
                        self.placed_objects.setdefault(object_type, []).append((x, y))
                        self.placing = None

        # camera movement
        if any(getattr(keyboard, key) for key in self.controlls['movement']['boost']):    
            boost = 3
        else:
            boost = 1
        if getattr(keyboard, self.controlls['movement']['up']):
            self.camera_y += self.camera_speed * boost
            self.camera_x += self.camera_speed * boost

        if self.camera_x - self.camera_speed >= 0 and self.camera_y - self.camera_speed >= 0:
            if getattr(keyboard, self.controlls['movement']['down']):
                self.camera_y -= self.camera_speed * boost
                self.camera_x -= self.camera_speed * boost

        if self.camera_y - self.camera_speed >= 0:
            if getattr(keyboard, self.controlls['movement']['left']):
                self.camera_x += self.camera_speed * boost
                self.camera_y -= self.camera_speed * boost

        if self.camera_x - self.camera_speed >= 0:
            if getattr(keyboard, self.controlls['movement']['right']):
                self.camera_x -= self.camera_speed * boost
                self.camera_y += self.camera_speed * boost
        self.check_mining()

        if self.rocket_menu:
            self.rocket_menu.update()
        
    def on_mouse_down(self, pos, button):
        super().on_mouse_down(pos, button)
        
        if button == mouse.LEFT:
            # If rocket menu is visible and click is outside, close it
            if self.rocket_menu and self.rocket_menu.visible:
                if not self.rocket_menu.is_click_inside(pos):
                    self.rocket_menu.close()
                    return
                
                # If click is inside, handle menu clicks
                result = self.rocket_menu.scrollable_ui.on_click(pos)
                if result:
                    # Parse the result to get rocket type and orbit
                    # Result format: "rocket_type -> orbit"
                    parts = result.split(" -> ")
                    if len(parts) == 2:
                        rocket_type, orbit = parts[0].strip(), parts[1].strip()
                        # Launch the rocket with the stored launch position
                        if launch_rocket(rocket_type, orbit, self.rocket_menu.launch_pos):
                            self.rocket_menu.close()
                            self.refresh_resources()
                            write_save_data()  # Save to JSON
                        else:
                            print("Launch failed!")
                return
            
            # rocket menu verfügbare racketenstarts (typ und orbit)
            rocket_modelle = []
            for varianten in save_data["rockets"]:
                if save_data["rockets"][varianten]["GEO"] > 0:
                    rocket_modelle.append([varianten, "LEO"])
                    rocket_modelle.append([varianten, "GEO"])
                elif save_data["rockets"][varianten]["LEO"] > 0:
                    rocket_modelle.append([varianten, "LEO"])
                else:
                    continue
            
            x, y = self.screen_to_iso(pos[0], pos[1])
            if save_data["start_modul_pos"]["rocket"] is not None:
                rr = calculate_placementspace("rocket", save_data["start_modul_pos"]["rocket"][0], save_data["start_modul_pos"]["rocket"][1])
            else:
                rr = []
            for extra in save_data["rocket"]["extra_pos"]:
                temp = calculate_placementspace("rocket", extra[0], extra[1])
                rr.extend(temp)
            
            for pos in rr:
                if abs(pos[0] - x) <= 0.5 and abs(pos[1] - y) <= 0.5:
                    index = rr.index(pos)
                    rocket_pos = rr[index - index % 4] # verweist auf die wurzel der vier blockierten koordinaten, wo die rackete gespeichert ist
                    self.rocket_menu = RocketMenu(rocket_modelle, f"Rocket at {rocket_pos}")
                    self.rocket_menu.launch_pos = rocket_pos  # Speichere die Position
                    self.rocket_menu.open()
                    return

#Scene Game Sketch <- leider nicht vollständig implementiert
class GameSketch(GameScene):
    def __init__(self, save_path=None):
        super().__init__(save_path)
        self.save_path = save_path

    def draw(self):
        bliting_bg("bg_blueprint.jpg")
        x1= 0
        x2 = 0
        for filename, modul in rocket_moduls.items():
            if "tr_" in filename:
                screen.blit(modul, (x1, 100))
                x1+=80
            else:
                screen.blit(modul, (x2, 300))
                x2+=80

        # plazieren aller module und überprüfung ob sie zusammen passen visuel
        center_x = WIDTH - 100
        y = 100

        trenner_small = rocket_moduls["trenner.png0"]
        trenner_medium = rocket_moduls["trenner.png1"]
        faring = rocket_moduls["faring_big.png0"]
        steuereinheit = rocket_moduls["steuereinheit.png0"]
        fuel_small = rocket_moduls["fuel_smal.png0"]
        medium_small = rocket_moduls["medium-smal.png0"]
        fuel_medium = rocket_moduls["fuel_medium.png0"]
        tr_Vak_medium = rocket_moduls["tr_Vak_medium.png0"]
        tr_SL_medium = rocket_moduls["tr_SL_medium.png0"]
        screen.blit(faring, (center_x - faring.get_width() // 2, y))
        y+=faring.get_height()
        screen.blit(trenner_small, (center_x - trenner_small.get_width() // 2, y))
        y+=trenner_small.get_height()
        screen.blit(steuereinheit, (center_x - steuereinheit.get_width() // 2, y))
        y += steuereinheit.get_height()
        screen.blit(fuel_small, (center_x - fuel_small.get_width() // 2, y))
        y += fuel_small.get_height()
        screen.blit(medium_small, (center_x - medium_small.get_width() // 2, y))
        y += medium_small.get_height()
        screen.blit(tr_Vak_medium, (center_x - tr_Vak_medium.get_width() // 2, y))
        y+= tr_Vak_medium.get_height()
        screen.blit(trenner_medium, (center_x - trenner_medium.get_width() // 2, y))
        y+= trenner_medium.get_height()
        screen.blit(fuel_medium, (center_x - fuel_medium.get_width() // 2, y))
        y+= fuel_medium.get_height()
        screen.blit(fuel_medium, (center_x - fuel_medium.get_width() // 2, y))
        y+= fuel_medium.get_height()
        screen.blit(fuel_medium, (center_x - fuel_medium.get_width() // 2, y))
        y+= fuel_medium.get_height()
        screen.blit(tr_SL_medium, (center_x - tr_SL_medium.get_width() // 2, y))
        self.draw_ui()

    def update(self):
        super().update()

#Scene Game Map <- leider nicht vollständig implementiert, nur ein planet zur verfügung
class GameMap(GameScene):
    def __init__(self, save_path=None):
        super().__init__(save_path)
        self.save_path = save_path
    
    def draw(self):
        bliting_bg("bg_nightsky.jpg")

        # die planeten bliten
        screen.blit(planet_sina, (WIDTH // 2 - PLANETEN_SIZE // 2, PLANET_Y_OFFSET))
        screen.blit(planet_kyra, (WIDTH // 6 - PLANETEN_SIZE // 2, PLANET_Y_OFFSET))
        screen.blit(planet_maya, (WIDTH * 5 // 6 - PLANETEN_SIZE // 2, PLANET_Y_OFFSET))
        screen.blit(planet_nell, (WIDTH // 2 - PLANETEN_SIZE // 2, HEIGHT - PLANET_Y_OFFSET - PLANETEN_SIZE))
        screen.blit(planet_olga, (WIDTH // 6 - PLANETEN_SIZE // 2, HEIGHT - PLANET_Y_OFFSET - PLANETEN_SIZE))
        screen.blit(planet_cesar, (WIDTH * 5 // 6 - PLANETEN_SIZE // 2, HEIGHT - PLANET_Y_OFFSET - PLANETEN_SIZE))
        screen.blit(padlock, (WIDTH * 5 // 6 - PLANETEN_SIZE // 4, PLANET_Y_OFFSET + PLANETEN_SIZE // 2))
        screen.blit(padlock, (WIDTH // 6 - PLANETEN_SIZE // 4, PLANET_Y_OFFSET + PLANETEN_SIZE // 2))
        screen.blit(padlock, (WIDTH // 2 - PLANETEN_SIZE // 4, HEIGHT - PLANET_Y_OFFSET - PLANETEN_SIZE // 2))
        screen.blit(padlock, (WIDTH // 6 - PLANETEN_SIZE // 4, HEIGHT - PLANET_Y_OFFSET - PLANETEN_SIZE // 2))
        screen.blit(padlock, (WIDTH * 5 // 6 - PLANETEN_SIZE // 4, HEIGHT - PLANET_Y_OFFSET - PLANETEN_SIZE // 2))

        self.draw_ui()
    
    def update(self):
        super().update()


#-------------------------------------------
#Game Over wenn nichts mehr plaziert werden kann
class GameOver():
    def __init__(self):
        pass

    def draw():
        pass
    def update():
        pass


#-------------------------------------------
#Hintergrund laden und skalieren
backgrounds = {}
for filename in os.listdir("images"):
    if filename.startswith("bg_"): #alle bg im spiel starten mit bg_
        path = os.path.join("images", filename)

        bg = pygame.image.load(path)

        orig_width = bg.get_width()
        orig_height = bg.get_height()

        scale = max(WIDTH / orig_width, HEIGHT / orig_height)

        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)

        bg = pygame.transform.smoothscale(bg, (new_width, new_height))

        backgrounds[filename] = bg #speichert die geladenen und skalierten BGs in dem bg dict

#Türen für Transition laden
door_top = pygame.image.load("images/door_top.png")
door_bottom = pygame.image.load("images/door_bottom.png")

#skaliert die türen auf die fenster größe, dabei so verzert das beide richtungen passen -> deswegen pixelart damit es trozdem gut aussieht
def scale_to_half_height_full_width(img):
    return pygame.transform.smoothscale(img, (WIDTH, HEIGHT // 2))

door_top = scale_to_half_height_full_width(door_top)
door_bottom = scale_to_half_height_full_width(door_bottom)

#geräusche der türen
door_sound = pygame.mixer.Sound("sounds/door_open_close.wav")
door_sound.set_volume(0.5)

#Funktion die automatisch die Hintergrundbilder aus der Liste zentriert auf den Bildschirm blitet
def bliting_bg(img: str):
    bg = backgrounds[img]
    screen.blit(bg, ((WIDTH-bg.get_width()) // 2, (HEIGHT-bg.get_height()) // 2))

#Fonts für die Titel der Menu scenen
def menu_font() -> str:
    if isinstance(manager.scene, Menu):
        return "maturasc"
    else:
        return "stencil"
    
#starten eines neuen games
def new_game_logik(current_scene):
    save_name = current_scene.input_text.strip()
    noise = OpenSimplex(random.randint(0, 1_048_575))
    if save_name:
        filename = sanitize_filename(save_name)
        if filename:
            save_folder = "saved_games"
            os.makedirs(save_folder, exist_ok=True)
            save_path_ = os.path.join(save_folder, f"{filename}.json")
            counter = 1
            if os.path.exists(save_path_):  
                while True:
                    alt_path = os.path.join(save_folder, f"{filename}_{counter}.json")
                    if not os.path.exists(alt_path):
                        save_path_ = alt_path
                        break
                    counter += 1
                filename = f"{filename}_{counter}"

            with open("save_format.json", "r", encoding="utf-8") as f:
                save_data_ = json.load(f)
            save_data_["name"] = filename
            save_data_["created"] = time.strftime("%Y%m%d%H%M%S", time.gmtime())
            save_data_["seed"] = noise._seed

            global save_path
            global save_data
            save_path = save_path_
            save_data = save_data_
            print(save_path, save_data)

            with open(save_path_, "w", encoding="utf-8") as save_file:
                json.dump(save_data_, save_file, indent=2)

            current_scene.current_save_path = save_path_
            manager.change_scene(GameHomeBase(save_path=save_path_))

#fortfahren eines games mit json datei
def continue_game_logik(current_scene):
    save_name = current_scene.input_text.strip()
    if save_name:
        filename = sanitize_filename(save_name)
        save_path_ = os.path.join("saved_games", f"{filename}.json")
        if os.path.exists(save_path_): #schreibt json inhalt auf code interne var und läd game mit denen
            global save_path
            global save_data
            save_path = save_path_
            save_data = load_save(save_path)
            manager.change_scene(GameHomeBase(save_path=save_path_))
        else:
            print(f"No save file found for: {save_name}")

#läd json datei automatisch 
def load_save(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

#speichert aktuellen spielstand von codeinterner variable auf json datei
def write_save_data():
    global save_path
    global save_data
    if save_path and save_data:
        with open(save_path, "w", encoding="utf-8") as save_file:
            json.dump(save_data, save_file, indent=2)

controlls = load_save("controlls.json")

#formatiert das attribut für den key vergleich von pygame
def key_attr(inner_dict: str, item: str, outer_dict: str = controlls) -> str:
    return getattr(pygame, outer_dict[inner_dict][item])

#ruft daten aus json datei ab nicht spezifisch für controll datei
def attr_json(file: str, inner_dict: str, item: str) -> int | str | list[int | str | list]:
    outer_dict = load_save(file)
    return outer_dict[inner_dict][item]

#wandelt die eckpunkte im save file format in die einzelnen koordinaten für das viereck um
def koordinaten_netz(eckpunkte: list) -> list:
    return eckpunkte[0][0], eckpunkte[0][1], eckpunkte[1][0], eckpunkte[1][1]

#berechnet alle felder die ein modul beansprucht
def calculate_placementspace(object_type: str, x: int, y: int) -> list[list[int, int]]:
    if object_type == "solar" or object_type == "miner":
        return [[x, y]]
    elif object_type == "base" or object_type == "rocket" or object_type == "antenne":
        return [[x, y], [x - 1, y], [x, y - 1], [x - 1, y - 1]]

#überprüft, ob position genug plaz zum plazieren bietet
def is_space_free(area: list, border: list, object_type: str, x: int, y: int) -> bool:
    global save_data
    checking_koordinates = calculate_placementspace(object_type, x, y)
    placed = save_data.get("placed_objects", []) if save_data else []
    
    # Special handling for miner: must be on border, not in unlocked area
    if object_type == "miner":
        if (x, y) not in border:
            return False
        # Check if already placed
        pos_tuple = (x, y)
        if pos_tuple in placed or [x, y] in placed:
            return False
        return True
    
    # For other objects: validate all placement parts
    for pos in checking_koordinates:
        # Convert list to tuple for comparison if needed
        pos_tuple = tuple(pos) if isinstance(pos, list) else pos
        
        # Check if already placed
        if pos_tuple in placed or list(pos_tuple) in placed:
            return False
        # Check if out of bounds
        if pos[0] < 0 or pos[1] < 0:
            return False
        # Check if all parts are in unlocked area
        if pos_tuple not in area:
            return False
        # Check if in border (not allowed for non-miners)
        if pos_tuple in border:
            return False

    return True

#manipuliert resourcen( /+_max ) mithilfe von stats_change_libary
def module_resource_manipulation(object_type: str) -> bool:
    global save_data
    if not save_data:
        return False

    for resource_max in stats_change_libary[object_type]["resource_max"]: #updatet die max werte
        if save_data["resource_max"][resource_max] + stats_change_libary[object_type]["resource_max"][resource_max] >= 0:
            save_data["resource_max"][resource_max] += stats_change_libary[object_type]["resource_max"][resource_max]
        else:
            return False
        
    for resource in stats_change_libary[object_type]["resources"]: #updatet die resourcen selbst
        if save_data["resources"][resource] + stats_change_libary[object_type]["resources"][resource] >= 0:
            if resource in save_data["resource_max"]:
                print("max")
                if save_data["resources"][resource] + stats_change_libary[object_type]["resources"][resource] > save_data["resource_max"][resource]:
                    print("überfluss")
                    save_data["resources"][resource] = save_data["resource_max"][resource]
                else:
                    print("in limit")
                    save_data["resources"][resource] += stats_change_libary[object_type]["resources"][resource]
            else:
                save_data["resources"][resource] += stats_change_libary[object_type]["resources"][resource]
        else:
            return False

    return True

#rückgabe wenn tile abgebaut wurde
def miner_return(element: list[tuple[int, int, int, int]], change_lib: dict = stats_change_libary):
    global save_data
    for resource in change_lib["miner"]["mining"]:
        change = 0
        print(element)
        if change_lib["miner"]["mining"][resource][0] == change_lib["miner"]["mining"][resource][1]: # wenn die beiden zahlen gleich sind genau diesen wert zurückgeben
            change += random.randint(change_lib["miner"]["mining"][resource][0], change_lib["miner"]["mining"][resource][1])
        else: # sonst addition über anzahl der blöcke die abgebaut wurde mit random wert mit zahlen als grenze
            for _ in range(1, element[3] + 1):
                change += random.randint(change_lib["miner"]["mining"][resource][0], change_lib["miner"]["mining"][resource][1])
                print(_, element[3], change)
        if resource in save_data["resource_max"]:
            if save_data["resources"][resource] + change < save_data["resource_max"][resource]:
                save_data["resources"][resource] += change
            else:
                save_data["resources"][resource] = save_data["resource_max"][resource]
        else:
            save_data["resources"][resource] += change

#checkt alles für raketenstart und führt ihn aus
def launch_rocket(rocket_type: str, orbit: str, lounch_pos: list):
    global save_data
    
    # Check if rocket type exists
    if rocket_type not in save_data["rockets"]:
        print(f"Rocket type {rocket_type} not found!")
        return False
    
    rocket_config = save_data["rockets"][rocket_type]
    
    # Check if orbit has available rockets
    if orbit not in rocket_config or rocket_config[orbit] <= 0:
        print(f"No rockets available for {orbit}!")
        return False
    
    # Get resource costs from the rocket config
    resources_needed = {}
    for resource in ["electricity", "metal", "minerals", "water", "communication", "money", "science"]:
        if resource in rocket_config:
            resources_needed[resource] = rocket_config[resource]
    
    # Check if we have enough resources
    for resource, cost in resources_needed.items():
        current = save_data["resources"].get(resource, 0)
        if current + cost < 0:
            print(f"Not enough {resource}! Need {abs(cost)}, have {current}")
            return False
    
    # Deduct resources
    for resource, cost in resources_needed.items():
        if resource == "electricity":
            continue
        else:
            save_data["resources"][resource] += cost
    
    # Add satellites to the orbit
    sat_key = f"sateliten{orbit}"  # "satelitenLEO" or "satelitenGEO"
    if sat_key not in save_data:
        save_data[sat_key] = 0
    
    # Each rocket can carry multiple satellites
    satellites_per_rocket = rocket_config[orbit]
    save_data[sat_key] += satellites_per_rocket
    
    # Decrease rocket count
    save_data["rocket"]["number"] -= 1
    if lounch_pos == save_data["start_modul_pos"]["rocket"]:
        save_data["start_modul_pos"]["rocket"] = None
    else:
        save_data["rocket"]["extra_pos"].remove(lounch_pos)
    occupied_place = calculate_placementspace("rocket", lounch_pos[0], lounch_pos[1])
    for pos in occupied_place:
        save_data["placed_objects"].remove(pos)

    
    print(f"Successfully launched {rocket_type} to {orbit}!")
    print(f"Satellites in {orbit}: {save_data[sat_key]}")
    
    return True

#setzt die buttonkollision für die szenen um
def on_mouse_down(pos, button):
    manager.on_mouse_down(pos, button)

#regelt den input von eingabefeld von aktiver scene
def sanitize_filename(name: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ ")
    sanitized = "".join(ch for ch in name if ch in allowed).strip()
    sanitized = sanitized.replace(" ", "_")
    return sanitized[:32]

#regestriert und verarbeitet tastaturinput
def on_key_down(key, mod, unicode):
    scene = manager.scene
    global save_path, save_data

    if isinstance(scene, GameScene):#ausführungen wenn im game
        if key == key_attr('extra', 'open_menu'): #öffnet menu und speichert spielstand
            if save_path and save_data:
                write_save_data()
            manager.change_scene(Menu())
        elif key == key_attr('extra', 'toggle_debug'): #debug zahlen toggeln oben links
            try:
                manager.debug_overlay = not getattr(manager, 'debug_overlay', False)
            except Exception:
                manager.debug_overlay = True
        elif key == key_attr('extra', 'screenshot'): #screenshot von aktueler pos
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            pygame.image.save(screen.surface, filename)
            print(f"Screenshot saved as {filename}")
        elif key == key_attr('extra', 'quick_save'): #quicksave
            if save_path and save_data:
                write_save_data()
        elif key == key_attr('extra', 'load_quick_save'): #läd letzten gespeicherten spielstand
            save_data = load_save(save_path)
            if isinstance(scene, GameHomeBase):
                manager.change_scene(GameHomeBase(save_path=scene.save_path))
            elif isinstance(scene, GameSketch):
                manager.change_scene(GameSketch(save_path=scene.save_path))
            elif isinstance(scene, GameMap):
                manager.change_scene(GameMap(save_path=scene.save_path))
        elif key == key_attr('game_scene_switch', 'fwd'): # wechselt szene in 'vorwärtzrichtung'
            if isinstance(scene, GameHomeBase):
                manager.change_scene(GameSketch(save_path=scene.save_path))
            elif isinstance(scene, GameSketch):
                manager.change_scene(GameMap(save_path=scene.save_path))
            elif isinstance(scene, GameMap):
                manager.change_scene(GameHomeBase(save_path=scene.save_path))
        elif key == key_attr('game_scene_switch', 'bck'): # wechselt szene in 'rückwärtzrichtung'
            if isinstance(scene, GameHomeBase):
                manager.change_scene(GameMap(save_path=scene.save_path))
            elif isinstance(scene, GameSketch):
                manager.change_scene(GameHomeBase(save_path=scene.save_path))
            elif isinstance(scene, GameMap):
                manager.change_scene(GameSketch(save_path=scene.save_path))
        # wächselt zu bestimmter szene
        elif key == key_attr('game_scene_switch', 'base') and not isinstance(scene, GameHomeBase):
            manager.change_scene(GameHomeBase(save_path=scene.save_path))
        elif key == key_attr('game_scene_switch', 'sketch') and not isinstance(scene, GameSketch):
            manager.change_scene(GameSketch(save_path=scene.save_path))
        elif key == key_attr('game_scene_switch', 'map') and not isinstance(scene, GameMap):
            manager.change_scene(GameMap(save_path=scene.save_path))

        return

    #ausführungen im menu

    if not getattr(scene, "input", False):
        pass
    elif isinstance(scene, MenuSzene): #eingabe komandos
        if key == key_attr('menu', 'input_back'):
            scene.input_text = scene.input_text[:-1]
            return

        if key == key_attr('menu', 'input_lock'):
            if isinstance(scene, NewGame): #erstellt json bei new game
                new_game_logik(scene)
            elif isinstance(scene, ContinueGame): #läd json bei continue game
                continue_game_logik(scene)
            else:
                print("Entered:", scene.input_text)

            if key == key_attr('menu', 'input_space') and len(scene.input_text) < 32: #eingabe leerzeichen
                scene.input_text += " "
                return

    if unicode: #normale zeicheneingabe
        if len(scene.input_text) < 32:
            scene.input_text += unicode

#-------------------------------------------
#Startet mit dem Hauptmenü
manager = None

tooltip = ToolTip()
manager = SceneManager(Menu())

#initiale draw funktion die die aktuelle Szene zeichnet
def draw():
    screen.clear()
    manager.draw()
    tooltip.draw()

#frames
def update():
    manager.update()
    tooltip.update()

#go
pgzrun.go()