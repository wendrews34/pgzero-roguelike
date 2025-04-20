import pgzrun
import random
import math
from pygame.rect import Rect

# Configurações do jogo
WIDTH = 800
HEIGHT = 600
TILE_SIZE = 40

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)

# Menu Principal
menu_active = True
start_button = Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
music_button = Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
exit_button = Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50)
music_on = True

# Jogo
game_active = False
player = None
enemies = []
treasure = None
map_data = []
level = 1
items = []
game_over = False
victory = False

# Sons
music.play("dungeon")

# Classes
class Entity(Actor):
    def __init__(self, image, pos, speed):
        super().__init__(image, pos)
        self.speed = speed
        self.frame = 0
        self.animation_timer = 0

    def animate(self, images, duration):
        self.animation_timer += 1
        if self.animation_timer > duration:
            self.frame = (self.frame + 1) % len(images)
            self.image = images[self.frame]
            self.animation_timer = 0

class Player(Entity):
    def __init__(self, pos):
        super().__init__("explorer0", pos, 5)
        self.images = ["explorer0", "explorer1", "explorer2", "explorer3"]
        self.power = 1

    def move(self, dx, dy):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        if is_valid_position(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.animate(self.images, 5)

class Enemy(Entity):
    def __init__(self, pos):
        super().__init__("enemy0", pos, 3)
        self.images = ["enemy0", "enemy1", "enemy2", "enemy3"]
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    def update(self):
        dx, dy = self.direction
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        if is_valid_position(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.animate(self.images, 10)
        else:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

class FastEnemy(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.speed = 6
        self.image = "fast_enemy0"
        self.images = ["fast_enemy0", "fast_enemy1", "fast_enemy2", "fast_enemy3"]

class Item(Actor):
    def __init__(self, image, pos):
        super().__init__(image, pos)

# Funções do jogo
def generate_map():
    global map_data
    map_data = [[1 for _ in range(WIDTH // TILE_SIZE)] for _ in range(HEIGHT // TILE_SIZE)]
    for _ in range(50 + level * 10):
        x = random.randint(1, WIDTH // TILE_SIZE - 2)
        y = random.randint(1, HEIGHT // TILE_SIZE - 2)
        map_data[y][x] = 0

def place_entities():
    global player, enemies, treasure, items
    player_pos = find_empty_tile()
    player = Player(player_pos)
    treasure_pos = find_empty_tile()
    treasure = Actor("treasure", treasure_pos)
    enemies = [Enemy(find_empty_tile()) for _ in range(3 + level)]
    enemies.extend([FastEnemy(find_empty_tile()) for _ in range(level)])
    items = [Item("potion", find_empty_tile()) for _ in range(level)]

def find_empty_tile():
    while True:
        x = random.randint(0, WIDTH // TILE_SIZE - 1)
        y = random.randint(0, HEIGHT // TILE_SIZE - 1)
        if map_data[y][x] == 0:
            return (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)

def is_valid_position(x, y):
    grid_x = int(x // TILE_SIZE)
    grid_y = int(y // TILE_SIZE)
    return 0 <= grid_x < WIDTH // TILE_SIZE and 0 <= grid_y < HEIGHT // TILE_SIZE and map_data[grid_y][grid_x] == 0

def draw_map():
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            if tile == 1:
                screen.blit("wall", (x * TILE_SIZE, y * TILE_SIZE))

def draw_menu():
    screen.fill(BLACK)
    screen.draw.text("Roguelike Game", center=(WIDTH // 2, HEIGHT // 4), color=WHITE, fontsize=60)
    screen.draw.filled_rect(start_button, GRAY)
    screen.draw.text("Start", center=start_button.center, color=WHITE, fontsize=30)
    screen.draw.filled_rect(music_button, GRAY)
    screen.draw.text("Music: " + ("On" if music_on else "Off"), center=music_button.center, color=WHITE, fontsize=30)
    screen.draw.filled_rect(exit_button, GRAY)
    screen.draw.text("Exit", center=exit_button.center, color=WHITE, fontsize=30)

def draw_game():
    draw_map()
    player.draw()
    treasure.draw()
    for enemy in enemies:
        enemy.draw()
    for item in items:
        item.draw()

def draw_game_over():
    screen.fill(BLACK)
    if victory:
        screen.draw.text("Victory!", center=(WIDTH // 2, HEIGHT // 2), color=WHITE, fontsize=60)
    else:
        screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2), color=RED, fontsize=60)

def update():
    global game_over, victory, level
    if game_active:
        for enemy in enemies:
            enemy.update()
            if player.colliderect(enemy):
                game_over = True
        for item in items:
            if player.colliderect(item):
                player.power += 1
                items.remove(item)
        if player.colliderect(treasure):
            level += 1
            if level > 3:
                game_over = True
                victory = True
            else:
                generate_map()
                place_entities()

def on_mouse_down(pos):
    global menu_active, game_active, music_on, game_over, victory, level
    if menu_active:
        if start_button.collidepoint(pos):
            menu_active = False
            game_active = True
            generate_map()
            place_entities()
        elif music_button.collidepoint(pos):
            music_on = not music_on
            if music_on:
                music.unpause()
            else:
                music.pause()
        elif exit_button.collidepoint(pos):
            exit()
    elif game_over:
        game_over = False
        victory = False
        level = 1
        game_active = True
        generate_map()
        place_entities()

def on_key_down(key):
    if game_active and not game_over:
        if key == keys.W:
            player.move(0, -1)
        elif key == keys.S:
            player.move(0, 1)
        elif key == keys.A:
            player.move(-1, 0)
        elif key == keys.D:
            player.move(1, 0)

def draw():
    if menu_active:
        draw_menu()
    elif game_active:
        if not game_over:
            draw_game()
        else:
            draw_game_over()

pgzrun.go()