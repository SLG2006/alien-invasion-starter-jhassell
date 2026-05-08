import time
import pygame
import random
from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
from alien_bullet import AlienBullet
from button import Button
from scoreboard import Scoreboard
from boss import Boss
from beam import Beam


class AlienInvasion:
    BEAM_CHARGE_FRAMES   = 300   # 5 s at 60 fps
    BEAM_COOLDOWN_FRAMES = 180   # 3 s recharge
    BOSS_INTRO_FRAMES    = 150   # 2.5 s warning screen

    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Alien Invasion")
        self.clock = pygame.time.Clock()
        self.dots = [(random.randint(0, 800), random.randint(0, 600)) for _ in range(150)]
        self.stats = GameStats(self)
        self.play_button = Button(self, 'Play')
        self.sb = Scoreboard(self)
        self.ship = Ship(self.screen, self.settings)
        self.bullets = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.beams = pygame.sprite.Group()
        self.boss = None
        # game_phase: 'normal' | 'boss_intro' | 'boss_fight' | 'game_won'
        self.game_phase = 'normal'
        self.weapon_upgraded = False
        self.space_held_frames = 0
        self.beam_cooldown = 0
        self.boss_intro_timer = 0
        self.game_won_timer = 0
        self.notifications = []
        self._create_fleet()

    # ── Main loop ──────────────────────────────────────────────────

    def run_game(self):
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                if self.game_phase == 'normal':
                    self._check_fleet_edges()
                    self.aliens.update()
                    self._update_bullets()
                    self._update_alien_bullets()
                    self._check_aliens_bottom()
                    if pygame.sprite.spritecollideany(self.ship, self.aliens):
                        self._ship_hit()
                elif self.game_phase == 'boss_intro':
                    self._update_boss_intro()
                elif self.game_phase == 'boss_fight':
                    self._update_boss_fight()
                elif self.game_phase == 'game_won':
                    self.game_won_timer -= 1
                    if self.game_won_timer <= 0:
                        self.stats.game_active = False
                        self.game_phase = 'normal'
                        pygame.mouse.set_visible(True)
            self._update_screen()
            self.clock.tick(60)

    # ── Events ─────────────────────────────────────────────────────

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.stats.game_active:
                    self._check_play_button(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_RIGHT:
                    self.ship.moving_right = True
                elif event.key == pygame.K_LEFT:
                    self.ship.moving_left = True
                elif event.key == pygame.K_SPACE:
                    if self.stats.game_active and self.game_phase in ('normal', 'boss_fight'):
                        if len(self.bullets) < self.settings.bullets_allowed:
                            self.bullets.add(Bullet(self.ship, self.settings))
                elif event.key == pygame.K_1:
                    self._debug_jump_to_level(1)
                elif event.key == pygame.K_2:
                    self._debug_jump_to_level(2)
                elif event.key == pygame.K_3:
                    self._debug_jump_to_level(3)
                elif event.key == pygame.K_4:
                    self._debug_jump_to_boss()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.ship.moving_right = False
                elif event.key == pygame.K_LEFT:
                    self.ship.moving_left = False
                elif event.key == pygame.K_SPACE:
                    # Fire beam on release if fully charged
                    if (self.game_phase == 'boss_fight' and
                            self.weapon_upgraded and
                            self.beam_cooldown == 0 and
                            self.space_held_frames >= self.BEAM_CHARGE_FRAMES):
                        self._fire_beam()
                    self.space_held_frames = 0

    def _check_play_button(self, mouse_pos):
        if self.play_button.rect.collidepoint(mouse_pos):
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()
            self.beams.empty()
            self.boss = None
            self.game_phase = 'normal'
            self.weapon_upgraded = False
            self.space_held_frames = 0
            self.beam_cooldown = 0
            self.notifications = []
            self._create_fleet()
            self.ship.rect.midbottom = self.screen.get_rect().midbottom
            pygame.mouse.set_visible(False)

    # ── Ship / fleet helpers ────────────────────────────────────────

    def _ship_hit(self):
        self.stats.ships_left -= 1
        self.sb.prep_ships()
        if self.stats.ships_left == 0:
            self.stats.game_active = False
            self.game_phase = 'normal'
            self.boss = None
            self.weapon_upgraded = False
            pygame.mouse.set_visible(True)
            return
        self.alien_bullets.empty()
        self.bullets.empty()
        self.beams.empty()
        self.space_held_frames = 0
        self.beam_cooldown = 0
        if self.game_phase == 'normal':
            self.aliens.empty()
            self._create_fleet()
        self.ship.rect.midbottom = self.screen.get_rect().midbottom
        time.sleep(0.5)

    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.height:
                self._ship_hit()
                break

    def _create_fleet(self):
        alien = Alien(self.screen, self.settings)
        alien_width, alien_height = alien.rect.size
        screen_rect = self.screen.get_rect()

        available_x = screen_rect.width - 2 * alien_width
        aliens_per_row = available_x // (2 * alien_width)

        available_y = screen_rect.height - 3 * alien_height - self.ship.rect.height
        number_of_rows = max(1, available_y // (2 * alien_height) - 2)

        for row in range(number_of_rows):
            for col in range(aliens_per_row):
                alien = Alien(self.screen, self.settings)
                alien.rect.x = alien_width + col * (2 * alien_width)
                alien.rect.y = alien_height + row * (2 * alien_height)
                self.aliens.add(alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                for a in self.aliens.sprites():
                    a.rect.y += self.settings.fleet_drop_speed
                self.settings.fleet_direction *= -1
                break

    # ── Normal-phase bullets ────────────────────────────────────────

    def _update_alien_bullets(self):
        if (self.aliens and
                len(self.alien_bullets) < self.settings.max_alien_bullets and
                random.random() < self.settings.alien_shoot_chance):
            shooter = random.choice(self.aliens.sprites())
            self.alien_bullets.add(AlienBullet(shooter, self.settings))

        self.alien_bullets.update()

        screen_height = self.screen.get_rect().height
        for b in [b for b in self.alien_bullets if b.rect.top >= screen_height]:
            self.alien_bullets.remove(b)

        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self._ship_hit()

    def _update_bullets(self):
        self.bullets.update()
        for bullet in [b for b in self.bullets if b.rect.bottom < 0]:
            self.bullets.remove(bullet)
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens_hit in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens_hit)
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            self.bullets.empty()
            self.alien_bullets.empty()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()
            if self.stats.level > 3:
                self._start_boss_sequence()
            else:
                self._create_fleet()

    # ── Boss sequence ───────────────────────────────────────────────

    def _start_boss_sequence(self):
        self.bullets.empty()
        self.alien_bullets.empty()
        # Full heal
        self.stats.ships_left = self.settings.ship_limit
        self.sb.prep_ships()
        # Weapon upgrade
        self.weapon_upgraded = True
        self.settings.bullets_allowed = 5
        # Create boss (starts off-screen, enters during intro)
        self.boss = Boss(self.screen, self.settings)
        self.game_phase = 'boss_intro'
        self.boss_intro_timer = self.BOSS_INTRO_FRAMES

    def _update_boss_intro(self):
        self.boss.update()  # boss flies in during the warning screen
        self.boss_intro_timer -= 1
        # Wait until both the timer and the entrance animation are done
        if self.boss_intro_timer <= 0 and not self.boss.entering:
            self.game_phase = 'boss_fight'
            self._add_notification(
                "HEALTH RESTORED!  WEAPON UPGRADED!", 220, (100, 255, 100), 28, 110)
            self._add_notification(
                "5 LASERS  |  HOLD SPACE 5s, RELEASE = BEAM", 220, (150, 255, 150), 22, 145)

    def _update_boss_fight(self):
        self.boss.update()

        # Phase-2 enrage notification
        if self.boss.phase_changed:
            self._add_notification("BOSS ENRAGED!", 180, (255, 80, 0), 40, -20)

        # Shoot timer (only after boss has fully entered)
        if not self.boss.entering:
            self.boss.shoot_timer -= 1
            if self.boss.shoot_timer <= 0 and not self.boss.telegraphing:
                self.boss.start_telegraph()
                interval = (random.randint(90, 150) if self.boss.phase == 1
                            else random.randint(45, 80))
                self.boss.shoot_timer = interval

        if self.boss.should_fire:
            self._boss_fire_burst()

        # Beam charging (hold SPACE)
        self._update_beam_charge()
        if self.game_phase != 'boss_fight':
            return

        # Player bullets → boss
        self.bullets.update()
        for b in [b for b in self.bullets if b.rect.bottom < 0]:
            self.bullets.remove(b)
        hits = pygame.sprite.spritecollide(self.boss, self.bullets, True)
        for _ in hits:
            if self.boss.take_damage(1):
                self._boss_defeated()
                return

        # Beam visual update (damage already applied on fire)
        self.beams.update()

        # Boss bullets → player
        self.alien_bullets.update()
        screen_height = self.screen.get_rect().height
        for b in [b for b in self.alien_bullets if b.rect.top >= screen_height]:
            self.alien_bullets.remove(b)
        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self._ship_hit()

    def _boss_fire_burst(self):
        burst = self.boss.shoot_burst
        spread = 50
        speed = 8.0 if self.boss.phase == 1 else 11.0
        for i in range(burst):
            bullet = AlienBullet(self.boss, self.settings)
            if burst > 1:
                offset = (i - burst // 2) * (spread // max(burst - 1, 1))
                bullet.rect.centerx = self.boss.rect.centerx + offset
            bullet.rect.top = self.boss.rect.bottom
            bullet.speed = speed
            self.alien_bullets.add(bullet)

    # ── Beam weapon ─────────────────────────────────────────────────

    def _update_beam_charge(self):
        if self.beam_cooldown > 0:
            self.beam_cooldown -= 1
            self.space_held_frames = 0
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Cap at BEAM_CHARGE_FRAMES so the bar stays full when ready
            self.space_held_frames = min(self.space_held_frames + 1, self.BEAM_CHARGE_FRAMES)
        else:
            self.space_held_frames = 0

    def _fire_beam(self):
        beam = Beam(self.ship)
        self.beams.add(beam)
        self.space_held_frames = 0
        self.beam_cooldown = self.BEAM_COOLDOWN_FRAMES
        if self.boss and pygame.sprite.collide_rect(beam, self.boss):
            if self.boss.take_damage(Beam.damage):
                self._boss_defeated()

    def _boss_defeated(self):
        self.beams.empty()
        self.alien_bullets.empty()
        self.bullets.empty()
        self.stats.score += 5000
        self.sb.prep_score()
        self.sb.check_high_score()
        self.game_phase = 'game_won'
        self.game_won_timer = 360
        self._add_notification("BOSS DEFEATED!", 360, (255, 215, 0), 72, -70)
        self._add_notification("YOU WIN!", 360, (255, 255, 255), 56, 10)
        self._add_notification(f"FINAL SCORE: {self.stats.score:,}", 340, (200, 200, 255), 32, 75)

    # ── Notifications ───────────────────────────────────────────────

    def _add_notification(self, text, duration, color=(255, 255, 255), size=28, y_offset=0):
        self.notifications.append({
            'text': text, 'timer': duration,
            'color': color, 'size': size, 'y_offset': y_offset,
        })

    def _draw_notifications(self):
        screen_rect = self.screen.get_rect()
        active = []
        for n in self.notifications:
            font = pygame.font.SysFont(None, n['size'])
            surf = font.render(n['text'], True, n['color'])
            x = screen_rect.centerx - surf.get_width() // 2
            y = screen_rect.centery + n['y_offset']
            self.screen.blit(surf, (x, y))
            n['timer'] -= 1
            if n['timer'] > 0:
                active.append(n)
        self.notifications = active

    # ── Charge bar ──────────────────────────────────────────────────

    def _draw_charge_bar(self):
        bar_width = 180
        bar_height = 16
        x = 10
        y = self.screen.get_rect().height - 55
        font = pygame.font.SysFont(None, 17)

        pygame.draw.rect(self.screen, (30, 30, 30), (x, y, bar_width, bar_height))

        if self.beam_cooldown > 0:
            ratio = self.beam_cooldown / self.BEAM_COOLDOWN_FRAMES
            fill = int(bar_width * ratio)
            pygame.draw.rect(self.screen, (200, 130, 0), (x, y, fill, bar_height))
            label = font.render("BEAM RECHARGING", True, (200, 180, 80))
        elif self.space_held_frames > 0:
            ratio = min(self.space_held_frames / self.BEAM_CHARGE_FRAMES, 1.0)
            fill = int(bar_width * ratio)
            if self.space_held_frames >= self.BEAM_CHARGE_FRAMES:
                pygame.draw.rect(self.screen, (150, 255, 150), (x, y, fill, bar_height))
                label = font.render("BEAM READY - RELEASE!", True, (200, 255, 200))
            else:
                pygame.draw.rect(self.screen, (0, 200, 0), (x, y, fill, bar_height))
                label = font.render("BEAM CHARGING...", True, (100, 255, 100))
        else:
            label = font.render("HOLD SPACE FOR BEAM", True, (80, 160, 80))

        pygame.draw.rect(self.screen, (120, 120, 120), (x, y, bar_width, bar_height), 1)
        self.screen.blit(label, (x, y - 16))

    # ── Title screen ────────────────────────────────────────────────

    def _draw_title_screen(self):
        screen_rect = self.screen.get_rect()

        # Pick the most epic available serif font on the system
        title_font = None
        for name in ('palatino', 'georgia', 'baskerville', 'timesnewroman', 'times'):
            candidate = pygame.font.SysFont(name, 54, bold=True)
            # SysFont silently falls back to freesansbold; accept any non-default
            if candidate.size('A')[1] > 0:
                title_font = candidate
                break
        if title_font is None:
            title_font = pygame.font.SysFont(None, 60, bold=True)

        subtitle_font = pygame.font.SysFont(None, 26)
        hint_font     = pygame.font.SysFont(None, 22)

        title_text = "The Legend of Zarigüeya"
        # Render with gold drop-shadow for the epic feel
        shadow_surf = title_font.render(title_text, True, (90, 40, 0))
        title_surf  = title_font.render(title_text, True, (255, 210, 0))

        tx = screen_rect.centerx - title_surf.get_width() // 2
        ty = screen_rect.centery - 185

        self.screen.blit(shadow_surf, (tx + 3, ty + 3))   # shadow
        self.screen.blit(title_surf,  (tx,     ty))        # gold title

        # Decorative golden line under title
        line_y = ty + title_surf.get_height() + 8
        pygame.draw.line(self.screen, (180, 140, 0),
                         (screen_rect.centerx - 200, line_y),
                         (screen_rect.centerx + 200, line_y), 2)

        # Subtitle
        sub = subtitle_font.render("A Possum's Last Stand Against the Eagle Empire",
                                   True, (180, 180, 210))
        self.screen.blit(sub, (screen_rect.centerx - sub.get_width() // 2, line_y + 12))

        # Debug key hint (small, dim)
        hint = hint_font.render("1 / 2 / 3 / 4  —  jump to level", True, (80, 80, 80))
        self.screen.blit(hint, (screen_rect.centerx - hint.get_width() // 2,
                                screen_rect.bottom - 30))

    # ── Debug level jumps ───────────────────────────────────────────

    def _debug_jump_to_level(self, level):
        self.settings.initialize_dynamic_settings()
        for _ in range(level - 1):
            self.settings.increase_speed()
        self.stats.reset_stats()
        self.stats.level = level
        self.stats.game_active = True
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.aliens.empty()
        self.bullets.empty()
        self.alien_bullets.empty()
        self.beams.empty()
        self.boss = None
        self.game_phase = 'normal'
        self.weapon_upgraded = False
        self.space_held_frames = 0
        self.beam_cooldown = 0
        self.notifications = []
        self._create_fleet()
        self.ship.rect.midbottom = self.screen.get_rect().midbottom
        pygame.mouse.set_visible(False)

    def _debug_jump_to_boss(self):
        self._debug_jump_to_level(4)
        self._start_boss_sequence()

    # ── Boss intro overlay ──────────────────────────────────────────

    def _draw_boss_intro_screen(self):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        screen_rect = self.screen.get_rect()
        font_big = pygame.font.SysFont(None, 90)
        font_med = pygame.font.SysFont(None, 36)

        title = font_big.render("!! FINAL BOSS !!", True, (220, 0, 0))
        self.screen.blit(title,
                         (screen_rect.centerx - title.get_width() // 2,
                          screen_rect.centery - 70))

        sub = font_med.render("Prepare yourself...", True, (200, 200, 200))
        self.screen.blit(sub,
                         (screen_rect.centerx - sub.get_width() // 2,
                          screen_rect.centery + 20))

        bar_width = 300
        bar_height = 10
        bx = screen_rect.centerx - bar_width // 2
        by = screen_rect.centery + 75
        ratio = 1.0 - (self.boss_intro_timer / self.BOSS_INTRO_FRAMES)
        pygame.draw.rect(self.screen, (60, 20, 20), (bx, by, bar_width, bar_height))
        pygame.draw.rect(self.screen, (200, 0, 0), (bx, by, int(bar_width * ratio), bar_height))
        pygame.draw.rect(self.screen, (150, 150, 150), (bx, by, bar_width, bar_height), 1)

    # ── Screen ──────────────────────────────────────────────────────

    def _update_screen(self):
        self.screen.fill((0, 0, 0))
        for x, y in self.dots:
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 2)

        if not self.stats.game_active:
            self._draw_title_screen()
            self.play_button.draw_button()
        elif self.game_phase == 'boss_intro':
            self.screen.blit(self.boss.image, self.boss.rect)
            self._draw_boss_intro_screen()
        elif self.game_phase == 'boss_fight':
            self.screen.blit(self.boss.image, self.boss.rect)
            self.boss.draw_hp_bar()
            self.ship.blitme()
            self.bullets.draw(self.screen)
            self.beams.draw(self.screen)
            self.alien_bullets.draw(self.screen)
            self.sb.show_score()
            self._draw_charge_bar()
            self._draw_notifications()
        elif self.game_phase == 'game_won':
            self.ship.blitme()
            self._draw_notifications()
        else:  # normal
            self.aliens.draw(self.screen)
            self.ship.blitme()
            self.bullets.draw(self.screen)
            self.alien_bullets.draw(self.screen)
            self.sb.show_score()

        pygame.display.flip()


if __name__ == '__main__':
    AlienInvasion().run_game()
