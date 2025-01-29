import pygame
import random
import os
from settings import *
from sound import play_sound, load_sounds

class Player:
    def __init__(self, screen_width, screen_height):
        self.rect = pygame.Rect(
            screen_width // 2 - PLAYER_SIZE // 2, screen_height * 3 // 5, PLAYER_SIZE, PLAYER_SIZE
        )

    def move(self, touch_x, screen_width):
        if touch_x < screen_width // 2:
            self.rect.x -= PLAYER_SPEED
        else:
            self.rect.x += PLAYER_SPEED

        self.rect.x = max(0, min(self.rect.x, screen_width - PLAYER_SIZE))

    def draw(self, screen):
        pygame.draw.ellipse(screen, PLAYER_COLOR, self.rect)

class Enemy:
    def __init__(self, x, y, speed, color):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.speed = speed
        self.color = color

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)

class SpecialItem:
    def __init__(self, x, y, speed, shape, color):
        self.rect = pygame.Rect(x, y, SPECIAL_SIZE, SPECIAL_SIZE)
        self.speed = speed
        self.shape = shape
        self.color = color
        self.angle = 0

    def update(self):
        self.rect.y += self.speed
        self.angle += 5

    def draw(self, screen):
        surface = pygame.Surface((SPECIAL_SIZE, SPECIAL_SIZE), pygame.SRCALPHA)

        if self.shape == "square":
            pygame.draw.rect(surface, self.color, (0, 0, SPECIAL_SIZE, SPECIAL_SIZE))
        elif self.shape == "triangle":
            points = [
                (SPECIAL_SIZE // 2, 0),
                (0, SPECIAL_SIZE),
                (SPECIAL_SIZE, SPECIAL_SIZE),
            ]
            pygame.draw.polygon(surface, self.color, points)

        rotated_surface = pygame.transform.rotate(surface, self.angle)

        new_rect = rotated_surface.get_rect(center=self.rect.center)

        screen.blit(rotated_surface, new_rect.topleft)


class Game:
    def __init__(self, screen, screen_size, sound_on):
        self.screen = screen
        self.screen_width, self.screen_height = screen_size
        self.player = Player(self.screen_width, self.screen_height)
        self.enemies = []
        self.special_items = []
        self.score = 0
        self.hd = self.screen_height > 1920
        self.errors = ERROR_MARGIN
        self.font_size = SCORE_FONT_SIZE
        if self.hd : self.font_size += 17
        self.font = pygame.font.Font(FONT_PATH, self.font_size)
        self.last_speed_increment = pygame.time.get_ticks()
        self.game_over = False
        self.enemy_speed = ENEMY_SPEED
        self.enemy_count = 1
        self.level = 1
        self.sound_on = sound_on
        self.last_tick = pygame.time.get_ticks()

        self.sounds = load_sounds()

        self.csv_path = os.path.join(os.path.dirname(__file__), 'data', 'highscores.csv')

        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w') as file:
                file.write("Player,Score\n")

    def spawn_enemy(self):
        x = random.randint(0, self.screen_width - ENEMY_SIZE)
        y = -ENEMY_SIZE if random.random() < 2 / 3 else self.screen_height
        speed = self.enemy_speed if y == -ENEMY_SIZE else -self.enemy_speed
        color = random.choice(ENEMY_COLORS)
        self.enemies.append(Enemy(x, y, speed, color))

    def spawn_special_item(self):
        x = random.randint(0, self.screen_width - SPECIAL_SIZE)
        y = -SPECIAL_SIZE
        shape = random.choice(["square", "triangle"])
        color = SPECIAL_SQUARE_COLOR if shape == "square" else SPECIAL_TRIANGLE_COLOR
        speed = self.enemy_speed + 2
        self.special_items.append(SpecialItem(x, y, speed, shape, color))

    def update_enemies(self):
        for enemy in self.enemies:
            enemy.update()

            if enemy.rect.top > self.screen_height or enemy.rect.bottom < 0:
                enemy.rect.x = random.randint(0, self.screen_width - ENEMY_SIZE)
                enemy.rect.y = -ENEMY_SIZE if enemy.speed > 0 else self.screen_height
                self.score += 1

            elif self.player.rect.colliderect(enemy.rect):
                enemy.rect.x = random.randint(0, self.screen_width - ENEMY_SIZE)
                enemy.rect.y = -ENEMY_SIZE if enemy.speed > 0 else self.screen_height
                self.errors -= 1
                if self.errors <= 1:
                    self.game_over = True
                if self.sound_on:
                    play_sound('collision', self.sounds)

    def update_special_items(self):
        for item in self.special_items[:]:
            item.update()
            if item.rect.top > self.screen_height:
                self.special_items.remove(item)

    def check_collision(self):
        for item in self.special_items[:]:
            if self.player.rect.colliderect(item.rect):
                self.score += 60 if item.shape == "square" else 40
                self.special_items.remove(item)
                if self.sound_on:
                    play_sound('special_item', self.sounds)

    def update(self, sound_on):
        self.sound_on = sound_on
        touches = pygame.mouse.get_pressed()
        if touches[0]:
            touch_x, _ = pygame.mouse.get_pos()
            self.player.move(touch_x, self.screen_width)
            
        if len(self.enemies) < 40 + self.level:
            if random.randint(1, 30) == 1:
                self.spawn_enemy()

        if self.score > 0 and self.score % POINTS_FOR_SPECIAL == 0 and len(self.special_items) < 1:
            self.spawn_special_item()

        self.update_enemies()
        self.update_special_items()
        self.check_collision()

        if pygame.time.get_ticks() - self.last_tick > SPEED_INCREMENT_INTERVAL:
            self.enemy_speed += 1
            self.level += 1
            self.errors += 1
            additional_enemies = int(self.enemy_count * ENEMY_INCREMENT_PERCENTAGE)
            
            if self.level % 9 == 0:
                self.enemy_count += 1

            for _ in range(additional_enemies):
                self.spawn_enemy()
            self.last_speed_increment = pygame.time.get_ticks()

            self.last_tick = pygame.time.get_ticks()

        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for item in self.special_items:
            item.draw(self.screen)

        score_surface = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        errors_surface = self.font.render(f"Lives: {self.errors - 1}", True, (255, 255, 255))
        level_surface = self.font.render(f"Level: {self.level}", True, (255, 255, 255))

        self.screen.blit(score_surface, (10, 20))
        self.screen.blit(errors_surface, (10, 55))
        self.screen.blit(level_surface, (self.screen_width - level_surface.get_width() - 20, 20))

    def reset(self):
        self.score = 0 
        self.errors = ERROR_MARGIN
        self.enemies.clear()
        self.special_items.clear()
        self.game_over = False
        self.enemy_speed = ENEMY_SPEED
        self.enemy_count = 1
        self.level = 0
        self.last_tick = pygame.time.get_ticks()
