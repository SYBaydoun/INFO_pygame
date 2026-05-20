"""import pgzrun

def draw():
    pass
def update():
    pass
def on_mouse_down(pos, button):
    print(button)"""
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))

running = True

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(event.button)

pygame.quit()