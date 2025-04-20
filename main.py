import pgzrun
import pygame
from pygame import Rect
import random
import sys

# Configurações da tela
WIDTH = 800
HEIGHT = 600
GRAVITY = 1  # Simulação simples de gravidade

class Hero(Actor):
    def __init__(self, pos):
        super().__init__("hero_idle_0", pos=pos) # Imagem inicial
        self.images_idle = ["hero_idle_0", "hero_idle_1"] # Lista de sprites para animação ociosa
        self.images_move = ["hero_move_0", "hero_move_1"] # Lista de sprites para animação de movimento
        self.animation_timer = 0
        self.animation_speed = 5 # Controla a velocidade da animação (quantos frames por troca de sprite)
        self.current_animation = "idle"
        self.frame_index = 0
        self.velocity_y = 0
        self.facing_right = True
        self.vx = 0

    def update(self):
        self.animate()
        self.apply_gravity()
        self.move_and_collide(platforms)

    def animate(self):
        if self.current_animation == "idle":
            images = self.images_idle
        elif self.current_animation == "move":
            images = self.images_move

        if self.animation_timer > self.animation_speed:
            self.frame_index = (self.frame_index + 1) % len(images)
            self.image = images[self.frame_index]
            self.animation_timer = 0
        else:
            self.animation_timer += 1

    def move(self, direction):
        if direction == "left":
            self.vx = -5
            self.current_animation = "move"
            self.facing_right = False
        elif direction == "right":
            self.vx = 5
            self.current_animation = "move"
            self.facing_right = True
        elif direction == "idle":
            self.vx = 0
            self.current_animation = "idle"

    def jump(self):
        if self.velocity_y == 0:
            self.velocity_y = -15 # Força do salto
            sounds.jump.play()

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.y += self.velocity_y

    def move_and_collide(self, platforms):
        self.y += self.velocity_y
        on_ground = False
        for platform in platforms:
            if self.colliderect(platform):
                if self.velocity_y > 0:
                    self.bottom = platform.top
                    self.velocity_y = 0
                    on_ground = True
                elif self.velocity_y < 0:
                    self.top = platform.bottom
                    self.velocity_y = 0
        if not on_ground:
            self.current_animation = "idle" # Podemos mudar para uma animação de "caindo" depois
        self.x += self.vx
        # Manter o herói dentro dos limites da tela (opcional)
        if self.left < 0:
            self.left = 0
        elif self.right > WIDTH:
            self.right = WIDTH

class Enemy(Actor):
    def __init__(self, pos, left_boundary, right_boundary):
        super().__init__("enemy_idle_0", pos=pos) # Placeholder image
        self.left_boundary = left_boundary
        self.right_boundary = right_boundary
        self.speed = 2
        self.moving_right = True
        self.images_idle = ["enemy_idle_0", "enemy_idle_1"] # Placeholder images
        self.animation_timer = 0
        self.animation_speed = 10
        self.frame_index = 0

    def update(self):
        self.move()
        self.animate()

    def move(self):
        if self.moving_right:
            self.x += self.speed
            if self.right > self.right_boundary:
                self.moving_right = False
        else:
            self.x -= self.speed
            if self.left < self.left_boundary:
                self.moving_right = True

    def animate(self):
        if self.animation_timer > self.animation_speed:
            self.frame_index = (self.frame_index + 1) % len(self.images_idle)
            self.image = self.images_idle[self.frame_index]
            self.animation_timer = 0
        else:
            self.animation_timer += 1

# Criação do herói
hero = Hero((WIDTH // 2, HEIGHT - 50))

# Criação das plataformas
platforms = [
    Rect(50, HEIGHT - 30, 200, 30),      # Plataforma no canto inferior esquerdo
    Rect(300, HEIGHT - 100, 300, 30),     # Plataforma no meio
    Rect(650, HEIGHT - 50, 100, 50),      # Pequena plataforma à direita
    Rect(0, HEIGHT - 20, WIDTH, 20)       # Chão
]

# Criação dos inimigos
enemies = [
    Enemy((150, HEIGHT - 60), 100, 250), # Inimigo na primeira plataforma
    Enemy((450, HEIGHT - 130), 350, 550) # Inimigo na plataforma do meio
]

# Estado do jogo
game_state = "menu"
music_enabled = True

# Carregar música e sons
music.play("background_music")
music.set_volume(0.5) # Define um volume inicial (opcional)
sounds.jump = pygame.mixer.Sound("jump.wav")
sounds.game_over = pygame.mixer.Sound("game_over.wav")

# Criação dos botões do menu
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 30)
        self.text_surface = self.font.render(text, True, BLACK)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self):
        screen.draw.rect(self.rect, WHITE)
        screen.blit(self.text_surface, self.text_rect)

    def is_clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        return self.rect.collidepoint(mouse_pos) and mouse_clicked

button_start = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 40, "Iniciar Jogo")
button_music_text = "Música (Ligada)" if music_enabled else "Música (Desligada)"
button_music = Button(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 40, button_music_text)
button_quit = Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 40, "Sair")

def draw():
    screen.fill(BLACK)
    if game_state == "menu":
        button_start.draw()
        button_music.draw()
        button_quit.draw()
    elif game_state == "game":
        hero.draw()
        for platform in platforms:
            screen.draw.rect(platform, (100, 100, 100))
        for enemy in enemies:
            enemy.draw()
    elif game_state == "game_over":
        screen.draw.text("Game Over!", center=(WIDTH // 2, HEIGHT // 2), color=WHITE, fontsize=60)

def update():
    global game_state, music_enabled
    if game_state == "game":
        hero.update()
        for enemy in enemies:
            enemy.update()
            if hero.colliderect(enemy):
                game_state = "game_over"
                sounds.game_over.play()
    elif game_state == "menu":
        if music_enabled and not music.is_playing:
            music.play("background_music")
        elif not music_enabled and music.is_playing:
            music.stop()

def on_key_down(key):
    global game_state
    if game_state == "game":
        if key == pygame.K_SPACE:
            hero.jump()

def on_key_up(key):
    if game_state == "game":
        hero.move("idle")

def on_mouse_down(pos):
    global game_state, music_enabled, button_music
    if game_state == "menu":
        if button_start.is_clicked():
            game_state = "game"
            if music_enabled and not music.is_playing:
                music.play("background_music")
        elif button_music.is_clicked():
            music_enabled = not music_enabled
            button_music_text = f"Música ({'Ligada' if music_enabled else 'Desligada'})"
            button_music = Button(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 40, button_music_text)
            if music_enabled and not music.is_playing:
                music.play("background_music")
            else:
                music.stop()
        elif button_quit.is_clicked():
            sys.exit()
    elif game_state == "game_over":
        pass
pgzrun.go()