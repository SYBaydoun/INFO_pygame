import pgzrun
import pygame

WIDTH = 600
HEIGHT = 800

pygame.font.init()
fonts = pygame.font.get_fonts()
text = "Click to scroll through fonts"
offset = 0

def draw():
    screen.fill("black")

    for i, f in enumerate(fonts):
        y = 10 + i * 30 - offset

        if -30 < y < HEIGHT:
            try:
                font = pygame.font.SysFont(f, 20)
                text_surface = font.render(f+"_FeiniSpaceAgency", True, (255, 220, 80))
                screen.surface.blit(text_surface, (100, y))
            except:
                print(f"Could not load font: {f}")
def on_mouse_down(pos, button):
    global offset
    if button == mouse.WHEEL_UP:
        offset -= 20
    elif button == mouse.WHEEL_DOWN:
        offset += 20

def update():
    pass

pgzrun.go()

widelatin
broadway
magneto
maturascriptcapitals

screen.draw.text(
    money_text,
    (start_x, y - 18),
    fontsize=font_size,
    color=(255, 220, 80)
)

