import pygame

from audio import AudioBank
from components.input import InputComponent
from components.sprite import SpriteComponent
from components.tag import TagComponent
from config import (
    COLOR_BG,
    FONT_SIZE,
    FONT_SUB_SIZE,
    FONT_TITLE_SIZE,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TITLE,
)
from ecs_core.ecs import World
from game_data import LEVELS
from game_flow import GameFlowMixin
from game_state import GameRuntime
from game_view import GameViewMixin
from score_store import load_scores
from systems.collision_system import CollisionSystem
from systems.damage_system import DamageSystem
from systems.enemy_ai_system import EnemyAISystem
from systems.fire_system import FireSystem
from systems.input_system import InputSystem
from systems.movement_system import MovementSystem
from systems.render_system import RenderSystem


class Game(GameFlowMixin, GameViewMixin):
    """Runs the game loop and manages the main game states."""

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
        self.end_options = ["Save Score", "Restart", "Controls", "Quit"]
        self.pause_selected = 0
        self.gameover_selected = 0
        self.victory_selected = 0
        self.controls_return_state = "title"

        self.player_eid  = None
        self.enemy_eids  = []
        self.backgrounds = self._load_backgrounds()
        self.star_layers = self._create_star_layers()
        self.high_scores = load_scores()


        self.life_icon_img = None
        self._update_life_icon()
        self._handle_state_audio(force=True)



    def _register_systems(self) -> None:
        self.world.add_system(InputSystem())
        self.world.add_system(FireSystem())
        self.world.add_system(EnemyAISystem())
        self.world.add_system(MovementSystem())
        self.world.add_system(CollisionSystem())
        self.world.add_system(DamageSystem())
        self.world.add_system(RenderSystem())
    def run(self) -> None:
        running = True

        while running:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.runtime.state in ("gameover", "victory"):
                        if not self.runtime.score_saved:
                            if event.key == pygame.K_BACKSPACE:
                                self.runtime.score_name_input = self.runtime.score_name_input[:-1] or ""
                                continue
                            if event.unicode and event.unicode.isalnum():
                                if len(self.runtime.score_name_input) < 8:
                                    self.runtime.score_name_input += event.unicode.upper()
                                continue

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
            self._update_star_layers()

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
                    self._prepare_score_entry()
                    self._enter_state("victory", 32)

            if fDict_kwargs.get("trigger_gameover"):
                self._prepare_score_entry()
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

    def shutdown(self) -> None:
        self.audio.shutdown()
