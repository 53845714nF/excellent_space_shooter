"""
Audio Manager Module.
Handles background music, sound effects, volume control and persistent audio settings.
"""
import json
import os
import pygame
from paths import get_save_path, asset_path


class AudioManager:
    """
    Manages music and sound effect volumes with persistent JSON settings.
    """

    def __init__(self, settings_path=None):
        self.settings_path = settings_path or get_save_path("settings.json")
        self.music_volume = 0.3
        self.sfx_volume = 0.6
        self.music_sound = None
        self.registered_sfx = []
        self.test_sound = None

        self.load_settings()

    def load_settings(self):
        """Loads audio settings from JSON file."""
        if not os.path.exists(self.settings_path):
            self.save_settings()
            return

        try:
            with open(self.settings_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    self.music_volume = max(0.0, min(1.0, float(data.get("music_volume", 0.3))))
                    self.sfx_volume = max(0.0, min(1.0, float(data.get("sfx_volume", 0.6))))
        except (json.JSONDecodeError, OSError, ValueError):
            self.music_volume = 0.3
            self.sfx_volume = 0.6

    def save_settings(self):
        """Saves current audio settings to JSON file."""
        try:
            temp_path = f"{self.settings_path}.tmp"
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(
                    {
                        "music_volume": round(self.music_volume, 2),
                        "sfx_volume": round(self.sfx_volume, 2),
                    },
                    file,
                    indent=2,
                )
            os.replace(temp_path, self.settings_path)
        except OSError as exc:
            print(f"Warnung: Audioeinstellungen konnten nicht gespeichert werden: {exc}")

    def set_music_sound(self, sound: pygame.mixer.Sound):
        """Registers the main background music sound."""
        self.music_sound = sound
        if self.music_sound:
            self.music_sound.set_volume(self.music_volume)

    def set_music_volume(self, volume: float):
        """Sets music volume between 0.0 and 1.0."""
        self.music_volume = max(0.0, min(1.0, round(volume, 2)))
        if self.music_sound:
            self.music_sound.set_volume(self.music_volume)
        self.save_settings()

    def change_music_volume(self, delta: float):
        """Changes music volume by delta (+/- 0.1)."""
        self.set_music_volume(self.music_volume + delta)

    def set_sfx_volume(self, volume: float):
        """Sets sound effects volume between 0.0 and 1.0."""
        self.sfx_volume = max(0.0, min(1.0, round(volume, 2)))
        for sound in self.registered_sfx:
            try:
                sound.set_volume(self.sfx_volume)
            except Exception:
                pass
        if self.test_sound:
            try:
                self.test_sound.set_volume(self.sfx_volume)
            except Exception:
                pass
        self.save_settings()

    def change_sfx_volume(self, delta: float):
        """Changes sound effects volume by delta (+/- 0.1)."""
        self.set_sfx_volume(self.sfx_volume + delta)

    def register_sfx(self, sound: pygame.mixer.Sound):
        """Registers a sound effect and applies current SFX volume."""
        if sound is not None:
            sound.set_volume(self.sfx_volume)
            if sound not in self.registered_sfx:
                self.registered_sfx.append(sound)

    def apply_to_player(self, player):
        """Applies SFX volume to player's shoot and shield sounds."""
        if player:
            if hasattr(player, "shoot_sound"):
                self.register_sfx(player.shoot_sound)
            if hasattr(player, "lost_live_sound"):
                self.register_sfx(player.lost_live_sound)

    def apply_to_ship(self, ship):
        """Applies SFX volume to a ship's shield sound."""
        if ship and hasattr(ship, "lost_live_sound"):
            self.register_sfx(ship.lost_live_sound)

    def play_test_sfx(self):
        """Plays a preview sound effect at current SFX volume."""
        if self.test_sound is None:
            try:
                self.test_sound = pygame.mixer.Sound(asset_path("sounds", "sfx_laser2.ogg"))
            except Exception:
                return
        self.test_sound.set_volume(self.sfx_volume)
        self.test_sound.play()


audio_manager = AudioManager()
