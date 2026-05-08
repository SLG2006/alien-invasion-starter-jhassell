class Settings:
    def __init__(self):
        # Static settings
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (0, 0, 0)
        self.ship_limit = 3
        self.fleet_drop_speed = 10
        self.max_alien_bullets = 5
        self.speedup_scale = 1.1
        self.alien_points = 50

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        self.ship_speed = 5.0
        self.bullet_speed = 10.0
        self.alien_speed = 1.0
        self.alien_bullet_speed = 5.0
        self.alien_shoot_chance = 0.015
        self.fleet_direction = 1
        self.bullets_allowed = 3

    def increase_speed(self):
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_bullet_speed *= self.speedup_scale
        self.alien_shoot_chance *= self.speedup_scale
