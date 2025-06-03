import pygame
import random
import asyncio
import platform
import os
from pygame import mixer

pygame.init()
mixer.init()


WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spaceship Shooter")


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


BASE_PATH = r"\python project\Spaceshoot"


try:
    spaceship_path = os.path.join(BASE_PATH, "spaceship.png")
    if not os.path.exists(spaceship_path):
        raise FileNotFoundError(f"spaceship.png not found at {spaceship_path}")
    player_img = pygame.image.load(spaceship_path)
    player_img = pygame.transform.scale(player_img, (50, 50))
    print(f"Successfully loaded spaceship.png from {spaceship_path}")
except Exception as e:
    print(f"Error loading spaceship.png: {e}")
    print("Using fallback green rectangle for player")
    player_img = pygame.Surface((50, 50))
    player_img.fill((0, 255, 0))

try:
    enemy_path = os.path.join(BASE_PATH, "enemy.png")
    background_path = os.path.join(BASE_PATH, "space_background.jpg")
    enemy_img = pygame.image.load(enemy_path) if os.path.exists(enemy_path) else None
    background_img = pygame.image.load(background_path) if os.path.exists(background_path) else None
    if enemy_img:
        enemy_img = pygame.transform.scale(enemy_img, (50, 50))
    else:
        print("enemy.png not found, using red rectangle")
        enemy_img = pygame.Surface((50, 50))
        enemy_img.fill((255, 0, 0))
    if background_img:
        background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    else:
        print("space_background.jpg not found, using black background")
        background_img = pygame.Surface((WIDTH, HEIGHT))
        background_img.fill(BLACK)
except Exception as e:
    print(f"Error loading enemy.png or space_background.jpg: {e}")
    enemy_img = pygame.Surface((50, 50))
    enemy_img.fill((255, 0, 0))
    background_img = pygame.Surface((WIDTH, HEIGHT))
    background_img.fill(BLACK)

try:
    shoot_sound = mixer.Sound(os.path.join(BASE_PATH, "shoot.wav"))
    explosion_sound = mixer.Sound(os.path.join(BASE_PATH, "explosion.wav"))
except Exception as e:
    print(f"Error loading sounds: {e}")
    shoot_sound = None
    explosion_sound = None

player_width = 50
player_height = 50
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_speed = 5
player_rect = pygame.Rect(player_x, player_y, player_width, player_height)


bullet_width = 5
bullet_height = 10
bullet_speed = 7
bullets = []
bullet_img = pygame.Surface((bullet_width, bullet_height))
bullet_img.fill(WHITE)


enemy_bullet_width = 5
enemy_bullet_height = 10
enemy_bullet_speed = 5
enemy_bullets = []
enemy_bullet_img = pygame.Surface((enemy_bullet_width, enemy_bullet_height))
enemy_bullet_img.fill(RED)


enemy_width = 50
employee_height = 50
enemy_speed = 3
enemies = []
enemy_spawn_rate = 60
enemy_spawn_counter = 0
enemy_shoot_chance = 0.10


score = 0
game_over = False
font = pygame.font.SysFont(None, 36)

def setup():
    global player_rect
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

def draw_player():
    screen.blit(player_img, player_rect)

def draw_bullets():
    for bullet in bullets[:]:
        screen.blit(bullet_img, bullet)
        bullet.y -= bullet_speed
        if bullet.y < 0:
            bullets.remove(bullet)
    for bullet in enemy_bullets[:]:
        screen.blit(enemy_bullet_img, bullet)
        bullet.y += enemy_bullet_speed
        if bullet.y > HEIGHT:
            enemy_bullets.remove(bullet)

def spawn_enemy():
    x = random.randint(0, WIDTH - enemy_width)
    enemy = pygame.Rect(x, 0, enemy_width, employee_height)
    enemies.append(enemy)

def draw_enemies():
    for enemy in enemies[:]:
        screen.blit(enemy_img, enemy)
        enemy.y += enemy_speed
        if enemy.y > HEIGHT:
            enemies.remove(enemy)
        
        if random.random() < enemy_shoot_chance:
            bullet = pygame.Rect(
                enemy.centerx - enemy_bullet_width // 2,
                enemy.bottom,
                enemy_bullet_width,
                enemy_bullet_height
            )
            enemy_bullets.append(bullet)
            if shoot_sound:
                shoot_sound.play()

def check_collisions():
    global score, game_over
    # Player bullets hitting enemies
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 10
                if explosion_sound:
                    explosion_sound.play()
                break

    for bullet in enemy_bullets[:]:
        if bullet.colliderect(player_rect):
            enemy_bullets.remove(bullet)
            game_over = True
            if explosion_sound:
                explosion_sound.play()

    for enemy in enemies:
        if player_rect.colliderect(enemy):
            game_over = True
            if explosion_sound:
                explosion_sound.play()

def draw_score():
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def draw_game_over():
    game_over_text = font.render(f"Game Over! Score: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(restart_text, (WIDTH // 2 - 80, HEIGHT // 2 + 50))

def reset_game():
    global score, game_over, bullets, enemy_bullets, enemies, player_rect, enemy_spawn_counter
    score = 0
    game_over = False
    bullets = []
    enemy_bullets = []
    enemies = []
    player_rect.x = WIDTH // 2 - player_width // 2
    player_rect.y = HEIGHT - player_height - 10
    enemy_spawn_counter = 0

def update_loop():
    global game_over, enemy_spawn_counter
    if game_over:
        screen.blit(background_img, (0, 0))
        draw_game_over()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
        return True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False


    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.x > 0:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] and player_rect.x < WIDTH - player_width:
        player_rect.x += player_speed
    if keys[pygame.K_SPACE] and len(bullets) < 5:
        bullet = pygame.Rect(
            player_rect.centerx - bullet_width // 2,
            player_rect.y - bullet_height,
            bullet_width,
            bullet_height
        )
        bullets.append(bullet)
        if shoot_sound:
            shoot_sound.play()

    
    enemy_spawn_counter += 1
    if enemy_spawn_counter >= enemy_spawn_rate:
        spawn_enemy()
        enemy_spawn_counter = 0


    screen.blit(background_img, (0, 0))
    draw_player()
    draw_bullets()
    draw_enemies()
    check_collisions()
    draw_score()
    pygame.display.flip()
    return True

async def main():
    setup()
    running = True
    while running:
        running = update_loop()
        await asyncio.sleep(1.0 / 60)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())