import pygame
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up display
RESOLUTION = (800, 600)
screen = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption("Shooting Game")

# Load background image
bg_path = "bg.jpg"  # Replace with your background image path
try:
    bg = pygame.image.load(bg_path).convert()
    bg = pygame.transform.scale(bg, RESOLUTION)  # Scale the background image to the screen resolution
except pygame.error as e:
    print(f"Cannot load background image: {bg_path}. Error: {e}")
    raise SystemExit(e)

# Load sound effects
shoot_sound = pygame.mixer.Sound("shoot.wav")  # Replace with your shoot sound file path
hit_sound = pygame.mixer.Sound("hit.wav")  # Replace with your hit sound file path
game_over_sound = pygame.mixer.Sound("game_over.wav")  # Replace with your game over sound file path

class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.color = (0, 255, 0)
        self.speed = 1
        self.x = (RESOLUTION[0] - self.width) // 2
        self.y = (RESOLUTION[1] - self.height) // 2
        self.shield = False

    def move(self, keys):
        if keys[pygame.K_RIGHT] and self.x < RESOLUTION[0] - self.width:
            self.x += self.speed
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_DOWN] and self.y < RESOLUTION[1] - self.height:
            self.y += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        if self.shield:
            pygame.draw.rect(screen, (0, 0, 255), (self.x - 5, self.y - 5, self.width + 10, self.height + 10), 3)

class Bullet:
    def __init__(self, x, y, speed, width=5, height=10, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = width
        self.height = height
        self.color = color

    def move(self):
        self.y -= self.speed

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Enemy:
    def __init__(self, x, y, speed, width=50, height=50, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = width
        self.height = height
        self.color = color

    def move(self):
        self.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Boss:
    def __init__(self, x, y, speed, width=100, height=100, color=(255, 0, 0), health=10):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = width
        self.height = height
        self.color = color
        self.health = health

    def move(self):
        self.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def hit(self):
        self.health -= 1

class Game:
    def __init__(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.boss = None
        self.level = 1
        self.enemies_destroyed = 0
        self.enemies_per_level = 5
        self.enemy_spawn_timer = 500
        self.enemy_speed = 0.8
        self.score = 0
        self.double_bullets = False
        self.upgrade_mode = False
        self.paused = False
        self.shield_active = False
        self.available_upgrades = [1, 2, 3, 4, 5]
        self.lives = 3

    def reset(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.boss = None
        self.enemy_spawn_timer = 1000
        self.level = 1
        self.enemies_destroyed = 0
        self.enemy_speed = 0.5
        self.score = 0
        self.double_bullets = False
        self.shield_active = False
        self.available_upgrades = [1, 2, 3, 4, 5]
        self.lives = 3

    def create_enemy(self):
        x = random.randint(0, RESOLUTION[0] - 50)
        y = random.randint(-100, -40)
        self.enemies.append(Enemy(x, y, self.enemy_speed))

    def create_boss(self):
        x = (RESOLUTION[0] - 100) // 2
        y = -100
        self.boss = Boss(x, y, self.enemy_speed)

    def display_game_over(self):
        game_over_sound.play()
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over", True, (255, 0, 0))
        screen.blit(text, (RESOLUTION[0] // 2 - text.get_width() // 2, RESOLUTION[1] // 2 - text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(2000)

    def display_level(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Level {self.level}", True, (255, 255, 255))
        screen.blit(text, (10, 10))

    def display_score(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(text, (RESOLUTION[0] - 150, 10))

    def display_lives(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        screen.blit(text, (RESOLUTION[0] - 150, 50))

    def display_upgrade_options(self):
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        options = ["1. Increase Player Speed", "2. Increase Bullet Speed", "3. Increase Bullet Size", "4. Double Bullets", "5. Shield for One Level"]
        for i, option in enumerate(options):
            if i + 1 in self.available_upgrades:
                text = font.render(option, True, (255, 255, 255))
                screen.blit(text, (50, 150 + i * 50))
        pygame.display.flip()

    def apply_upgrade(self, upgrade_choice):
        if upgrade_choice == 1:
            self.player.speed += 1
        elif upgrade_choice == 2:
            for bullet in self.bullets:
                bullet.speed += 1
        elif upgrade_choice == 3:
            for bullet in self.bullets:
                bullet.width += 2
                bullet.height += 2
        elif upgrade_choice == 4:
            self.double_bullets = True
        elif upgrade_choice == 5:
            self.player.shield = True
            self.shield_active = True
        self.available_upgrades.remove(upgrade_choice)

    def toggle_pause(self):
        self.paused = not self.paused

    def display_pause_message(self):
        font = pygame.font.Font(None, 74)
        text = font.render("Paused", True, (255, 255, 255))
        screen.blit(text, (RESOLUTION[0] // 2 - text.get_width() // 2, RESOLUTION[1] // 2 - text.get_height() // 2))
        pygame.display.flip()

    def main_game_loop(self):
        game_running = True

        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.toggle_pause()
                    if self.upgrade_mode:
                        if event.key == pygame.K_1 and 1 in self.available_upgrades:
                            self.apply_upgrade(1)
                            self.upgrade_mode = False
                        elif event.key == pygame.K_2 and 2 in self.available_upgrades:
                            self.apply_upgrade(2)
                            self.upgrade_mode = False
                        elif event.key == pygame.K_3 and 3 in self.available_upgrades:
                            self.apply_upgrade(3)
                            self.upgrade_mode = False
                        elif event.key == pygame.K_4 and 4 in self.available_upgrades:
                            self.apply_upgrade(4)
                            self.upgrade_mode = False
                        elif event.key == pygame.K_5 and 5 in self.available_upgrades:
                            self.apply_upgrade(5)
                            self.upgrade_mode = False
                    else:
                        if event.key == pygame.K_SPACE:
                            bullet_x = self.player.x + self.player.width // 2 - 5 // 2
                            bullet_y = self.player.y
                            self.bullets.append(Bullet(bullet_x, bullet_y, 2))
                            shoot_sound.play()
                            if self.double_bullets:
                                self.bullets.append(Bullet(bullet_x - 10, bullet_y, 2))
                                self.bullets.append(Bullet(bullet_x + 10, bullet_y, 2))

            if not self.paused:
                if not self.upgrade_mode:
                    keys = pygame.key.get_pressed()
                    self.player.move(keys)

                    for bullet in self.bullets[:]:
                        bullet.move()
                        if bullet.y < 0:
                            self.bullets.remove(bullet)

                    if self.level < 10:
                        if self.enemy_spawn_timer <= 0:
                            self.create_enemy()
                            self.enemy_spawn_timer = max(100, 1000 - (self.level * 100))
                        else:
                            self.enemy_spawn_timer -= 1

                        for enemy in self.enemies[:]:
                            enemy.move()
                            if enemy.y > RESOLUTION[1]:
                                self.enemies.remove(enemy)

                        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                        for enemy in self.enemies[:]:
                            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                            if player_rect.colliderect(enemy_rect):
                                if not self.player.shield:
                                    self.lives -= 1
                                    self.enemies.remove(enemy)
                                    if self.lives <= 0:
                                        self.display_game_over()
                                        self.reset()
                                        break
                                else:
                                    self.enemies.remove(enemy)

                        for bullet in self.bullets[:]:
                            bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
                            for enemy in self.enemies[:]:
                                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                                if bullet_rect.colliderect(enemy_rect):
                                    self.bullets.remove(bullet)
                                    self.enemies.remove(enemy)
                                    self.enemies_destroyed += 1
                                    self.score += 10
                                    hit_sound.play()
                                    break

                        if self.enemies_destroyed >= self.enemies_per_level:
                            self.level += 1
                            self.enemies_destroyed = 0
                            self.enemy_speed += 0.2
                            self.upgrade_mode = True
                            if self.shield_active:
                                self.player.shield = False
                                self.shield_active = False
                    else:
                        if self.boss is None:
                            self.create_boss()
                        else:
                            self.boss.move()
                            if self.boss.y > RESOLUTION[1]:
                                self.display_game_over()
                                self.reset()
                                break

                            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                            boss_rect = pygame.Rect(self.boss.x, self.boss.y, self.boss.width, self.boss.height)
                            if player_rect.colliderect(boss_rect):
                                if not self.player.shield:
                                    self.lives -= 1
                                    if self.lives <= 0:
                                        self.display_game_over()
                                        self.reset()
                                        break

                            for bullet in self.bullets[:]:
                                bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
                                if bullet_rect.colliderect(boss_rect):
                                    self.bullets.remove(bullet)
                                    self.boss.hit()
                                    self.score += 10
                                    hit_sound.play()
                                    if self.boss.health <= 0:
                                        self.level += 1
                                        self.boss = None
                                        self.upgrade_mode = True
                                        if self.shield_active:
                                            self.player.shield = False
                                            self.shield_active = False
                                    break

                    screen.blit(bg, (0, 0))
                    self.player.draw()
                    for bullet in self.bullets:
                        bullet.draw()
                    for enemy in self.enemies:
                        enemy.draw()
                    if self.boss:
                        self.boss.draw()
                    self.display_level()
                    self.display_score()
                    self.display_lives()
                    pygame.display.flip()
                else:
                    self.display_upgrade_options()
            else:
                self.display_pause_message()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.main_game_loop()