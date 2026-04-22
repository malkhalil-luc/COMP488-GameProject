from pathlib import Path

import pygame


class AudioBank:
    def __init__(self) -> None:
        self.enabled = False
        self.muted = False

        self.music_volume = 0.34
        self.sfx_volume = 0.30
        self.ui_volume = 0.28

        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._loop_channel: pygame.mixer.Channel | None = None
        self._ui_channel: pygame.mixer.Channel | None = None
        self._alert_channel: pygame.mixer.Channel | None = None
        self._fire_channel: pygame.mixer.Channel | None = None
        self._enemy_channel: pygame.mixer.Channel | None = None
        self._hit_channel: pygame.mixer.Channel | None = None
        self._last_play_ms: dict[str, int] = {}
        self._cooldowns_ms = {
            "fire": 70,
            "enemy_fire": 140,
            "leader_fire": 120,
            "hit_enemy": 50,
            "player_hurt": 180,
            "powerup": 180,
            "ui_confirm": 120,
            "leader_spawn": 250,
            "level_transition": 250,
            "in_level": 250,
            "game_over": 300,
            "victory": 300,
        }
        self._sound_multipliers = {
            "ambience": 0.95,
            "bg_loop": 1.0,
            "fire": 0.34,
            "enemy_fire": 0.16,
            "leader_fire": 0.24,
            "hit_enemy": 0.50,
            "player_hurt": 0.82,
            "powerup": 0.62,
            "ui_confirm": 0.80,
            "game_over": 1.00,
            "leader_spawn": 0.98,
            "level_transition": 0.72,
            "in_level": 0.62,
            "victory": 0.95,
        }

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

            pygame.mixer.set_num_channels(20)
            pygame.mixer.set_reserved(6)
            self._loop_channel = pygame.mixer.Channel(0)
            self._ui_channel = pygame.mixer.Channel(1)
            self._alert_channel = pygame.mixer.Channel(2)
            self._fire_channel = pygame.mixer.Channel(3)
            self._enemy_channel = pygame.mixer.Channel(4)
            self._hit_channel = pygame.mixer.Channel(5)
            self._load_sounds()
            self._apply_volumes()
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def _load_sounds(self) -> None:
        sounds_dir = Path(__file__).resolve().parent / "assets" / "sounds"

        sound_files = {
            "fire": "fire.wav",
            "enemy_fire": "enemy_fire.wav",
            "leader_fire": "leader_fire.wav",
            "hit_enemy": "hit_enemy.wav",
            "player_hurt": "player_hurt.wav",
            "powerup": "powerup.wav",
            "ui_confirm": "ui_confirm.wav",
            "game_over": "game_over.wav",
            "leader_spawn": "leader_spawn.wav",
            "level_transition": "level_transition.wav",
            "in_level": "in_level.wav",
            "victory": "victory.wav",
            "ambience": "ambience.wav",
            "bg_loop": "bg_loop.wav",
        }

        for name, filename in sound_files.items():
            path = sounds_dir / filename
            if path.exists():
                self._sounds[name] = pygame.mixer.Sound(str(path))

    def _apply_volumes(self) -> None:
        if not self.enabled:
            return

        if self._loop_channel is not None:
            self._loop_channel.set_volume(0.0 if self.muted else self.music_volume)
        if self._ui_channel is not None:
            self._ui_channel.set_volume(0.0 if self.muted else self.ui_volume)
        if self._alert_channel is not None:
            self._alert_channel.set_volume(0.0 if self.muted else self.sfx_volume)
        if self._fire_channel is not None:
            self._fire_channel.set_volume(0.0 if self.muted else self.sfx_volume * 0.85)
        if self._enemy_channel is not None:
            self._enemy_channel.set_volume(0.0 if self.muted else self.sfx_volume * 0.72)
        if self._hit_channel is not None:
            self._hit_channel.set_volume(0.0 if self.muted else self.sfx_volume * 0.80)

        for key, sound in self._sounds.items():
            if key in ("bg_loop", "ambience"):
                base = self.music_volume
            elif key == "ui_confirm":
                base = self.ui_volume
            else:
                base = self.sfx_volume
            multiplier = self._sound_multipliers.get(key, 1.0)
            sound.set_volume(0.0 if self.muted else base * multiplier)

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        self._apply_volumes()

    def adjust_volume(self, delta: float) -> None:
        self.music_volume = max(0.0, min(1.0, self.music_volume + delta))
        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume + delta))
        self.ui_volume = max(0.0, min(1.0, self.ui_volume + delta))
        self._apply_volumes()

    def get_volume_percent(self) -> int:
        return int(round(self.music_volume * 100))

    def play(self, name: str) -> None:
        if not self.enabled or self.muted:
            return

        sound = self._sounds.get(name)
        if sound is None:
            return

        now = pygame.time.get_ticks()
        cooldown = self._cooldowns_ms.get(name, 0)
        last_play = self._last_play_ms.get(name, -cooldown)
        if now - last_play < cooldown:
            return
        self._last_play_ms[name] = now

        if name == "ui_confirm" and self._ui_channel is not None:
            self._ui_channel.play(sound)
            return

        if name in ("leader_spawn", "level_transition", "in_level", "game_over", "victory") and self._alert_channel is not None:
            self._alert_channel.play(sound)
            return

        if name == "fire" and self._fire_channel is not None:
            if not self._fire_channel.get_busy():
                self._fire_channel.play(sound)
            return

        if name in ("enemy_fire", "leader_fire") and self._enemy_channel is not None:
            if not self._enemy_channel.get_busy():
                self._enemy_channel.play(sound)
            return

        if name == "hit_enemy" and self._hit_channel is not None:
            if not self._hit_channel.get_busy():
                self._hit_channel.play(sound)
            return

        channel = pygame.mixer.find_channel()
        if channel is not None:
            channel.play(sound)

    def play_loop(self, name: str) -> None:
        if not self.enabled or self._loop_channel is None:
            return

        sound = self._sounds.get(name)
        if sound is None:
            return

        if self._loop_channel.get_sound() is sound:
            return

        self._loop_channel.stop()
        self._loop_channel.play(sound, loops=-1)
        self._apply_volumes()

    def stop_loop(self) -> None:
        if self._loop_channel is not None:
            self._loop_channel.stop()

    def shutdown(self) -> None:
        if not self.enabled:
            return

        self.stop_loop()
        if self._ui_channel is not None:
            self._ui_channel.stop()
        if self._alert_channel is not None:
            self._alert_channel.stop()
        if self._fire_channel is not None:
            self._fire_channel.stop()
        if self._enemy_channel is not None:
            self._enemy_channel.stop()
        if self._hit_channel is not None:
            self._hit_channel.stop()
