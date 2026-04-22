import pygame
from pathlib import Path
from audio import AudioBank
from game_data import LEVELS
from game_state import GameRuntime
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    HUD_H, BOSS_BAR_H, FIELD_TOP, FIELD_BOTTOM,
    COLOR_BG, COLOR_LEADER,
    FONT_SIZE, FONT_TITLE_SIZE, FONT_SUB_SIZE,
)
from ecs_core.ecs import World
from systems.input_system import InputSystem
from systems.fire_system import FireSystem
from systems.enemy_ai_system import EnemyAISystem
from systems.movement_system import MovementSystem
from systems.collision_system import CollisionSystem
from systems.damage_system import DamageSystem
from systems.render_system import RenderSystem
from entities.player import create_player
from entities.enemy import create_enemy_formation, create_leader_guard_line
from entities.leader import create_leader
from components.sprite import SpriteComponent
from components.input import InputComponent
from components.tag import TagComponent


class Game:
    """
    Runs the game loop and manages the main game states.
    """

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.font       = pygame.font.SysFont(None, FONT_SIZE)
        self.font_title = pygame.font.SysFont(None, FONT_TITLE_SIZE)
        self.font_sub   = pygame.font.SysFont(None, FONT_SUB_SIZE)
        self.audio = AudioBank()

        self.world = World()
        self._register_systems()

        self.runtime = GameRuntime()
        self.levels = LEVELS
        self.current_level_index = 0
        self.current_wave_index = 0
        self.current_wave_config = self.levels[0].waves[0]
        self.current_leader_config = self.levels[0].leader
        self.frame_count = 0
        self.transition_timer = 0
        self.transition_text = ""
        self.last_pickup_text = ""
        self.last_audio_state = ""
        self.pending_spawn_sound = ""
        self.show_debug = False
        self.reduced_flash = False
        self.guard_phase_active = False
        self.menu_options = ["Start Game", "Controls", "Quit"]
        self.menu_selected = 0
        self.pause_options = ["Resume", "Controls", "Quit"]
        self.end_options = ["Restart", "Controls", "Quit"]
        self.pause_selected = 0
        self.gameover_selected = 0
        self.victory_selected = 0
        self.controls_return_state = "title"

        self.player_eid  = None
        self.enemy_eids  = []
        self.backgrounds = self._load_backgrounds()


        self.heart_img = pygame.image.load("assets/sprites/heart.png").convert_alpha()
        self.heart_img = pygame.transform.scale(self.heart_img, (20, 20))
        self._handle_state_audio(force=True)



    def _register_systems(self) -> None:
        """
        Adds the systems to the world in the order they should run.
        """
        self.world.add_system(InputSystem())
        self.world.add_system(FireSystem())
        self.world.add_system(EnemyAISystem())
        self.world.add_system(MovementSystem())
        self.world.add_system(CollisionSystem())
        self.world.add_system(DamageSystem())
        self.world.add_system(RenderSystem())

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

    def _current_player_sprite_path(self) -> str:
        return f"assets/sprites/player_level{self.current_level_index + 1}.png"

    def _update_player_sprite(self) -> None:
        if self.player_eid is None:
            return

        sprite = self.world.get_component(self.player_eid, SpriteComponent)
        if sprite is not None:
            sprite.image_path = self._current_player_sprite_path()

    def _draw_background(self) -> None:
        background = None

        if self.runtime.state in ("title", "controls"):
            background = self.backgrounds.get("menu")
        else:
            background = self.backgrounds.get(f"level{self.current_level_index + 1}")

        if background is not None:
            self.screen.blit(background, (0, 0))

    def _reset(self) -> None:
        """
        Resets the game and starts a fresh run.
        """
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

    def _draw_menu_options(
        self,
        panel: pygame.Rect,
        options: list[str],
        selected_index: int,
        top: int,
    ) -> None:
        for index, option in enumerate(options):
            is_selected = index == selected_index
            color = (255, 240, 150) if is_selected else (210, 210, 210)
            prefix = "> " if is_selected else "  "
            option_surf = self.font_sub.render(f"{prefix}{option}", True, color)
            self.screen.blit(
                option_surf,
                option_surf.get_rect(centerx=panel.centerx, top=top + index * 34),
            )


    def run(self) -> None:
        """
        Runs the main loop until the player quits.
        """
        running = True

        while running:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1:
                        self.show_debug = not self.show_debug

                    if event.key == pygame.K_m:
                        self.audio.toggle_mute()
                        continue

                    if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.audio.adjust_volume(-0.05)
                        continue

                    if event.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
                        self.audio.adjust_volume(0.05)
                        continue

                    if event.key == pygame.K_f:
                        self.reduced_flash = not self.reduced_flash
                        continue

                    if self.runtime.state == "controls":
                        if self.runtime.menu_input_lock_timer > 0:
                            continue
                        if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                            self.audio.play("ui_confirm")
                            if self.controls_return_state in ("gameover", "victory"):
                                self.last_audio_state = self.controls_return_state
                            self._enter_state(self.controls_return_state, 10)
                        elif event.key == pygame.K_RETURN:
                            if not self.runtime.menu_confirm_ready:
                                continue
                            self.audio.play("ui_confirm")
                            if self.controls_return_state in ("gameover", "victory"):
                                self.last_audio_state = self.controls_return_state
                            self._enter_state(self.controls_return_state, 10)
                            self.runtime.menu_confirm_ready = False
                        continue

                    if event.key in (pygame.K_p, pygame.K_ESCAPE):
                        if self.runtime.state == "play":
                            self._enter_state("paused", 10)
                            continue
                        if self.runtime.state == "paused":
                            self.runtime.state = "play"
                            continue

                    if event.key == pygame.K_r:
                        if self.runtime.state in ("gameover", "victory"):
                            self.audio.play("ui_confirm")
                            self._reset()
                            continue

                    if self.runtime.state in ("title", "paused", "gameover", "victory"):
                        if self.runtime.menu_input_lock_timer > 0:
                            continue
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self._move_menu_selection(-1)
                            self.audio.play("ui_confirm")
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self._move_menu_selection(1)
                            self.audio.play("ui_confirm")
                        elif event.key == pygame.K_RETURN:
                            if not self.runtime.menu_confirm_ready:
                                continue
                            self.audio.play("ui_confirm")
                            if self._activate_current_menu_option():
                                events = []
                            self.runtime.menu_confirm_ready = False
                        elif event.key == pygame.K_q:
                            if self.runtime.state in ("title", "paused", "gameover", "victory"):
                                running = False
                        continue


            self._update_transition()

            if self.runtime.menu_input_lock_timer > 0:
                self.runtime.menu_input_lock_timer -= 1

            pressed = pygame.key.get_pressed()
            if not (pressed[pygame.K_SPACE] or pressed[pygame.K_RETURN]):
                self.runtime.menu_confirm_ready = True

            if self.runtime.state == "play":
                self.frame_count += 1

            self.screen.fill(COLOR_BG)
            self._draw_background()

            fDict_kwargs = {
                "screen": self.screen,
                "events": events,
                "game_state": self.runtime.state,
                "score": self.runtime.score,
                "lives": self.runtime.lives,
                "level_index": self.current_level_index,
                "leader_alive": self.runtime.leader_alive,
                "leader_hit_cooldown": self.runtime.leader_hit_cooldown,
                "wave_config": self.current_wave_config,
                "leader_config": self.current_leader_config,
                "frame_count": self.frame_count,
                "rapid_fire_timer": self.runtime.rapid_fire_timer,
                "shield_timer": self.runtime.shield_timer,
            }


            self.world.update(fDict_kwargs)
            self.runtime.leader_hit_cooldown = fDict_kwargs.get(
                "leader_hit_cooldown",
                self.runtime.leader_hit_cooldown,
            )

            if self.runtime.state == "play":
                if self.runtime.leader_hit_cooldown > 0:
                    self.runtime.leader_hit_cooldown -= 1

                if self.runtime.rapid_fire_timer > 0:
                    self.runtime.rapid_fire_timer -= 1

                if self.runtime.shield_timer > 0:
                    self.runtime.shield_timer -= 1

                if self.runtime.pickup_text_timer > 0:
                    self.runtime.pickup_text_timer -= 1
                    if self.runtime.pickup_text_timer == 0:
                        self.runtime.pickup_text = ""

                if self.runtime.status_text_timer > 0:
                    self.runtime.status_text_timer -= 1
                    if self.runtime.status_text_timer == 0:
                        self.runtime.status_text = ""

                if self.runtime.screen_flash_timer > 0:
                    self.runtime.screen_flash_timer -= 1

            if fDict_kwargs.get("lives", self.runtime.lives) < self.runtime.lives:
                self.runtime.player_flash_timer = 60
                self._set_screen_flash((220, 60, 60), 10)

            if self.runtime.player_flash_timer > 0:
                self.runtime.player_flash_timer -= 1
                player_entities = self.world.get_entities_with(InputComponent, SpriteComponent)
                for eid in player_entities:
                    sprite = self.world.get_component(eid, SpriteComponent)
                    sprite.visible = (self.runtime.player_flash_timer % 6) < 3
            else:
                player_entities = self.world.get_entities_with(InputComponent, SpriteComponent)
                for eid in player_entities:
                    sprite = self.world.get_component(eid, SpriteComponent)
                    sprite.visible = True

            self.runtime.score = fDict_kwargs.get("score", self.runtime.score)
            self.runtime.lives = fDict_kwargs.get("lives", self.runtime.lives)
            self.runtime.rapid_fire_timer += fDict_kwargs.get("rapid_fire_bonus", 0)
            self.runtime.shield_timer += fDict_kwargs.get("shield_bonus", 0)
            new_pickup_text = fDict_kwargs.get("pickup_text", "")
            if new_pickup_text:
                self.runtime.pickup_text = new_pickup_text
                self.runtime.pickup_text_timer = 90
                if new_pickup_text != self.last_pickup_text or self.runtime.pickup_text_timer == 90:
                    self.audio.play("powerup")
                if new_pickup_text == "SHIELD":
                    self._set_screen_flash((255, 220, 80), 8)
                elif new_pickup_text == "RAPID FIRE":
                    self._set_screen_flash((80, 180, 255), 8)
                elif new_pickup_text == "EXTRA LIFE":
                    self._set_screen_flash((80, 220, 120), 8)
                self.last_pickup_text = new_pickup_text

            self._play_frame_sounds(fDict_kwargs.get("sound_events", []))

            if self.guard_phase_active:
                tagged_entities = self.world.get_entities_with(TagComponent)
                guard_alive = False
                for eid in tagged_entities:
                    tag = self.world.get_component(eid, TagComponent)
                    if tag.label == "leader_guard":
                        guard_alive = True
                        break
                if not guard_alive:
                    self.guard_phase_active = False
                    self._set_status_text("LEADER ACTIVE", 90)
                    self._set_screen_flash((255, 170, 80), 10)

            if fDict_kwargs.get("wave_cleared") and not self.runtime.leader_alive:
                self._advance_after_wave_clear()

            if fDict_kwargs.get("trigger_victory"):
                self._advance_after_leader_defeat()
                if self.runtime.state == "victory":
                    self._enter_state("victory", 32)

            if fDict_kwargs.get("trigger_gameover"):
                self._enter_state("gameover", 32)

            self._handle_state_audio()


            if self.runtime.state in ("play", "paused"):
                self._draw_hud()

            if self.runtime.state == "title":
                self._draw_title_overlay()
            elif self.runtime.state == "controls":
                self._draw_controls_overlay()
            elif self.runtime.state == "transition":
                self._draw_transition_overlay()
            elif self.runtime.state == "paused":
                self._draw_pause_overlay()
            elif self.runtime.state == "gameover":
                self._draw_gameover_overlay()
            elif self.runtime.state == "victory":
                self._draw_victory_overlay()

            self._draw_feedback_overlay()

            if self.show_debug:
                self._draw_debug_panel()

            pygame.display.flip()
            self.clock.tick(FPS)


    def _draw_hud(self) -> None:
        """
        Draws the top HUD and the boss bar when needed.
        """
        score_surf = self.font.render(f"Score: {self.runtime.score}", True, (240, 240, 240))
        self.screen.blit(score_surf, score_surf.get_rect(topleft=(12, 14)))

        level_label = f"L{self.current_level_index + 1}  W{self.current_wave_index + 1}"
        if self.runtime.leader_alive:
            level_label = f"L{self.current_level_index + 1}  LEADER"
        level_surf = self.font.render(level_label, True, (200, 200, 200))
        self.screen.blit(level_surf, level_surf.get_rect(center=(SCREEN_WIDTH // 2, 24)))

        for i in range(self.runtime.lives):
            hx = SCREEN_WIDTH - 20 - i * 26
            self.screen.blit(self.heart_img, (hx - 20 , 12))

        pygame.draw.line(
            self.screen, (60, 60, 80),
            (0, HUD_H - 1), (SCREEN_WIDTH, HUD_H - 1), 2
        )

        powerup_surf = self.font.render(
            f"Powerups: {self._get_powerup_status()}",
            True,
            (220, 220, 220),
        )
        self.screen.blit(powerup_surf, powerup_surf.get_rect(topleft=(12, 36)))

        audio_surf = self.font.render(
            f"Audio: {self._get_audio_status()}",
            True,
            (220, 220, 220),
        )
        self.screen.blit(audio_surf, audio_surf.get_rect(topright=(SCREEN_WIDTH - 12, 36)))

        if self.runtime.pickup_text_timer > 0 and self.runtime.pickup_text:
            self._draw_attention_banner(
                self.runtime.pickup_text,
                (235, 245, 255),
                (70, 120, 180),
                HUD_H + 8,
            )

        if self.runtime.status_text_timer > 0 and self.runtime.status_text:
            self._draw_attention_banner(
                self.runtime.status_text,
                (255, 245, 170),
                (160, 120, 40),
                HUD_H + 44,
            )

        if self.runtime.leader_alive:
            self._draw_boss_bar()


    def _draw_boss_bar(self) -> None:
        """
        Draws the leader health bar at the bottom of the screen.
        """
        from components.health import HealthComponent
        from components.tag import TagComponent

        leader_entities = self.world.get_entities_with(TagComponent, HealthComponent)
        leader_hp  = 0
        leader_max = 1

        for eid in leader_entities:
            tag = self.world.get_component(eid, TagComponent)
            if tag.label == "leader":
                health = self.world.get_component(eid, HealthComponent)
                leader_hp  = health.hp
                leader_max = health.max_hp
                break

        bar_w   = 300
        bar_h   = 18
        bar_x   = SCREEN_WIDTH // 2 - bar_w // 2
        bar_y   = SCREEN_HEIGHT - BOSS_BAR_H + (BOSS_BAR_H - bar_h) // 2

        track_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        pygame.draw.rect(self.screen, (60, 20, 20), track_rect)

        pct      = leader_hp / leader_max
        fill_w   = int(bar_w * pct)
        fill_rect = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
        pygame.draw.rect(self.screen, COLOR_LEADER, fill_rect)

        pygame.draw.rect(self.screen, (200, 200, 200), track_rect, 2)

        label = self.font.render(f"LEADER  {leader_hp}/{leader_max}", True, (240, 240, 240))
        self.screen.blit(label, label.get_rect(
            centerx=SCREEN_WIDTH // 2,
            bottom=bar_y - 4,
        ))

    def _draw_feedback_overlay(self) -> None:
        if self.runtime.screen_flash_timer <= 0:
            return

        if self.runtime.state not in ("play", "paused", "transition"):
            return

        alpha = min(120, self.runtime.screen_flash_timer * 10)
        if self.reduced_flash:
            alpha = min(36, self.runtime.screen_flash_timer * 8)
        flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        flash.fill((*self.runtime.screen_flash_color, alpha))
        self.screen.blit(flash, (0, 0))

    def _get_audio_status(self) -> str:
        if not self.audio.enabled:
            return "OFF"
        if self.audio.muted:
            return f"MUTED {self.audio.get_volume_percent()}%"
        return f"ON {self.audio.get_volume_percent()}%"

    def _get_accessibility_status(self) -> str:
        if self.reduced_flash:
            return "Flash: Reduced"
        return "Flash: Normal"

    def _get_powerup_status(self) -> str:
        active = []

        if self.runtime.rapid_fire_timer > 0:
            active.append("Rapid")
        if self.runtime.shield_timer > 0:
            active.append("Shield")
        if self.runtime.pickup_text_timer > 0 and self.runtime.pickup_text == "EXTRA LIFE":
            active.append("Life +1")

        if not active:
            return "None"

        return ", ".join(active)

    def _draw_debug_panel(self) -> None:
        panel = pygame.Rect(10, SCREEN_HEIGHT - 126, 260, 112)
        surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        surf.fill((8, 8, 18, 190))
        self.screen.blit(surf, panel.topleft)
        pygame.draw.rect(self.screen, (90, 90, 130), panel, 2)

        wave_text = f"{self.current_wave_index + 1}"
        if self.runtime.leader_alive:
            wave_text = "Leader"

        lines = [
            f"DEBUG  FPS: {self.clock.get_fps():.1f}",
            f"State: {self.runtime.state}",
            f"Level: {self.current_level_index + 1}   Wave: {wave_text}",
            f"Lives: {self.runtime.lives}   Audio: {self._get_audio_status()}",
            f"Powerups: {self._get_powerup_status()}",
            self._get_accessibility_status(),
        ]

        y = panel.top + 10
        for line in lines:
            text = self.font.render(line, True, (230, 230, 230))
            self.screen.blit(text, (panel.left + 10, y))
            y += 17

    def _draw_attention_banner(
        self,
        text: str,
        text_color: tuple[int, int, int],
        border_color: tuple[int, int, int],
        top_y: int,
    ) -> None:
        banner = pygame.Rect(SCREEN_WIDTH // 2 - 140, top_y, 280, 28)
        shade = pygame.Surface((banner.width, banner.height), pygame.SRCALPHA)
        shade.fill((12, 16, 26, 210))
        self.screen.blit(shade, banner.topleft)
        pygame.draw.rect(self.screen, border_color, banner, 2)

        shadow = self.font.render(text, True, (20, 20, 20))
        shadow_rect = shadow.get_rect(center=(banner.centerx + 1, banner.centery + 1))
        self.screen.blit(shadow, shadow_rect)

        surf = self.font.render(text, True, text_color)
        rect = surf.get_rect(center=banner.center)
        self.screen.blit(surf, rect)


    def _draw_overlay_panel(self, height: int = 240) -> pygame.Rect:
        """
        Draws the dark panel used by menu and state overlays.
        """
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - height // 2, 440, height)
        dark  = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        dark.fill((10, 10, 20, 210))
        self.screen.blit(dark, panel.topleft)
        pygame.draw.rect(self.screen, (100, 100, 140), panel, 2)
        return panel

    def _draw_title_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        title = self.font_title.render("INVASION SPACERS", True, (0, 200, 255))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        self._draw_menu_options(panel, self.menu_options, self.menu_selected, panel.top + 92)

        hint = self.font.render("Menu: Up / Down    Confirm: Enter", True, (140, 140, 160))
        self.screen.blit(hint, hint.get_rect(centerx=panel.centerx, top=panel.top + 192))

        hint2 = self.font.render("M: Mute  - / +: Volume  F: Reduced Flash", True, (140, 140, 160))
        self.screen.blit(hint2, hint2.get_rect(centerx=panel.centerx, top=panel.top + 214))

    def _draw_controls_overlay(self) -> None:
        panel = self._draw_overlay_panel(300)

        title = self.font_title.render("CONTROLS", True, (240, 240, 240))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 24))

        lines = [
            "Move: Arrow Keys / WASD",
            "Fire: Space / Left Shift / Right Shift",
            "Pause / Resume: P or ESC",
            "Mute Audio: M",
            "Volume: - / +",
            "Reduced Flash: F",
            "Debug Toggle: F1",
            "Quit from Menus: Q",
        ]

        for index, line in enumerate(lines):
            surf = self.font.render(line, True, (210, 210, 210))
            self.screen.blit(surf, surf.get_rect(centerx=panel.centerx, top=panel.top + 78 + index * 22))

        back = self.font.render("Press ESC, Backspace, or Enter to return", True, (180, 180, 180))
        self.screen.blit(back, back.get_rect(centerx=panel.centerx, top=panel.top + 256))

    def _draw_pause_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        paused = self.font_title.render("PAUSED", True, (240, 240, 100))
        self.screen.blit(paused, paused.get_rect(centerx=panel.centerx, top=panel.top + 50))

        self._draw_menu_options(panel, self.pause_options, self.pause_selected, panel.top + 96)

        controls = self.font.render("Menu: Up / Down    Confirm: Enter", True, (180, 180, 180))
        self.screen.blit(controls, controls.get_rect(centerx=panel.centerx, top=panel.top + 198))

        hint = self.font.render("ESC or P also resumes    M: Mute    F1: Debug", True, (180, 180, 180))
        self.screen.blit(hint, hint.get_rect(centerx=panel.centerx, top=panel.top + 220))

    def _draw_transition_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        title = self.font_title.render(self.transition_text, True, (240, 240, 240))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 55))

        ready = self.font_sub.render("Get Ready", True, (200, 200, 120))
        self.screen.blit(ready, ready.get_rect(centerx=panel.centerx, top=panel.top + 130))

    def _draw_gameover_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        tint = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        tint.fill((90, 20, 20, 70))
        self.screen.blit(tint, panel.topleft)
        pygame.draw.rect(self.screen, (150, 70, 70), panel, 2)

        title = self.font_title.render("GAME OVER", True, (245, 245, 245))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        score = self.font_sub.render(f"Final Score: {self.runtime.score}", True, (245, 245, 245))
        self.screen.blit(score, score.get_rect(centerx=panel.centerx, top=panel.top + 100))

        self._draw_menu_options(panel, self.end_options, self.gameover_selected, panel.top + 128)

        quit_text = self.font.render("Menu: Up / Down    Confirm: Enter", True, (230, 230, 230))
        self.screen.blit(quit_text, quit_text.get_rect(centerx=panel.centerx, top=panel.top + 222))

    def _draw_victory_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        title = self.font_title.render("VICTORY!", True, (100, 220, 100))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        score = self.font_sub.render(f"Final Score: {self.runtime.score}", True, (240, 240, 240))
        self.screen.blit(score, score.get_rect(centerx=panel.centerx, top=panel.top + 100))

        self._draw_menu_options(panel, self.end_options, self.victory_selected, panel.top + 126)

        quit_text = self.font.render("Menu: Up / Down    Confirm: Enter", True, (180, 180, 180))
        self.screen.blit(quit_text, quit_text.get_rect(centerx=panel.centerx, top=panel.top + 224))

    def shutdown(self) -> None:
        self.audio.shutdown()
