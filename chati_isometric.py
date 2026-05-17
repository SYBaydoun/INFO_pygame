# Pygame Zero Isometric Heightmap 
from opensimplex import OpenSimplex
import pgzrun
import pygame
import random

WIDTH = 1200
HEIGHT = 800

TILE_WIDTH = 128
TILE_HEIGHT = 64

OFFSET_X = WIDTH // 2
OFFSET_Y = 600

HEIGHT_STEP = 52

camera_x = 0
camera_y = 0
speed = 0.1

noise = OpenSimplex(random.randint(0, 1_000_000))


MAP_SIZE = 10

tilemap = [
    [0 for x in range(MAP_SIZE)] for y in range(MAP_SIZE)
]


tiles = {
    0: "surface_bottom",
    1: "surface_light",
    2: "surface_medium",
    3: "surface_dark",
}

resources = {
    "electricity": {"current": 70, "max": 100},
    "metal": {"current": 40, "max": 100},
    "minerals": {"current": 85, "max": 100},
    "water": {"current": 20, "max": 100},
}
icon_size = (24, 24)
resource_icons = {
    "electricity": pygame.transform.scale(images.load("icon_electricity"), icon_size),
    "metal": pygame.transform.scale(images.load("icon_metal"), icon_size),
    "minerals": pygame.transform.scale(images.load("icon_minerals"), icon_size),
    "water": pygame.transform.scale(images.load("icon_water"), icon_size),

}
money_icon = pygame.transform.scale(images.load("icon_money"), icon_size)
science_icon = pygame.transform.scale(images.load("icon_science"), icon_size)
money = 123456
science = 67890

resource_colors = {
    "electricity": (255, 220, 50),
    "metal": (180, 180, 180),
    "minerals": (120, 200, 120),
    "water": (80, 160, 255),
}
resource_colors_empty = {
    "electricity": (255, 255, 100),
    "metal": (220, 220, 220),
    "minerals": (150, 220, 150),
    "water": (100, 180, 255),
}

scaled_tiles = {}

for tile_id, image_name in tiles.items():
    original = images.load(image_name)
    scaled_tiles[tile_id] = pygame.transform.scale(original, (128, 128))


TRANSITION_WIDTH = 3
BASE_SIZE_X = len(tilemap[0])
BASE_SIZE_Y = len(tilemap[1])


def get_height(x, y):

    inside_base = (
        0 <= x < BASE_SIZE_X and
        0 <= y < BASE_SIZE_Y
    )

    # 1. FIXE 10x10 FLÄCHE
    if inside_base:
        return 0

    # 2. NOISE TARGET
    n = noise.noise2(x * 0.03, y * 0.03)

    if n < -0.8:
        target = 0
    elif n < -0.65:
        target = 1
    elif n < -0.4:
        target = 2
    else:
        target = 3

    # 3. DISTANZ ZUR BASISFLÄCHE
    dx = max(0, x - (BASE_SIZE_X - 1))
    dy = max(0, y - (BASE_SIZE_Y - 1))
    dist = max(dx, dy)

    if dist <= 3:
        t = dist / 3  # 0 → 1 über 3 Tiles
        return int(0 + (target - 0) * t)

    # 4. REST DER WELT
    return target

def iso_to_screen(x, y):

    x -= camera_x
    y -= camera_y

    y = -y
    x = -x

    screen_x = (x - y) * (TILE_WIDTH // 2)
    screen_y = (x + y) * (TILE_HEIGHT // 2)

    screen_x += OFFSET_X
    screen_y += OFFSET_Y

    return screen_x, screen_y

def cam_movement():
    global camera_x, camera_y

    if keyboard.w:
        camera_y += speed
        camera_x += speed

    if camera_x - speed >= 0 and camera_y - speed >= 0: #so wird die map nicht von der cam verlassen
        if keyboard.s:
            camera_y -= speed
            camera_x -= speed

    if camera_y - speed >= 0:
        if keyboard.a:
            camera_x += speed
            camera_y -= speed

    if camera_x - speed >= 0:
        if keyboard.d:
            camera_x -= speed
            camera_y += speed

def draw():

    screen.fill((40, 40, 60))

    for y in reversed(range(int(camera_y)-20, int(camera_y)+20)):
        for x in reversed(range(int(camera_x)-20, int(camera_x)+20)):
            if x >= 0 and y >= 0:
                h = get_height(x, y)

                base_x, base_y = iso_to_screen(x, y)

                for level in range(int(h) + 1):

                    screen_x = base_x
                    screen_y = base_y - level * HEIGHT_STEP

                    tile = scaled_tiles[min(level, 3)]

                    screen.surface.blit(
                        tile,
                        (screen_x - TILE_WIDTH // 2,
                        screen_y - TILE_HEIGHT // 2)
                    )

    def draw_resource_bar(x, y, resource, data):
        bar_width = 200
        bar_height = 22
        radius = bar_height // 2

        current = data["current"]
        max_v = data["max"]
        ratio = current / max_v

        # COLORS
        bg = (30, 30, 45)
        border = (255, 255, 255)
        fill = resource_colors[resource]

        icon = resource_icons[resource]



        # --- BAR BACKGROUND (capsule) ---
        bar_x = x
        bar_y = y - bar_height // 2

        pygame.draw.rect(
            screen.surface,
            bg,
            (bar_x, bar_y, bar_width, bar_height),
            border_radius=radius
        )

        # --- BAR FILL (capsule clipped) ---
        fill_width = int(bar_width * ratio)

        pygame.draw.rect(
            screen.surface,
            fill,
            (bar_x, bar_y, fill_width, bar_height),
            border_radius=radius
        )

        # --- BORDER ---
        pygame.draw.rect(
            screen.surface,
            border,
            (bar_x, bar_y, bar_width, bar_height),
            2,
            border_radius=radius
        )
            # --- ICON CIRCLE (backplate) ---

        screen.draw.filled_circle(
            (x, y),
            icon_size[0] // 2 + 6,
            (20, 20, 35)
        )

        screen.draw.circle(
            (x, y),
            icon_size[0] // 2 + 4,
            (80, 80, 120)
        )

        # icon itself
        screen.surface.blit(
            icon,
            (x - icon_size[0] // 2, y - icon_size[1] // 2)
        )
    
    def draw_top_stats():

        spacing = 80

        money_text = str(money)
        science_text = str(science)

        font_size = 36

        font = pygame.font.SysFont(None, font_size)

        money_width = font.size(money_text)[0]
        science_width = font.size(science_text)[0]

        icon_w = icon_size[0]

        total_width = (
            money_width +
            icon_w +
            spacing +
            icon_w +
            science_width
        )

        start_x = WIDTH // 2 - total_width // 2
        y = 40

        # ---------- MONEY ----------
        money_text_x = start_x

        screen.draw.text(
            money_text,
            (money_text_x, y - 18),
            fontsize=font_size,
            color=(255, 220, 80)
        )

        money_icon_x = money_text_x + money_width + 20

        screen.draw.filled_circle(
            (money_icon_x, y),
            icon_size[0] // 2 + 6,
            (20, 20, 35)
        )

        screen.draw.circle(
            (money_icon_x, y),
            icon_size[0] // 2 + 4,
            (80, 80, 120)
        )

        screen.surface.blit(
            money_icon,
            (
                money_icon_x - icon_size[0] // 2,
                y - icon_size[1] // 2
            )
        )

        # ---------- SCIENCE ----------
        science_icon_x = money_icon_x + spacing

        screen.draw.filled_circle(
            (science_icon_x, y),
            icon_size[0] // 2 + 6,
            (20, 20, 35)
        )

        screen.draw.circle(
            (science_icon_x, y),
            icon_size[0] // 2 + 4,
            (80, 80, 120)
        )

        screen.surface.blit(
            science_icon,
            (
                science_icon_x - icon_size[0] // 2,
                y - icon_size[1] // 2
            )
        )

        screen.draw.text(
            science_text,
            (science_icon_x + 20, y - 18),
            fontsize=font_size,
            color=(120, 220, 255)
        )
    
    ui_x = 40
    ui_y = HEIGHT - 50
    spacing = 240

    for i, (resource, data) in enumerate(resources.items()):
        x = ui_x + i * spacing
        draw_resource_bar(x, ui_y, resource, data)
    
    draw_top_stats()


def update():
    cam_movement()

pgzrun.go()