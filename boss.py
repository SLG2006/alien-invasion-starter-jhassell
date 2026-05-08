import pygame
import random


class Boss(pygame.sprite.Sprite):
    def __init__(self, screen, settings):
        super().__init__()
        self.screen = screen
        self.settings = settings
        self.hp = 100
        self.max_hp = 100
        self.phase = 1
        self.phase_changed = False
        self.direction = 1
        self.speed = 2.0
        self.direction_change_chance = 0.02   # ~2 % per frame (≈ avg every 3 s)
        self.shoot_burst = 3
        self.telegraphing = False
        self.telegraph_timer = 0
        self.should_fire = False
        self.hit_flash_timer = 0
        self.entering = True
        self.enter_target_y = 70
        self.shoot_timer = 120

        self.width = 120
        self.height = 90
        self.base_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw_boss_eagle(self.base_image)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = screen.get_rect().centerx
        self.rect.top = -self.height

    def _draw_boss_eagle(self, surface):
        steel    = (60,  80, 110)
        silver   = (160, 180, 200)
        white    = (240, 240, 240)
        gold     = (255, 210,   0)
        red      = (220,  40,  40)
        navy     = (20,  28,  50)
        dark_red = (140,   0,   0)
        orange   = (255, 140,   0)

        w, h = self.width, self.height
        cx = w // 2

        # Large dark-red wings with energy lines
        pygame.draw.polygon(surface, dark_red, [(0, 25), (cx - 12, 42), (12, 68)])
        pygame.draw.polygon(surface, dark_red, [(w, 25), (cx + 12, 42), (w - 12, 68)])
        pygame.draw.polygon(surface, steel,    [(4, 25), (cx - 12, 40), (16, 64)])
        pygame.draw.polygon(surface, steel,    [(w - 4, 25), (cx + 12, 40), (w - 16, 64)])
        for i in range(3):
            pygame.draw.line(surface, red, (5 + i * 6, 28 + i * 4), (cx - 14, 38 + i * 4), 2)
            pygame.draw.line(surface, red, (w - 5 - i * 6, 28 + i * 4), (cx + 14, 38 + i * 4), 2)

        # Armored body
        pygame.draw.ellipse(surface, navy,   (cx - 20, 32, 40, 50))
        pygame.draw.ellipse(surface, steel,  (cx - 15, 36, 30, 35))
        pygame.draw.ellipse(surface, silver, (cx - 12, 38, 24, 20), 2)

        # White head (bald eagle)
        pygame.draw.circle(surface, white, (cx, 20), 18)
        pygame.draw.circle(surface, steel, (cx, 20), 18, 2)

        # Menacing downward beak
        pygame.draw.polygon(surface, gold,   [(cx - 10, 30), (cx + 10, 30), (cx, 46)])
        pygame.draw.polygon(surface, orange, [(cx - 7,  30), (cx + 7,  30), (cx, 42)])

        # Glowing red eyes (boss is angry)
        pygame.draw.circle(surface, red,             (cx - 8, 17), 5)
        pygame.draw.circle(surface, red,             (cx + 8, 17), 5)
        pygame.draw.circle(surface, (255, 100, 100), (cx - 8, 17), 3)
        pygame.draw.circle(surface, (255, 100, 100), (cx + 8, 17), 3)
        pygame.draw.circle(surface, white,           (cx - 7, 16), 1)
        pygame.draw.circle(surface, white,           (cx + 7, 16), 1)

        # Tail feathers
        pygame.draw.polygon(surface, steel, [(cx - 22, 78), (cx, 90), (cx + 22, 78)])
        for i in range(3):
            pygame.draw.line(surface, silver, (cx - 12 + i * 8, 78), (cx - 8 + i * 8, 88), 2)

    def update(self):
        self.should_fire = False
        self.phase_changed = False

        if self.entering:
            self.rect.top = min(self.rect.top + 3, self.enter_target_y)
            if self.rect.top >= self.enter_target_y:
                self.entering = False
            return

        if self.hp <= 50 and self.phase == 1:
            self.phase = 2
            self.phase_changed = True
            self.speed = 3.5
            self.direction_change_chance = 0.04   # phase 2: twice as erratic
            self.shoot_burst = 5

        # Random mid-row direction reversal — makes movement unpredictable
        if random.random() < self.direction_change_chance:
            self.direction *= -1

        self.rect.x += self.speed * self.direction
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right:
            self.rect.right = screen_rect.right   # clamp, then set direction explicitly
            self.direction = -1
        elif self.rect.left <= 0:
            self.rect.left = 0
            self.direction = 1

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            hit_img = self.base_image.copy()
            overlay = pygame.Surface(hit_img.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))
            hit_img.blit(overlay, (0, 0))
            self.image = hit_img
        elif self.telegraphing:
            self.telegraph_timer -= 1
            if self.telegraph_timer <= 0:
                self.telegraphing = False
                self.should_fire = True
                self.image = self.base_image.copy()
        else:
            self.image = self.base_image.copy()

    def start_telegraph(self):
        if not self.telegraphing and not self.entering:
            self.telegraphing = True
            self.telegraph_timer = 30
            tinted = self.base_image.copy()
            overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 140))
            tinted.blit(overlay, (0, 0))
            self.image = tinted

    def take_damage(self, amount):
        if self.entering:
            return False
        self.hp = max(0, self.hp - amount)
        self.hit_flash_timer = 6
        return self.hp <= 0

    def draw_hp_bar(self):
        screen_rect = self.screen.get_rect()
        bar_width = 300
        bar_height = 22
        x = screen_rect.centerx - bar_width // 2
        y = 60

        pygame.draw.rect(self.screen, (30, 30, 30), (x - 2, y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(self.screen, (70, 70, 70), (x, y, bar_width, bar_height))

        hp_ratio = self.hp / self.max_hp
        if hp_ratio > 0.5:
            bar_color = (0, 200, 50)
        elif hp_ratio > 0.25:
            bar_color = (255, 200, 0)
        else:
            bar_color = (220, 30, 30)

        fill_width = int(bar_width * hp_ratio)
        if fill_width > 0:
            pygame.draw.rect(self.screen, bar_color, (x, y, fill_width, bar_height))

        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, bar_width, bar_height), 2)

        font = pygame.font.SysFont(None, 20)
        label = font.render(f"BOSS HP  {self.hp} / {self.max_hp}", True, (255, 255, 255))
        self.screen.blit(label, (x + bar_width // 2 - label.get_width() // 2, y + 3))
