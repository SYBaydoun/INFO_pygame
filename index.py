from opensimplex import OpenSimplex
import random
import pgzrun
import pygame
import os
import json
import time

# öffnet das verfluchte Fenster zentriert, warum auch immer das nicht automatisch passiert
os.environ['SDL_VIDEO_CENTERED'] = '1'

#Parameter
WIDTH  = 1200
HEIGHT = 800

TITLE = "FeiniSpaceAgency"
creditMsg = "Game developed by:\nShahin Youssef Baydoun\nIdea by:\nMe\nGraphics by:\nMyself\nTested by:\nand I\nMoralische Unterstützung:\nAlinchen Bienchen :)\ntest"

#Buttons im Menübereich
menuLibrary = {"menu_items": ["Start New Game", "Continue Game", "Settings", "Credits", "Quit"],
               "new_items": ["Back"],
               "continue_items": ["Back"],
               "settings_items": ["Back", "Audio", "Video", "Controls"],
               "credits_items": ["Back"]
               }

#mausrat offset
offset = 0

#Game Variables
MAP_SIZE = 10
icon_size = (24, 24)
TILE_WIDTH = 128
TILE_HEIGHT = 64

#koordinatenursprungs anfangsposition
OFFSET_X = WIDTH // 2
OFFSET_Y = 600

HEIGHT_STEP = 52 #<- nicht 64, damit dahinterliegende niedrigere blöcke gesehen werden können

tilemap = [
    [0 for x in range(MAP_SIZE)] for y in range(MAP_SIZE)
]

tiles = {
    0: "surface_bottom",
    1: "surface_light",
    2: "surface_medium",
    3: "surface_dark",
}
solar = pygame.image.load("images/solar.png")
base = pygame.image.load("images/base.png")
rocket = pygame.image.load("images/rocket.png")


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

        if self.transitioning:
            self.draw_doors()

    def on_mouse_down(self, pos, button):
        if self.transitioning:
            return

        # nur scrollrad behandeln
        if button in (mouse.WHEEL_UP, mouse.WHEEL_DOWN):
            if hasattr(self.scene, "scrollable_ui") and self.scene.scrollable_ui:
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
        elif self.phase == 2:
            progress = 1
        else:
            progress = 1 - min(self.t / duration, 1)

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
    def __init__(self, text: str, center: tuple, width: int = 300, height: int = 50, border_radius: int = 15, target_alpha_a: int = 140, target_alpha_b: int = 220, r_inside: int = 25, g_inside: int = 35, b_inside: int = 70, r_outline: int = 120, g_outline: int = 170, b_outline: int = 255):
        #inhalt
        self.text = text

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
        else:
            self.target_alpha = self.target_alpha_a
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
        for b in self.buttons:
            b.update()

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
        for button in self.buttons:
            button.update()

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
    def __init__(self, items: list[str]):
        self.items = items
        self.visible = False
        self.rect = pygame.Rect(0, 0, 240, 280)
        self.rect.topright = (WIDTH - 10, 10)
        self.buttons: list[Button] = []
        self.setup_buttons()

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

    def set_items(self, items: list[str]):
        self.items = items
        self.setup_buttons()

    def add_item(self, text: str):
        self.items.append(text)
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

        for button in self.buttons:
            if button.clicked(pos):
                return button.text

        return None


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
                elif button.text.startswith("Save"):
                    print(f"Continuing game from {button.text}...")

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

        state = load_save(self.save_path)
        self.noise = OpenSimplex(state["seed"])

        self.resources = {
            "electricity": {
                "current": state["resources"]["electricity"],
                "max": state["resource_max"]["electricity"]
            },

            "metal": {
                "current": state["resources"]["metal"],
                "max": state["resource_max"]["metal"]
            },

            "minerals": {
                "current": state["resources"]["minerals"],
                "max": state["resource_max"]["minerals"]
            },

            "water": {
                "current": state["resources"]["water"],
                "max": state["resource_max"]["water"]
            },

            "communication": {
                "current": state["resources"]["communication"],
                "max": state["resource_max"]["communication"]
            }
        }

        self.money = state["resources"]["money"]
        self.science = state["resources"]["science"]

        self.ui_y = HEIGHT - 50

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
    def build_menu_rect(self):
        rect = pygame.Rect(0, 0, 200, 300)
        rect.topright = (WIDTH - 10, 10)
        build_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(build_surface, (20, 20, 30, 200), build_surface.get_rect(), border_radius=10)
        screen.surface.blit(build_surface, rect.topleft)
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

    def draw(self):
        pass

    def update(self):
        self.left_corner_button.update()
        self.right_corner_button.update()
        if hasattr(self, "build_menu"):
            self.build_menu.update()

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
            clicked_item = self.build_menu.handle_click(pos)
            if clicked_item:
                print(f"Build menu item clicked: {clicked_item}")

#Scene Game Base
class GameHomeBase(GameScene):

    def __init__(self, save_path: str=None):

        super().__init__(save_path)

        self.build_menu = BuildMenu(["Solar", "Base", "Rocket"])

        self.save_path = save_path

        self.camera_x = 0
        self.camera_y = 0

        self.camera_speed = 0.1

        self.scaled_tiles = {}

        self.solar_scaled = pygame.transform.scale(solar, (128, 128))
        self.base_scaled = pygame.transform.scale(base, (128, 128))
        self.rocket_scaled = pygame.transform.scale(rocket, (256, 256))

        self.controlls = load_save("controlls.json")

        for tile_id, image_name in tiles.items():

            original = images.load(image_name)

            self.scaled_tiles[tile_id] = pygame.transform.scale(
                original,
                (128, 128)
            )

    def get_height(self, x: int, y: int) -> int:

        inside_base = (
            0 <= x < MAP_SIZE and
            0 <= y < MAP_SIZE
        )

        if inside_base:
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

            return int(target * t)

        return target

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

    def draw(self):

        screen.fill((40, 40, 60))

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
        
        eckpunkte = attr_json(self.save_path, "start_modul_pos", "solar")
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
        x, y = attr_json(self.save_path, "start_modul_pos", "rocket")
        screen_x, screen_y = self.iso_to_screen(x, y)
        screen.surface.blit(self.rocket_scaled, (screen_x - TILE_WIDTH, screen_y - TILE_HEIGHT))
        
        x, y = attr_json(self.save_path, "start_modul_pos", "base")
        screen_x, screen_y = self.iso_to_screen(x, y)
        screen.surface.blit(self.base_scaled, (screen_x - TILE_WIDTH // 2, screen_y - TILE_HEIGHT // 2))



        self.draw_ui()

    def update(self):
        super().update()

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

#Scene Game Sketch
class GameSketch(GameScene):

    def __init__(self, save_path=None):

        super().__init__(save_path)

        self.save_path = save_path

    def draw(self):

        bliting_bg("bg_blueprint.jpg")

        self.draw_ui()

    def update(self):
        super().update()

#Scene Game Map
class GameMap(GameScene):
    def __init__(self, save_path=None):
        super().__init__(save_path)
        self.save_path = save_path
    
    def draw(self):
        bliting_bg("bg_settings.jpg")
        self.draw_ui()
    
    def update(self):
        super().update()

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
            save_path = os.path.join(save_folder, f"{filename}.json")
            counter = 1
            if os.path.exists(save_path):  
                while True:
                    alt_path = os.path.join(save_folder, f"{filename}_{counter}.json")
                    if not os.path.exists(alt_path):
                        save_path = alt_path
                        break
                    counter += 1
                filename = f"{filename}_{counter}"

            with open("save_format.json", "r", encoding="utf-8") as f:
                save_data = json.load(f)
            save_data["name"] = filename
            save_data["created"] = time.strftime("%Y%m%d%H%M%S", time.gmtime())
            save_data["seed"] = noise._seed

            with open(save_path, "w", encoding="utf-8") as save_file:
                json.dump(save_data, save_file, indent=2)

            current_scene.current_save_path = save_path
            manager.change_scene(GameHomeBase(save_path=save_path))

#fortfahren eines games mit json datei
def continue_game_logik(current_scene):
    save_name = current_scene.input_text.strip()
    if save_name:
        filename = sanitize_filename(save_name)
        save_path = os.path.join("saved_games", f"{filename}.json")
        if os.path.exists(save_path):
            print(f"Continuing game from {save_path}...")
            manager.change_scene(GameHomeBase(save_path=save_path))
        else:
            print(f"No save file found for: {save_name}")

#läd json datei automatisch 
def load_save(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
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

    if isinstance(scene, GameScene):
        if key == key_attr('extra', 'open_menu'):
            manager.change_scene(Menu())
        elif key == key_attr('extra', 'toggle_debug'):
            print("noise seed:", scene.noise._seed)
            if isinstance(scene, GameHomeBase):
                print("Koordinaten: ", scene.camera_x, ", ", scene.camera_y)
        elif key == key_attr('game_scene_switch', 'fwd'):
            if isinstance(scene, GameHomeBase):
                manager.change_scene(GameSketch(save_path=scene.save_path))
                print(scene)
            elif isinstance(scene, GameSketch):
                manager.change_scene(GameMap(save_path=scene.save_path))
                print(scene)
            elif isinstance(scene, GameMap):
                manager.change_scene(GameHomeBase(save_path=scene.save_path))
                print(scene)
        elif key == key_attr('game_scene_switch', 'bck'):
            if isinstance(scene, GameHomeBase):
                manager.change_scene(GameMap(save_path=scene.save_path))
                print(scene)
            elif isinstance(scene, GameSketch):
                manager.change_scene(GameHomeBase(save_path=scene.save_path))
                print(scene)
            elif isinstance(scene, GameMap):
                manager.change_scene(GameSketch(save_path=scene.save_path))
                print(scene)
        elif key == key_attr('game_scene_switch', 'base') and not isinstance(scene, GameHomeBase):
            manager.change_scene(GameHomeBase(save_path=scene.save_path))
        elif key == key_attr('game_scene_switch', 'sketch') and not isinstance(scene, GameSketch):
            manager.change_scene(GameSketch(save_path=scene.save_path))
        elif key == key_attr('game_scene_switch', 'map') and not isinstance(scene, GameMap):
            manager.change_scene(GameMap(save_path=scene.save_path))

        return


    if not getattr(scene, "input", False):
        pass
    elif isinstance(scene, MenuSzene):
        if key == key_attr('menu', 'input_back'):
            scene.input_text = scene.input_text[:-1]
            return

        if key == key_attr('menu', 'input_lock'):
            if isinstance(scene, NewGame): # erstellt json bei new game
                new_game_logik(scene)
            elif isinstance(scene, ContinueGame): # läd json bei continue game
                continue_game_logik(scene)
            else:
                print("Entered:", scene.input_text)

            if key == key_attr('menu', 'input_space') and len(scene.input_text) < 32:
                scene.input_text += " "
                return

    if unicode:
        if len(scene.input_text) < 32:
            scene.input_text += unicode

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