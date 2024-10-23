import pygame as pg
import random as ran
import sys

# Initialize Pygame
pg.init()
pg.font.init()

# Game Screen Config
WIDTH = 800
HEIGHT = 600
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.DOUBLEBUF)
pg.display.set_caption('Asteroid Shooter')

# Background sound
pg.mixer.music.load(r'D:\Game Dev\Talent Hub Class\Sesi 7\assets\space.mp3')
pg.mixer.music.set_volume(0.5)

# SFX
collision_sound = pg.mixer.Sound(r'D:\Game Dev\Talent Hub Class\Sesi 7\assets\explosion.mp3')
collision_sound.set_volume(0.5)
laser_sound = pg.mixer.Sound(r'D:\Game Dev\Talent Hub Class\Sesi 7\assets\laser.mp3')
laser_sound.set_volume(0.3)

# Parallax Background
backgrounds = [
    pg.image.load(r'D:\Game Dev\Talent Hub Class\Sesi 7\assets\prx-1.png').convert_alpha(),
    pg.image.load(r'D:\Game Dev\Talent Hub Class\Sesi 7\assets\prx-2.png').convert_alpha(),
    pg.image.load(r'D:\Game Dev\Talent Hub Class\Sesi 7\assets\prx-3.png').convert_alpha(),
    pg.image.load(r'D:\Game Dev\Talent Hub Class\Sesi 7\assets\prx-4.png').convert_alpha(),
    pg.image.load(r'D:\Game Dev\Talent Hub Class\Sesi 7\assets\prx-5.png').convert_alpha(),
]

# Parallax speed config
speeds = [0.1, 0.3, 0.5, 0.7, 0.9]
opacities = [255, 220, 200, 180, 160]

# Set Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Set FPS
FPS = 60
clock = pg.time.Clock()

# Global variables
highest_score = 0
current_level = 1
score_threshold = 5  # Score to increase level

# Laser Config
class Laser(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.image.load(r'D:\Game Dev\Talent Hub Class\Sesi 7\assets\Player_Laser.png').convert_alpha()
        self.image = pg.transform.smoothscale(self.image, (10, 30))  # Adjust the size of the laser
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -10  # Laser moves upwards

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()  # Remove the laser if it goes off-screen

# Player Config
class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load(r'D:\Game Dev\Talent Hub Class\Sesi 7\assets\player_1.png').convert_alpha()
        self.image = pg.transform.smoothscale(self.image, (70, 70))  
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-20, -20)  
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 6

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_a] and self.rect.left > 0:  # Move left
            self.rect.x -= self.speed
        if keys[pg.K_d] and self.rect.right < WIDTH:  # Move right
            self.rect.x += self.speed
        if keys[pg.K_w] and self.rect.top > 0:  # Move up
            self.rect.y -= self.speed
        if keys[pg.K_s] and self.rect.bottom < HEIGHT:  # Move down
            self.rect.y += self.speed

    def shoot(self):
        # Create and shoot a laser from the player's position
        laser = Laser(self.rect.centerx, self.rect.top - 10)  # Adjust position to spawn above the player
        all_sprites.add(laser)
        lasers.add(laser)
        pg.mixer.Sound.play(laser_sound)

# Enemies Config
class Enemy(pg.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image = pg.image.load(r'D:\Game Dev\Talent Hub Class\Sesi 7\assets\asteroid.png').convert_alpha()
        self.image = pg.transform.smoothscale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-20, -20)
        self.rect.x = ran.randint(0, WIDTH - 75)
        self.rect.y = ran.randint(-100, -50)
        self.speed = ran.randint(3, 5) + level  # Increase speed based on level
        self.health = 100 + (level * 20)  # Increase health based on level

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = ran.randint(0, WIDTH - 75)
            self.rect.y = ran.randint(-100, -50)
            self.speed = ran.randint(2, 7) + current_level  # Adjust speed for new enemies

# Function to display text
def draw_text(text, font, color, x, y):
    screen_text = font.render(text, True, color)
    screen.blit(screen_text, (x, y))

# Function for drawing buttons
def draw_button(text, x, y, w, h, inactive_color, active_color, action=None):
    mouse = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pg.draw.rect(screen, active_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pg.draw.rect(screen, inactive_color, (x, y, w, h))

    font = pg.font.SysFont(None, 40)
    text_surf = font.render(text, True, WHITE)
    screen.blit(text_surf, (x + (w / 4), y + (h / 4)))

# Function to restart the game
def restart_game():
    start_game()

# Function to draw each layer of the background with vertical scrolling (parallax)
def draw_backgrounds(scroll_y):
    for i, background in enumerate(backgrounds):
        surface = pg.Surface(background.get_size(), pg.SRCALPHA)
        surface.blit(background, (0, 0))
        surface.set_alpha(opacities[i])

        # Repeat background with vertical scrolling
        relative_y = scroll_y * speeds[i] % background.get_rect().height
        screen.blit(surface, (0, relative_y - background.get_rect().height))
        screen.blit(surface, (0, relative_y))

# Function to start the game
def start_game():
    global highest_score, current_level  # Using global variables

    # Play background music
    pg.mixer.music.play(-1)

    # Initialize sprite groups
    global all_sprites, lasers  # Declare the groups globally
    all_sprites = pg.sprite.Group()
    enemies = pg.sprite.Group()
    lasers = pg.sprite.Group()  # Group for lasers

    # Create Player
    player = Player()
    all_sprites.add(player)

    # Create initial enemies based on the level
    for i in range(5):
        enemy = Enemy(current_level)
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Create Score and Time
    score = 0
    start = pg.time.get_ticks()
    game_over = False
    scroll_y = 0

    # Game Loop
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:  # If the space key is pressed, shoot laser
                    player.shoot()

        if not game_over:
            all_sprites.update()

            # Check if the player collides with an enemy
            hits = pg.sprite.spritecollide(player, enemies, False)
            if hits:
                game_over = True
                game_over_time = (pg.time.get_ticks() - start) // 1000

                if score > highest_score:
                    highest_score = score  # Update highest score

                # Play collision sound effect
                pg.mixer.Sound.play(collision_sound)

            # Check for laser collisions with enemies
            enemy_hits = pg.sprite.groupcollide(enemies, lasers, False, True)
            for enemy in enemy_hits:
                enemy.health -= 50  # Deal damage to enemy
                if enemy.health <= 0:
                    score += 1  # Increase score for destroying an enemy
                    enemy.kill()  # Remove enemy
                    new_enemy = Enemy(current_level)  # Respawn a new enemy based on level
                    all_sprites.add(new_enemy)
                    enemies.add(new_enemy)

            # Level up logic
            if score >= current_level * score_threshold:  # Level up every score_threshold points
                current_level += 1

            # Score based on time
            score = (pg.time.get_ticks() - start) // 1000

        # Update background scrolling
        scroll_y += 2
        draw_backgrounds(scroll_y)

        # Display Score and Level
        font = pg.font.SysFont(None, 30)
        if game_over:
            text = font.render(f"Game Over! Final Score: {game_over_time}", True, WHITE)
            screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2))
            highest_score_text = font.render(f"Highest Score: {highest_score}", True, WHITE)
            screen.blit(highest_score_text, (WIDTH // 2 - 150, HEIGHT // 2 + 40))
            draw_button("Restart Game", WIDTH // 4, HEIGHT // 2 + 100, 400, 60, BLUE, RED, restart_game)
        else:
            text = font.render(f"Score: {score} | Level: {current_level}", True, WHITE)
            screen.blit(text, (10, 10))
            highest_score_text = font.render(f"Highest Score: {highest_score}", True, WHITE)
            screen.blit(highest_score_text, (WIDTH - 200, 10))

        # Update all sprites
        if not game_over:
            all_sprites.draw(screen)

        pg.display.flip()
        clock.tick(FPS)

# Function to create the main menu
def main_menu():
    scroll_y = 0
    menu = True
    while menu:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.mixer.music.stop()
                pg.quit()
                return

        scroll_y += 2  # Speed of vertical scrolling for the menu
        draw_backgrounds(scroll_y)

        font = pg.font.SysFont(None, 60)
        draw_text("Asteroid Shooter", font, WHITE, WIDTH // 3.5, HEIGHT // 4)

        # Display Start button
        draw_button("Start Game", WIDTH // 3.5, HEIGHT // 2, 350, 60, BLUE, RED, start_game)

        pg.display.flip()

# Start the game from the main menu
main_menu()
pg.quit()
