"""
Excellent Space Shooter
Main Game Module with Menu System and Persistent Highscores.
"""
# pylint: disable=E0611,E1101
import math
import random
import sys
import pygame
from pygame import QUIT as PG_QUIT, K_ESCAPE, K_RETURN, K_SPACE, K_h, K_w, K_UP, K_DOWN, K_TAB
from pygame.display import set_mode, set_caption, update
from pygame.event import get as pg_get
from pygame.time import Clock
from pygame.font import init as font_init, Font
from pygame.mixer import init as mixer_init, Sound

from enemy_manager import EnemyManager
from player import Player
from level import Level
from paths import asset_path
from sprites import get_sheet
from highscore_manager import HighscoreManager
from ui import Button, TextInput, VolumeSlider, draw_panel, draw_text
from audio_manager import audio_manager

# Pygame initialization
size = width, height = 750, 750
screen = set_mode(size)
set_caption("Excellent Space Shooter")
font_init()
mixer_init()

# Fonts
font_huge = Font(asset_path("fonts", "kenvector_future.ttf"), 42)
font_large = Font(asset_path("fonts", "kenvector_future.ttf"), 30)
font_medium = Font(asset_path("fonts", "kenvector_future.ttf"), 20)
font_small = Font(asset_path("fonts", "kenvector_future.ttf"), 15)
font_thin_large = Font(asset_path("fonts", "kenvector_future_thin.ttf"), 28)
font_thin_medium = Font(asset_path("fonts", "kenvector_future_thin.ttf"), 22)
font_thin_small = Font(asset_path("fonts", "kenvector_future_thin.ttf"), 17)

# Backward compatibility fonts
future_font = Font(asset_path("fonts", "kenvector_future.ttf"), 60)
future_thin_font = Font(asset_path("fonts", "kenvector_future_thin.ttf"), 30)

# Audio
music = Sound(asset_path("sounds", "space_half.mp3"))
lose_sound = Sound(asset_path("sounds", "sfx_lose.ogg"))
save_sound = Sound(asset_path("sounds", "sfx_shieldUp.ogg"))

audio_manager.set_music_sound(music)
audio_manager.register_sfx(lose_sound)
audio_manager.register_sfx(save_sound)

# Highscore Manager
highscore_manager = HighscoreManager()

# Menu background level
menu_level = Level(0)

# Global game objects for backward compatibility
player = Player(300, 650, "playerShip2_red")
enemy_manager = EnemyManager()
level = Level(0)


class GameState:
    """Game state constants."""
    MENU = "menu"
    SETTINGS = "settings"
    TRANSITION = "transition"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    HIGHSCORES = "highscores"


class GameManager:
    """
    Manages the complete game flow: menus, gameplay, pause, game-over, and highscore board.
    """

    def __init__(self):
        self.state = GameState.MENU
        self.settings_return_state = GameState.MENU
        self.clock = Clock()
        self.fps = 60
        self.keep_going = True

        # Highscores & player history
        self.highscore_manager = highscore_manager
        self.current_player_name = "PILOT"
        self.highlight_timestamp = None
        self.highscore_view = "top"  # "top" or "recent"

        # Game session objects
        self.player = None
        self.enemy_manager = None
        self.level = None
        self.number_enemies = 0
        self.lost_time = 0
        self.final_score = 0
        self.final_level = 1
        self.is_new_best = False
        self.score_saved = False

        # Decorative menu ship and transition animation assets
        sheet = get_sheet()
        self.menu_ship_img = sheet.get_image_name("playerShip2_red")
        self.speed_streak_img = sheet.get_image_name("speed")
        self.flame_imgs = [
            sheet.get_image_name("fire00"),
            sheet.get_image_name("fire08"),
            sheet.get_image_name("fire11"),
            sheet.get_image_name("fire14"),
        ]
        self.transition_frame = 0
        self.transition_max_frames = 115
        self.speed_lines = []
        self.exhaust_particles = []
        self.life_icon = sheet.get_image_name("playerLife2_red")

        # Create UI elements
        self._init_ui()

        # Start background music loop
        music.play(loops=-1)

    def _init_ui(self):
        """Initializes buttons and text input fields."""
        sheet = get_sheet()
        btn_w, btn_h = 280, 48
        cx = (width - btn_w) // 2

        # Main Menu Buttons
        self.btn_menu_start = Button(
            cx, 375, btn_w, btn_h, "SPIEL STARTEN", font_medium, style="green", hover_style="yellow", sheet=sheet
        )
        self.btn_menu_highscores = Button(
            cx, 435, btn_w, btn_h, "HIGHSCORES", font_medium, style="blue", hover_style="yellow", sheet=sheet
        )
        self.btn_menu_settings = Button(
            cx, 495, btn_w, btn_h, "EINSTELLUNGEN", font_medium, style="blue", hover_style="yellow", sheet=sheet
        )
        self.btn_menu_quit = Button(
            cx, 555, btn_w, btn_h, "BEENDEN", font_medium, style="red", hover_style="yellow", sheet=sheet
        )

        # Pause Menu Buttons
        self.btn_pause_resume = Button(
            cx, 285, btn_w, btn_h, "WEITER", font_medium, style="green", hover_style="yellow", sheet=sheet
        )
        self.btn_pause_settings = Button(
            cx, 345, btn_w, btn_h, "EINSTELLUNGEN", font_medium, style="blue", hover_style="yellow", sheet=sheet
        )
        self.btn_pause_restart = Button(
            cx, 405, btn_w, btn_h, "NEUSTART", font_medium, style="blue", hover_style="yellow", sheet=sheet
        )
        self.btn_pause_menu = Button(
            cx, 465, btn_w, btn_h, "HAUPTMENÜ", font_medium, style="red", hover_style="yellow", sheet=sheet
        )

        # Settings Screen Sliders and Buttons
        self.music_slider = VolumeSlider(245, 226, 260, 42, font_medium)
        self.btn_music_down = Button(175, 225, 54, 44, "-", font_large, style="red", hover_style="yellow", sheet=sheet)
        self.btn_music_up = Button(521, 225, 54, 44, "+", font_large, style="green", hover_style="yellow", sheet=sheet)

        self.sfx_slider = VolumeSlider(245, 356, 260, 42, font_medium)
        self.btn_sfx_down = Button(175, 355, 54, 44, "-", font_large, style="red", hover_style="yellow", sheet=sheet)
        self.btn_sfx_up = Button(521, 355, 54, 44, "+", font_large, style="green", hover_style="yellow", sheet=sheet)

        self.btn_settings_test = Button(cx, 435, btn_w, 44, "TEST-SOUND", font_small, style="blue", hover_style="yellow", sheet=sheet)
        self.btn_settings_back = Button(cx, 515, btn_w, 48, "ZURÜCK", font_medium, style="green", hover_style="yellow", sheet=sheet)

        # Game Over Buttons
        self.btn_gameover_save = Button(
            cx, 515, btn_w, btn_h, "SCORE SPEICHERN", font_medium, style="green", hover_style="yellow", sheet=sheet
        )
        self.btn_gameover_restart = Button(
            cx, 575, btn_w, btn_h, "NOCHMAL SPIELEN", font_medium, style="blue", hover_style="yellow", sheet=sheet
        )
        self.btn_gameover_menu = Button(
            cx, 635, btn_w, btn_h, "HAUPTMENÜ", font_medium, style="red", hover_style="yellow", sheet=sheet
        )
        self.btn_gameover_view_scores = Button(
            cx, 515, btn_w, btn_h, "BESTENLISTE", font_medium, style="blue", hover_style="yellow", sheet=sheet
        )

        # Highscores Screen Buttons
        tab_w, tab_h = 210, 38
        self.btn_tab_top = Button(
            160, 95, tab_w, tab_h, "BESTE SCORES", font_small, style="blue", hover_style="yellow", sheet=sheet
        )
        self.btn_tab_recent = Button(
            380, 95, tab_w, tab_h, "ZEITVERLAUF", font_small, style="blue", hover_style="yellow", sheet=sheet
        )

        bot_w, bot_h = 240, 46
        self.btn_hs_back = Button(
            110, 655, bot_w, bot_h, "ZURÜCK ZUM MENÜ", font_small, style="red", hover_style="yellow", sheet=sheet
        )
        self.btn_hs_start = Button(
            400, 655, bot_w, bot_h, "SPIEL STARTEN", font_small, style="green", hover_style="yellow", sheet=sheet
        )

        # Text input for player name
        self.name_input = TextInput(cx, 450, btn_w, 46, font_medium, default_text="PILOT", max_length=10)

    def start_flight_transition(self):
        """Initializes the game and begins the flight animation transition into Level 1."""
        global player, enemy_manager, level
        self.player = Player(319, 650, "playerShip2_red")
        self.enemy_manager = EnemyManager()
        self.level = Level(0)
        self.number_enemies = 0
        self.lost_time = 0
        self.score_saved = False
        self.is_new_best = False

        # Sync globals for compatibility
        player = self.player
        enemy_manager = self.enemy_manager
        level = self.level
        audio_manager.apply_to_player(self.player)

        self.transition_frame = 0
        self.state = GameState.TRANSITION
        save_sound.play()

        # Initialize speed streaks for hyperspace warp effect
        self.speed_lines = [
            {
                "x": random.randint(20, width - 30),
                "y": random.randint(-750, 750),
                "speed": random.randint(28, 48),
                "alpha": random.randint(140, 255),
            }
            for _ in range(25)
        ]
        self.exhaust_particles = []

    def start_new_game(self):
        """Starts a fresh game session directly without transition."""
        global player, enemy_manager, level
        self.player = Player(319, 650, "playerShip2_red")
        self.enemy_manager = EnemyManager()
        self.level = Level(0)
        self.number_enemies = 0
        self.lost_time = 0
        self.score_saved = False
        self.is_new_best = False

        # Sync globals for compatibility
        player = self.player
        enemy_manager = self.enemy_manager
        level = self.level
        audio_manager.apply_to_player(self.player)

        self.state = GameState.PLAYING

    def run(self):
        """Main application loop."""
        while self.keep_going:
            self.clock.tick(self.fps)
            mouse_pos = pygame.mouse.get_pos()

            events = pg_get()
            for event in events:
                if event.type == PG_QUIT:
                    self.keep_going = False
                    music.fadeout(400)
                    return

                # Route event handling by state
                if self.state == GameState.MENU:
                    self._handle_menu_events(event, mouse_pos)
                elif self.state == GameState.SETTINGS:
                    self._handle_settings_events(event, mouse_pos)
                elif self.state == GameState.TRANSITION:
                    self._handle_transition_events(event)
                elif self.state == GameState.PLAYING:
                    self._handle_playing_events(event)
                elif self.state == GameState.PAUSED:
                    self._handle_paused_events(event, mouse_pos)
                elif self.state == GameState.GAME_OVER:
                    self._handle_gameover_events(event, mouse_pos)
                elif self.state == GameState.HIGHSCORES:
                    self._handle_highscores_events(event, mouse_pos)

            # Update gameplay logic if playing or transitioning
            if self.state == GameState.PLAYING:
                self._update_playing()
            elif self.state == GameState.TRANSITION:
                self._update_transition()

            # Render current state
            self._render(mouse_pos)
            update()

    # --------------------------------------------------------------------------
    # Event Handlers
    # --------------------------------------------------------------------------

    def _handle_transition_events(self, event):
        """Allows skipping the flight transition with Space, Return, Escape or click."""
        if event.type == pygame.KEYDOWN:
            if event.key in (K_SPACE, K_RETURN, K_ESCAPE):
                self._finish_transition()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._finish_transition()

    def _handle_menu_events(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key in (K_RETURN, K_SPACE):
                self.start_flight_transition()
            elif event.key == K_h:
                self.state = GameState.HIGHSCORES
            elif event.key == K_ESCAPE:
                self.keep_going = False
                music.fadeout(400)

        if self.btn_menu_start.is_clicked(event):
            self.start_flight_transition()
        elif self.btn_menu_highscores.is_clicked(event):
            self.state = GameState.HIGHSCORES
        elif self.btn_menu_settings.is_clicked(event):
            self.settings_return_state = GameState.MENU
            self.state = GameState.SETTINGS
        elif self.btn_menu_quit.is_clicked(event):
            self.keep_going = False
            music.fadeout(400)

    def _handle_settings_events(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
            self.state = self.settings_return_state
            return

        # Handle dragging/clicking volume sliders
        m_changed, new_m = self.music_slider.handle_event(event, audio_manager.music_volume)
        if m_changed:
            audio_manager.set_music_volume(new_m)

        s_changed, new_s = self.sfx_slider.handle_event(event, audio_manager.sfx_volume)
        if s_changed:
            audio_manager.set_sfx_volume(new_s)

        # Handle buttons
        if self.btn_music_down.is_clicked(event):
            audio_manager.change_music_volume(-0.1)
        elif self.btn_music_up.is_clicked(event):
            audio_manager.change_music_volume(+0.1)
        elif self.btn_sfx_down.is_clicked(event):
            audio_manager.change_sfx_volume(-0.1)
            audio_manager.play_test_sfx()
        elif self.btn_sfx_up.is_clicked(event):
            audio_manager.change_sfx_volume(+0.1)
            audio_manager.play_test_sfx()
        elif self.btn_settings_test.is_clicked(event):
            audio_manager.play_test_sfx()
        elif self.btn_settings_back.is_clicked(event):
            self.state = self.settings_return_state

    def _handle_playing_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                self.state = GameState.PAUSED

    def _handle_paused_events(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
            self.state = GameState.PLAYING
            return

        if self.btn_pause_resume.is_clicked(event):
            self.state = GameState.PLAYING
        elif self.btn_pause_settings.is_clicked(event):
            self.settings_return_state = GameState.PAUSED
            self.state = GameState.SETTINGS
        elif self.btn_pause_restart.is_clicked(event):
            self.start_new_game()
        elif self.btn_pause_menu.is_clicked(event):
            self.state = GameState.MENU

    def _handle_gameover_events(self, event, mouse_pos):
        if not self.score_saved:
            submitted = self.name_input.handle_event(event)
            if submitted or self.btn_gameover_save.is_clicked(event):
                self._save_score_and_view()
                return

        if event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
            self.state = GameState.MENU
            return

        if self.score_saved:
            if self.btn_gameover_view_scores.is_clicked(event):
                self.state = GameState.HIGHSCORES
        if self.btn_gameover_restart.is_clicked(event):
            self.start_flight_transition()
        elif self.btn_gameover_menu.is_clicked(event):
            self.state = GameState.MENU

    def _handle_highscores_events(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                self.state = GameState.MENU
            elif event.key in (K_RETURN, K_SPACE):
                self.start_flight_transition()
            elif event.key == K_TAB:
                self.highscore_view = "recent" if self.highscore_view == "top" else "top"

        if self.btn_tab_top.is_clicked(event):
            self.highscore_view = "top"
        elif self.btn_tab_recent.is_clicked(event):
            self.highscore_view = "recent"
        elif self.btn_hs_back.is_clicked(event):
            self.state = GameState.MENU
        elif self.btn_hs_start.is_clicked(event):
            self.start_flight_transition()

    def _save_score_and_view(self):
        """Saves player highscore to JSON and navigates to the Highscore board."""
        name = self.name_input.text.strip() or self.current_player_name or "PILOT"
        self.current_player_name = name
        rank, entry = self.highscore_manager.add_score(name, self.final_score, self.final_level)
        self.highlight_timestamp = entry.get("timestamp")
        self.score_saved = True
        save_sound.play()
        self.state = GameState.HIGHSCORES

    # --------------------------------------------------------------------------
    # Gameplay Updates
    # --------------------------------------------------------------------------

    def _update_playing(self):
        if int(self.player.live) <= 0:
            self.final_score = self.player.score
            self.final_level = max(1, self.level.number)
            self.is_new_best = self.highscore_manager.is_new_record(self.final_score)
            self.score_saved = False
            self.name_input.text = self.current_player_name
            self.name_input.active = True
            lose_sound.play()
            self.state = GameState.GAME_OVER
            return

        if self.enemy_manager.count() == 0:
            self.level.number += 1
            self.number_enemies += 3
            self.enemy_manager.add(screen, self.number_enemies, self.level.number)

        self.player.movement(screen)
        self.player.move_shots(screen, "up", self.enemy_manager.enemy_list)
        self.player.collision(self.enemy_manager.enemy_list)
        self.enemy_manager.move(screen, self.player)

    def _update_transition(self):
        self.transition_frame += 1

        # Accelerate background during hyperspace warp (frames 25..75)
        if 25 <= self.transition_frame <= 75:
            menu_level.scroll -= 12

        # Update speed lines
        for line in self.speed_lines:
            line["y"] += line["speed"]
            if line["y"] > height:
                line["y"] = random.randint(-160, -60)
                line["x"] = random.randint(20, width - 30)

        # Update exhaust particles
        for p in self.exhaust_particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["radius"] = max(0.5, p["radius"] - 0.22)
            p["alpha"] = max(0, p["alpha"] - 14)
            if p["alpha"] <= 0 or p["radius"] <= 0.5:
                self.exhaust_particles.remove(p)

        if self.transition_frame >= self.transition_max_frames:
            self._finish_transition()

    def _finish_transition(self):
        """Concludes the transition animation and hands control to the player."""
        self.state = GameState.PLAYING
        self.player.x_position = 319
        self.player.y_position = 650
        self.exhaust_particles.clear()
        self.speed_lines.clear()

    # --------------------------------------------------------------------------
    # Rendering
    # --------------------------------------------------------------------------

    def _render(self, mouse_pos):
        if self.state == GameState.MENU:
            self._draw_main_menu(mouse_pos)
        elif self.state == GameState.SETTINGS:
            self._draw_settings(mouse_pos)
        elif self.state == GameState.TRANSITION:
            self._draw_transition()
        elif self.state == GameState.PLAYING:
            self._draw_playing()
        elif self.state == GameState.PAUSED:
            self._draw_playing()
            self._draw_paused(mouse_pos)
        elif self.state == GameState.GAME_OVER:
            self._draw_playing()
            self._draw_game_over(mouse_pos)
        elif self.state == GameState.HIGHSCORES:
            self._draw_highscores(mouse_pos)

    def _draw_transition(self):
        menu_level.draw_background(screen)

        frame = self.transition_frame
        ship_w = self.menu_ship_img.get_width()
        ship_center_x = (width - ship_w) // 2

        current_ship_x = float(ship_center_x)
        current_ship_y = 250.0
        draw_ship = True
        flame_scale = 1.0

        # Phase 1: Ignition & Boost launch (frames 0..35)
        if frame < 12:
            current_ship_x += random.uniform(-1.5, 1.5)
            current_ship_y += random.uniform(-1.0, 1.0)
            flame_scale = 0.8 + (frame / 12.0) * 0.4
        elif frame < 35:
            p = (frame - 12) / 23.0
            current_ship_x += random.uniform(-1.2, 1.2)
            current_ship_y = 250.0 - (p ** 2.5) * 450.0
            flame_scale = 1.2 + p * 0.7
        # Phase 2: Hyperspace Warp (frames 35..55)
        elif frame < 55:
            draw_ship = False
            current_ship_y = -999.0
        # Phase 3: Combat Re-Entry & Deceleration (frames 55..95)
        elif frame < 95:
            p = (frame - 55) / 40.0
            ease = 1.0 - (1.0 - p) ** 3
            current_ship_y = 820.0 - ease * (820.0 - 650.0)
            flame_scale = 1.4 - ease * 0.8
        # Phase 4: Ready for Battle (frames 95..115)
        else:
            current_ship_y = 650.0
            flame_scale = 0.6

        # Draw Hyperspace Speed Lines during high speed (frames 20..85)
        if 20 <= frame <= 85:
            warp_alpha = 255
            if frame < 35:
                warp_alpha = int(255 * ((frame - 20) / 15.0))
            elif frame > 70:
                warp_alpha = int(255 * (1.0 - (frame - 70) / 15.0))
            warp_alpha = max(0, min(255, warp_alpha))

            for line in self.speed_lines:
                streak = self.speed_streak_img.copy()
                streak.set_alpha(int(line["alpha"] * (warp_alpha / 255.0)))
                screen.blit(streak, (line["x"], int(line["y"])))

        # Draw exhaust particles
        for p in self.exhaust_particles:
            color = p["color"]
            alpha = int(p["alpha"])
            pr = max(1, int(p["radius"]))
            part_surf = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(
                part_surf,
                (color[0], color[1], color[2], alpha),
                (pr + 1, pr + 1),
                pr,
            )
            screen.blit(part_surf, (int(p["x"] - pr - 1), int(p["y"] - pr - 1)))

        # Draw Ship & Thruster Flame if on screen
        if draw_ship and -80 < current_ship_y < height + 80:
            # Spawn new fiery exhaust particles
            nozzle_x = current_ship_x + 56
            nozzle_y = current_ship_y + 70
            for _ in range(3):
                self.exhaust_particles.append({
                    "x": nozzle_x + random.uniform(-6, 6),
                    "y": nozzle_y + random.uniform(0, 4),
                    "vx": random.uniform(-1.0, 1.0),
                    "vy": random.uniform(5.0, 12.0),
                    "radius": random.uniform(3.5, 6.5) * flame_scale,
                    "color": random.choice([
                        (255, 215, 50),
                        (255, 120, 20),
                        (255, 60, 20),
                        (255, 255, 220),
                    ]),
                    "alpha": 220,
                })

            # Thruster Flame
            flame_idx = (frame // 2) % len(self.flame_imgs)
            raw_flame = self.flame_imgs[flame_idx]
            fw = max(8, int(20 * flame_scale))
            fh = max(12, int(46 * flame_scale))
            scaled_flame = pygame.transform.smoothscale(raw_flame, (fw, fh))
            screen.blit(scaled_flame, (int(current_ship_x + 56 - fw // 2), int(current_ship_y + 68)))

            # Ship
            screen.blit(self.menu_ship_img, (int(current_ship_x), int(current_ship_y)))

        # Fading Menu Elements (Frames 0..20)
        if frame < 20:
            fade = 1.0 - (frame / 20.0)
            alpha_val = int(255 * fade)
            title_surf = pygame.Surface((width, 180), pygame.SRCALPHA)
            t1 = font_huge.render("EXCELLENT", True, (0, 220, 255))
            t2 = font_huge.render("SPACE SHOOTER", True, (255, 204, 0))
            title_surf.blit(t1, (width // 2 - t1.get_width() // 2, 20))
            title_surf.blit(t2, (width // 2 - t2.get_width() // 2, 70))
            title_surf.set_alpha(alpha_val)
            screen.blit(title_surf, (0, 70))

        # Phase 4 Arcade Ready Banner (Frames 90..115)
        if 90 <= frame < 115:
            pulse = math.sin((frame - 90) / 25.0 * math.pi)
            banner_alpha = int(255 * pulse)
            banner_surf = pygame.Surface((width, 140), pygame.SRCALPHA)
            b1 = font_huge.render("LEVEL 1", True, (0, 220, 255))
            b2 = font_large.render("★ MISSION START ★", True, (255, 204, 0))
            banner_surf.blit(b1, (width // 2 - b1.get_width() // 2, 10))
            banner_surf.blit(b2, (width // 2 - b2.get_width() // 2, 65))
            banner_surf.set_alpha(banner_alpha)
            screen.blit(banner_surf, (0, 270))

        # Bottom skip hint
        skip_label = font_thin_small.render("LEERTASTE / ESC: ÜBERSPRINGEN", True, (120, 140, 170))
        screen.blit(skip_label, (width // 2 - skip_label.get_width() // 2, 720))

    def _draw_main_menu(self, mouse_pos):
        menu_level.draw_background(screen)

        # Title
        draw_text(screen, "EXCELLENT", font_huge, (0, 220, 255), center_pos=(width // 2, 75))
        draw_text(screen, "SPACE SHOOTER", font_huge, (255, 204, 0), center_pos=(width // 2, 125))
        draw_text(screen, "DEFEND THE GALAXY", font_thin_medium, (180, 200, 230), center_pos=(width // 2, 175))

        # Floating decorative ship
        ticks = pygame.time.get_ticks()
        hover_offset = math.sin(ticks / 300.0) * 8.0
        ship_w = self.menu_ship_img.get_width()
        screen.blit(self.menu_ship_img, (width // 2 - ship_w // 2, int(235 + hover_offset)))

        # Best Score Teaser
        best_score = self.highscore_manager.get_best_score()
        draw_text(
            screen,
            f"REKORD: {best_score} PKT",
            font_small,
            (255, 215, 0),
            center_pos=(width // 2, 335),
        )

        # Buttons
        self.btn_menu_start.update_hover(mouse_pos)
        self.btn_menu_start.draw(screen)

        self.btn_menu_highscores.update_hover(mouse_pos)
        self.btn_menu_highscores.draw(screen)

        self.btn_menu_settings.update_hover(mouse_pos)
        self.btn_menu_settings.draw(screen)

        self.btn_menu_quit.update_hover(mouse_pos)
        self.btn_menu_quit.draw(screen)

        # Footer hints
        draw_text(
            screen,
            "WASD / PFEILTASTEN: FLIEGEN  •  LEERTASTE: FEUERN  •  ESC: BEENDEN",
            font_thin_small,
            (140, 160, 190),
            center_pos=(width // 2, 715),
        )

    def _draw_settings(self, mouse_pos):
        menu_level.draw_background(screen)

        # Header Title
        draw_text(screen, "AUDIO EINSTELLUNGEN", font_large, (255, 204, 0), center_pos=(width // 2, 60))

        # Main Panel
        panel_rect = pygame.Rect(75, 120, 600, 500)
        draw_panel(screen, panel_rect, bg_color=(15, 20, 35, 230), border_color=(0, 200, 255), border_width=2)

        # Music Section
        draw_text(screen, "HINTERGRUNDMUSIK", font_medium, (0, 220, 255), center_pos=(width // 2, 175))
        self.btn_music_down.update_hover(mouse_pos)
        self.btn_music_down.draw(screen)

        self.music_slider.draw(screen, audio_manager.music_volume)

        self.btn_music_up.update_hover(mouse_pos)
        self.btn_music_up.draw(screen)

        # SFX Section
        draw_text(screen, "SOUNDEFFEKTE (SFX)", font_medium, (0, 220, 255), center_pos=(width // 2, 305))
        self.btn_sfx_down.update_hover(mouse_pos)
        self.btn_sfx_down.draw(screen)

        self.sfx_slider.draw(screen, audio_manager.sfx_volume)

        self.btn_sfx_up.update_hover(mouse_pos)
        self.btn_sfx_up.draw(screen)

        # Test Sound Button
        self.btn_settings_test.update_hover(mouse_pos)
        self.btn_settings_test.draw(screen)

        # Back Button
        self.btn_settings_back.update_hover(mouse_pos)
        self.btn_settings_back.draw(screen)

        # Footer hints
        draw_text(
            screen,
            "KLICKE ODER ZIEHE AN DEN BALKEN  •  ESC: ZURÜCK",
            font_thin_small,
            (140, 160, 190),
            center_pos=(width // 2, 700),
        )

    def _draw_playing(self):
        self.level.draw_background(screen)
        self.enemy_manager.draw(screen)
        self.player.draw(screen)

        # HUD - Lives with visual miniature ship icons
        lives_label = font_thin_large.render("Lives:", True, (255, 255, 255))
        screen.blit(lives_label, (10, 10))
        cur_lives = max(0, int(self.player.live))
        icon_x = 10 + lives_label.get_width() + 10
        for i in range(cur_lives):
            # If down to 1 critical life, pulse warning
            if cur_lives == 1 and (pygame.time.get_ticks() // 250) % 2 == 0:
                continue
            screen.blit(self.life_icon, (icon_x + i * 40, 12))

        score_label = font_thin_large.render(f"Score: {self.player.score}", True, (255, 255, 255))
        screen.blit(score_label, (10, 42))

        # Top Center: Highscore to beat
        best_recorded = max(self.highscore_manager.get_best_score(), self.player.score)
        best_label = font_thin_small.render(f"Best: {best_recorded}", True, (255, 215, 0))
        screen.blit(best_label, (width // 2 - best_label.get_width() // 2, 12))

        # Top Right: Level
        level_label = font_thin_large.render(f"Level: {self.level.number}", True, (255, 255, 255))
        screen.blit(level_label, (width - level_label.get_width() - 10, 10))

    def _draw_paused(self, mouse_pos):
        # Dim overlay
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((10, 12, 20, 200))
        screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(175, 120, 400, 430)
        draw_panel(screen, panel_rect, bg_color=(15, 20, 35, 235), border_color=(255, 204, 0), border_width=2)

        draw_text(screen, "SPIEL PAUSIERT", font_large, (255, 204, 0), center_pos=(width // 2, 170))
        draw_text(
            screen,
            f"Score: {self.player.score}  •  Level: {self.level.number}",
            font_thin_medium,
            (220, 230, 245),
            center_pos=(width // 2, 230),
        )

        self.btn_pause_resume.update_hover(mouse_pos)
        self.btn_pause_resume.draw(screen)

        self.btn_pause_settings.update_hover(mouse_pos)
        self.btn_pause_settings.draw(screen)

        self.btn_pause_restart.update_hover(mouse_pos)
        self.btn_pause_restart.draw(screen)

        self.btn_pause_menu.update_hover(mouse_pos)
        self.btn_pause_menu.draw(screen)

    def _draw_game_over(self, mouse_pos):
        # Dim overlay
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((15, 10, 15, 215))
        screen.blit(overlay, (0, 0))

        # Title
        draw_text(screen, "GAME OVER", font_huge, (255, 60, 60), center_pos=(width // 2, 100))

        # Stats Card
        stats_rect = pygame.Rect(135, 150, 480, 170)
        draw_panel(screen, stats_rect, bg_color=(20, 22, 38, 240), border_color=(0, 200, 255), border_width=2)

        draw_text(screen, "ENDSTAND", font_medium, (255, 204, 0), center_pos=(width // 2, 185))
        draw_text(
            screen,
            f"PUNKTE: {self.final_score}   |   LEVEL: {self.final_level}",
            font_thin_large,
            (255, 255, 255),
            center_pos=(width // 2, 235),
        )

        if self.is_new_best:
            draw_text(
                screen,
                "★ NEUER REKORD! ★",
                font_medium,
                (255, 220, 50),
                center_pos=(width // 2, 285),
            )
        else:
            best = self.highscore_manager.get_best_score()
            draw_text(
                screen,
                f"AKTUELLER REKORD: {best} PKT",
                font_thin_small,
                (180, 200, 230),
                center_pos=(width // 2, 285),
            )

        # Name Entry / Saved indicator
        if not self.score_saved:
            draw_text(
                screen,
                "NAME EINGEBEN (ENTER ZUM SPEICHERN):",
                font_thin_medium,
                (255, 255, 255),
                center_pos=(width // 2, 380),
            )
            self.name_input.draw(screen)

            self.btn_gameover_save.update_hover(mouse_pos)
            self.btn_gameover_save.draw(screen)
        else:
            draw_text(
                screen,
                "✓ SCORE ERFOLGREICH GESPEICHERT!",
                font_medium,
                (60, 255, 120),
                center_pos=(width // 2, 420),
            )
            self.btn_gameover_view_scores.update_hover(mouse_pos)
            self.btn_gameover_view_scores.draw(screen)

        self.btn_gameover_restart.update_hover(mouse_pos)
        self.btn_gameover_restart.draw(screen)

        self.btn_gameover_menu.update_hover(mouse_pos)
        self.btn_gameover_menu.draw(screen)

    def _draw_highscores(self, mouse_pos):
        menu_level.draw_background(screen)

        # Header Title
        draw_text(screen, "HIGHSCORES", font_large, (255, 204, 0), center_pos=(width // 2, 50))

        # View Mode Tabs
        self.btn_tab_top.update_hover(mouse_pos)
        self.btn_tab_top.draw(screen, force_active=(self.highscore_view == "top"))

        self.btn_tab_recent.update_hover(mouse_pos)
        self.btn_tab_recent.draw(screen, force_active=(self.highscore_view == "recent"))

        # Table Panel
        panel_rect = pygame.Rect(45, 145, 660, 485)
        draw_panel(screen, panel_rect, bg_color=(15, 20, 35, 230), border_color=(0, 200, 255), border_width=2)

        # Table Headers
        header_y = 170
        draw_text(screen, "RANG", font_small, (255, 204, 0), topleft_pos=(65, header_y))
        draw_text(screen, "PILOT", font_small, (255, 204, 0), topleft_pos=(145, header_y))
        draw_text(screen, "SCORE", font_small, (255, 204, 0), topleft_pos=(310, header_y))
        draw_text(screen, "LEVEL", font_small, (255, 204, 0), topleft_pos=(440, header_y))
        draw_text(screen, "DATUM", font_small, (255, 204, 0), topleft_pos=(530, header_y))

        # Table Divider line
        pygame.draw.line(screen, (80, 120, 180), (60, 202), (690, 202), 1)

        # Fetch records according to active tab
        if self.highscore_view == "top":
            records = self.highscore_manager.get_top_scores(8)
        else:
            records = self.highscore_manager.get_recent_scores(8)

        if not records:
            draw_text(
                screen,
                "Noch keine Highscores vorhanden! Spiele eine Runde.",
                font_thin_medium,
                (200, 210, 230),
                center_pos=(width // 2, 350),
            )
        else:
            row_y = 216
            for idx, item in enumerate(records):
                rank_str = f"#{idx + 1}"
                name_str = item.get("name", "PILOT")
                score_str = str(item.get("score", 0))
                lvl_str = f"LVL {item.get('level', 1)}"
                date_str = item.get("date", "-")
                ts = item.get("timestamp")

                # Rank coloring
                if self.highscore_view == "top":
                    if idx == 0:
                        color = (255, 215, 0)      # Gold
                    elif idx == 1:
                        color = (215, 215, 225)    # Silver
                    elif idx == 2:
                        color = (205, 127, 50)     # Bronze
                    else:
                        color = (220, 235, 255)
                else:
                    color = (220, 235, 255)

                # Highlight freshly submitted highscore
                if self.highlight_timestamp and ts == self.highlight_timestamp:
                    highlight_rect = pygame.Rect(55, row_y - 4, 640, 36)
                    pygame.draw.rect(screen, (25, 75, 45), highlight_rect, border_radius=4)
                    pygame.draw.rect(screen, (50, 255, 120), highlight_rect, 1, border_radius=4)
                    color = (100, 255, 150)

                draw_text(screen, rank_str, font_thin_medium, color, topleft_pos=(65, row_y))
                draw_text(screen, name_str, font_thin_medium, color, topleft_pos=(145, row_y))
                draw_text(screen, score_str, font_thin_medium, color, topleft_pos=(310, row_y))
                draw_text(screen, lvl_str, font_thin_medium, color, topleft_pos=(440, row_y))
                draw_text(screen, date_str, font_thin_medium, color, topleft_pos=(530, row_y))

                row_y += 42

        # Bottom Buttons
        self.btn_hs_back.update_hover(mouse_pos)
        self.btn_hs_back.draw(screen)

        self.btn_hs_start.update_hover(mouse_pos)
        self.btn_hs_start.draw(screen)


def main():
    """Main entrypoint function."""
    game = GameManager()
    game.run()


if __name__ == "__main__":
    main()
