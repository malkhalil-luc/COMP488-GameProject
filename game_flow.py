from pathlib import Path
import random

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT
from components.sprite import SpriteComponent
from components.tag import TagComponent
from entities.enemy import create_enemy_formation, create_leader_guard_line
from entities.leader import create_leader
from entities.player import create_player
from score_store import save_score


class GameFlowMixin:
    def _load_background(self, path: str) -> pygame.Surface | None:
        file_path = Path(path)
        if not file_path.exists():
            return None

        try:
            image = pygame.image.load(str(file_path)).convert()
            return pygame.transform.smoothscale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            return None

    def _load_backgrounds(self) -> dict[str, pygame.Surface | None]:
        return {
            "menu": self._load_background("assets/backgrounds/menu_bg.png"),
            "level1": self._load_background("assets/backgrounds/level1_bg.png"),
            "level2": self._load_background("assets/backgrounds/level2_bg.png"),
            "level3": self._load_background("assets/backgrounds/level3_bg.png"),
        }

    def _create_star_layers(self) -> list[list[dict[str, float | tuple[int, int, int]]]]:
        layers = []
        layer_specs = [
            (24, 0.18, (140, 150, 175), 1),
            (18, 0.34, (190, 200, 220), 2),
            (12, 0.55, (245, 245, 255), 3),
        ]

        for count, speed, color, size in layer_specs:
            stars = []
            for _ in range(count):
                stars.append({
                    "x": float(random.randint(0, SCREEN_WIDTH)),
                    "y": float(random.randint(0, SCREEN_HEIGHT)),
                    "speed": speed + random.uniform(-0.05, 0.05),
                    "size": size,
                    "color": color,
                })
            layers.append(stars)

        return layers

    def _star_speed_scale(self) -> float:
        if self.runtime.state in ("title", "controls"):
            return 0.35
        if self.runtime.state in ("paused", "gameover", "victory"):
            return 0.25

        level_scales = [0.55, 0.75, 0.95]
        index = min(self.current_level_index, len(level_scales) - 1)
        return level_scales[index]

    def _update_star_layers(self) -> None:
        speed_scale = self._star_speed_scale()

        for stars in self.star_layers:
            for star in stars:
                star["y"] += float(star["speed"]) * speed_scale
                star["x"] += float(star["speed"]) * 0.12 * speed_scale

                if float(star["y"]) > SCREEN_HEIGHT + 4:
                    star["y"] = -6.0
                    star["x"] = float(random.randint(0, SCREEN_WIDTH))

                if float(star["x"]) > SCREEN_WIDTH + 4:
                    star["x"] = -4.0

    def _draw_star_layers(self) -> None:
        for stars in self.star_layers:
            for star in stars:
                pygame.draw.circle(
                    self.screen,
                    star["color"],
                    (int(float(star["x"])), int(float(star["y"]))),
                    int(star["size"]),
                )

    def _current_player_sprite_path(self) -> str:
        return f"assets/sprites/player_level{self.current_level_index + 1}.png"

    def _update_life_icon(self) -> None:
        try:
            icon = pygame.image.load(self._current_player_sprite_path()).convert_alpha()
            self.life_icon_img = pygame.transform.scale(icon, (22, 22))
        except pygame.error:
            self.life_icon_img = None

    def _update_player_sprite(self) -> None:
        if self.player_eid is None:
            return

        sprite = self.world.get_component(self.player_eid, SpriteComponent)
        if sprite is not None:
            sprite.image_path = self._current_player_sprite_path()
        self._update_life_icon()

    def _draw_background(self) -> None:
        if self.runtime.state in ("title", "controls"):
            background = self.backgrounds.get("menu")
        else:
            background = self.backgrounds.get(f"level{self.current_level_index + 1}")

        if background is not None:
            self.screen.blit(background, (0, 0))

        self._draw_star_layers()

    def _prepare_score_entry(self) -> None:
        self.runtime.score_name_input = ""
        self.runtime.score_saved = False

    def _save_current_score(self) -> None:
        if self.runtime.score_saved:
            return

        self.high_scores = save_score(self.runtime.score_name_input, self.runtime.score)
        self.runtime.score_saved = True
        self._set_status_text("SCORE SAVED", 90)

    def _reset(self) -> None:
        self.runtime.reset_run_values()
        self.current_level_index = 0
        self.current_wave_index = 0
        self.frame_count = 0
        self.transition_timer = 0
        self.transition_text = ""
        self.current_wave_config = self.levels[0].waves[0]
        self.current_leader_config = self.levels[0].leader
        self.world.clear()

        self.player_eid = create_player(self.world, self._current_player_sprite_path())
        self._start_current_wave()

    def _clear_non_player_entities(self) -> None:
        tagged_entities = self.world.get_entities_with(TagComponent)

        for eid in list(tagged_entities):
            tag = self.world.get_component(eid, TagComponent)
            if tag.label != "player":
                self.world.remove_entity(eid)

    def _start_transition(self, text: str, frames: int = 90, sound_name: str = "level_transition") -> None:
        self.runtime.state = "transition"
        self.transition_text = text
        self.transition_timer = frames
        if sound_name:
            self.audio.play(sound_name)

    def _start_current_wave(self) -> None:
        self._clear_non_player_entities()
        level = self.levels[self.current_level_index]
        self.current_wave_config = level.waves[self.current_wave_index]
        self.current_leader_config = level.leader
        self.runtime.leader_alive = False
        self.guard_phase_active = False
        self._update_player_sprite()
        self.enemy_eids = create_enemy_formation(
            self.world,
            self.current_wave_config,
            self.current_level_index,
        )
        transition_sound = "level_transition"
        if self.current_wave_index > 0:
            transition_sound = "in_level"
        self._start_transition(
            f"{level.name}  -  Wave {self.current_wave_index + 1}",
            sound_name=transition_sound,
        )

    def _start_level_leader(self) -> None:
        self._clear_non_player_entities()
        level = self.levels[self.current_level_index]
        self.current_leader_config = level.leader
        self._update_player_sprite()
        create_leader(self.world, self.current_leader_config, self.current_level_index)
        create_leader_guard_line(self.world, self.current_level_index)
        self.runtime.leader_alive = True
        self.guard_phase_active = True
        self.pending_spawn_sound = "leader_spawn"
        self._set_status_text("DEFENSE LINE INCOMING", 110)
        self._start_transition(f"{level.name}  -  Leader", sound_name="level_transition")

    def _advance_after_wave_clear(self) -> None:
        level = self.levels[self.current_level_index]

        if self.current_wave_index < len(level.waves) - 1:
            self.current_wave_index += 1
            self._start_current_wave()
        else:
            self._start_level_leader()

    def _advance_after_leader_defeat(self) -> None:
        self.runtime.leader_alive = False
        self.guard_phase_active = False
        self._clear_non_player_entities()

        if self.current_level_index < len(self.levels) - 1:
            self.current_level_index += 1
            self.current_wave_index = 0
            self._start_current_wave()
        else:
            self.runtime.state = "victory"

    def _update_transition(self) -> None:
        if self.runtime.state != "transition":
            return

        if self.transition_timer > 0:
            self.transition_timer -= 1

        if self.transition_timer <= 0:
            self.transition_text = ""
            self.runtime.state = "play"
            if self.pending_spawn_sound:
                self.audio.play(self.pending_spawn_sound)
                self.pending_spawn_sound = ""

    def _set_status_text(self, text: str, timer: int = 90) -> None:
        self.runtime.status_text = text
        self.runtime.status_text_timer = timer

    def _set_screen_flash(self, color: tuple[int, int, int], timer: int = 10) -> None:
        self.runtime.screen_flash_color = color
        if self.reduced_flash:
            self.runtime.screen_flash_timer = min(timer, 3)
        else:
            self.runtime.screen_flash_timer = timer

    def _lock_menu_input(self, frames: int = 16) -> None:
        self.runtime.menu_input_lock_timer = frames
        self.runtime.menu_confirm_ready = False

    def _enter_state(self, new_state: str, lock_frames: int = 0) -> None:
        self.runtime.state = new_state

        if new_state == "paused":
            self.pause_selected = 0
        elif new_state == "gameover":
            self.gameover_selected = 0
        elif new_state == "victory":
            self.victory_selected = 0

        if new_state in ("title", "controls", "paused", "gameover", "victory"):
            self._lock_menu_input(lock_frames)

    def _handle_state_audio(self, force: bool = False) -> None:
        if not force and self.runtime.state == self.last_audio_state:
            return

        self.last_audio_state = self.runtime.state

        if self.runtime.state in ("title", "controls", "paused"):
            self.audio.play_loop("ambience")
            return

        if self.runtime.state in ("play", "transition"):
            self.audio.play_loop("bg_loop")
            return

        if self.runtime.state == "gameover":
            self.audio.play_loop("ambience")
            self.audio.play("game_over")
            return

        if self.runtime.state == "victory":
            self.audio.play_loop("ambience")
            self.audio.play("victory")

    def _play_frame_sounds(self, sound_events: list[str]) -> None:
        played_counts: dict[str, int] = {}
        caps = {
            "fire": 1,
            "enemy_fire": 1,
            "leader_fire": 1,
            "hit_enemy": 2,
            "player_hurt": 1,
            "powerup": 1,
            "ui_confirm": 1,
            "leader_spawn": 1,
            "level_transition": 1,
            "in_level": 1,
            "game_over": 1,
            "victory": 1,
        }

        for sound_name in sound_events:
            count = played_counts.get(sound_name, 0)
            if count >= caps.get(sound_name, 1):
                continue

            self.audio.play(sound_name)
            played_counts[sound_name] = count + 1

    def _move_menu_selection(self, direction: int) -> None:
        if self.runtime.state == "title":
            self.menu_selected = (self.menu_selected + direction) % len(self.menu_options)
        elif self.runtime.state == "paused":
            self.pause_selected = (self.pause_selected + direction) % len(self.pause_options)
        elif self.runtime.state == "gameover":
            self.gameover_selected = (self.gameover_selected + direction) % len(self.end_options)
        elif self.runtime.state == "victory":
            self.victory_selected = (self.victory_selected + direction) % len(self.end_options)

    def _activate_current_menu_option(self) -> bool:
        if self.runtime.state == "title":
            choice = self.menu_options[self.menu_selected]
            if choice == "Start Game":
                self._reset()
                return True
            if choice == "Controls":
                self.controls_return_state = "title"
                self._enter_state("controls", 8)
                return False
            if choice == "Quit":
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return False

        elif self.runtime.state == "paused":
            choice = self.pause_options[self.pause_selected]
            if choice == "Resume":
                self.runtime.state = "play"
                return False
            if choice == "Controls":
                self.controls_return_state = "paused"
                self._enter_state("controls", 8)
                return False
            if choice == "Quit":
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return False

        elif self.runtime.state == "gameover":
            choice = self.end_options[self.gameover_selected]
            if choice == "Save Score":
                self._save_current_score()
                return False
            if choice == "Restart":
                self._reset()
                return True
            if choice == "Controls":
                self.controls_return_state = "gameover"
                self._enter_state("controls", 8)
                return False
            if choice == "Quit":
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return False

        elif self.runtime.state == "victory":
            choice = self.end_options[self.victory_selected]
            if choice == "Save Score":
                self._save_current_score()
                return False
            if choice == "Restart":
                self._reset()
                return True
            if choice == "Controls":
                self.controls_return_state = "victory"
                self._enter_state("controls", 8)
                return False
            if choice == "Quit":
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return False

        return False
