#state machine + orchestration
import pygame
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
from entities.enemy import create_enemy_formation
from entities.leader import create_leader
from components.sprite import SpriteComponent
from components.input import InputComponent
from components.tag import TagComponent


class Game:
    """
    Owns the state machine, game variables, world, and frame loop.

    Call game.run() from main.py to start.
    """

    def __init__(self) -> None:
        #  pygame setup 
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        #  fonts 
        self.font       = pygame.font.SysFont(None, FONT_SIZE)
        self.font_title = pygame.font.SysFont(None, FONT_TITLE_SIZE)
        self.font_sub   = pygame.font.SysFont(None, FONT_SUB_SIZE)
        self.audio = AudioBank()

        #  ECS world 
        self.world = World()
        self._register_systems()

        #  runtime game state 
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

        # Entity IDs — stored so game.py can reference them if needed
        self.player_eid  = None
        self.enemy_eids  = []


        self.heart_img = pygame.image.load("assets/sprites/heart.png").convert_alpha()
        self.heart_img = pygame.transform.scale(self.heart_img, (20, 20))
        self._handle_state_audio(force=True)



    def _register_systems(self) -> None:
        """
        Register all systems in execution order.
        Order is critical — see module docstring.
        """
        self.world.add_system(InputSystem())
        self.world.add_system(FireSystem())
        self.world.add_system(EnemyAISystem())
        self.world.add_system(MovementSystem())
        self.world.add_system(CollisionSystem())
        self.world.add_system(DamageSystem())
        self.world.add_system(RenderSystem())

    def _reset(self) -> None:
        """
        Reset all game variables and rebuild the world for a fresh run.

        Called when starting from title screen and on restart from
        gameover or victory screen.

        Steps:
            1. Reset score, lives, leader flag
            2. Clear the entire world (remove all entities)
            3. Spawn fresh player + enemy formation
        """
        self.runtime.reset_run_values()
        self.current_level_index = 0
        self.current_wave_index = 0
        self.frame_count = 0
        self.transition_timer = 0
        self.transition_text = ""
        self.current_wave_config = self.levels[0].waves[0]
        self.current_leader_config = self.levels[0].leader


        # clear existing entities from the world
        self.world.clear()

        # Spawn initial entities via factories
        self.player_eid = create_player(self.world)
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
        self.enemy_eids = create_enemy_formation(self.world, self.current_wave_config)
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
        create_leader(self.world, self.current_leader_config)
        self.runtime.leader_alive = True
        self.pending_spawn_sound = "leader_spawn"
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

    def _handle_state_audio(self, force: bool = False) -> None:
        if not force and self.runtime.state == self.last_audio_state:
            return

        self.last_audio_state = self.runtime.state

        if self.runtime.state in ("title", "paused"):
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
            self.audio.stop_loop()
            self.audio.play("victory")


    def run(self) -> None:
        """
        Main game loop. Called from main.py.
        Runs until the player closes the window.
        """
        running = True

        while running:
            #  Collect events 
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False

                #  State machine input (game state transitions)
                # InputSystem only handles entity velocity

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1:
                        self.show_debug = not self.show_debug

                    # Title screen → start game
                    if self.runtime.state == "title" and event.key == pygame.K_SPACE:
                        self.audio.play("ui_confirm")
                        self._reset()
                        events = []


                    # Play → pause / pause → play
                    elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                        if self.runtime.state == "play":
                            self.runtime.state = "paused"
                        elif self.runtime.state == "paused":
                            self.runtime.state = "play"


                    # Gameover or victory → restart
                    elif event.key == pygame.K_r:
                        if self.runtime.state in ("gameover", "victory"):
                            self.audio.play("ui_confirm")
                            self._reset()

                    elif event.key == pygame.K_m:
                        self.audio.toggle_mute()

                    elif event.key == pygame.K_q:
                        if self.runtime.state in ("title", "paused", "gameover", "victory"):
                            running = False


            self._update_transition()

            if self.runtime.state == "play":
                self.frame_count += 1

            #  Clear screen 
            self.screen.fill(COLOR_BG)

            # Build kwargs for this dict frame 
            # Systems read from and write back to this dict.
            fDict_kwargs = {
                "screen": self.screen,
                "events": events,
                "game_state": self.runtime.state,
                "score": self.runtime.score,
                "lives": self.runtime.lives,
                "leader_alive": self.runtime.leader_alive,
                "leader_hit_cooldown": self.runtime.leader_hit_cooldown,
                "wave_config": self.current_wave_config,
                "leader_config": self.current_leader_config,
                "frame_count": self.frame_count,
                "rapid_fire_timer": self.runtime.rapid_fire_timer,
                "shield_timer": self.runtime.shield_timer,
            }


            #  Update world (runs all systems in order) 
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

            ### flash the player sprite when hit
            if fDict_kwargs.get("lives", self.runtime.lives) < self.runtime.lives:
                self.runtime.player_flash_timer = 60  # 1 second of flashing

            if self.runtime.player_flash_timer > 0:
                self.runtime.player_flash_timer -= 1
                # toggle visible every 6 frames — creates a flash effect
                player_entities = self.world.get_entities_with(InputComponent, SpriteComponent)
                for eid in player_entities:
                    sprite = self.world.get_component(eid, SpriteComponent)
                    sprite.visible = (self.runtime.player_flash_timer % 6) < 3
            else:
                # make sure player is always visible when not flashing
                player_entities = self.world.get_entities_with(InputComponent, SpriteComponent)
                for eid in player_entities:
                    sprite = self.world.get_component(eid, SpriteComponent)
                    sprite.visible = True

                ###

            #  Read signals written by systems
            # Score and lives may have been updated by DamageSystem
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
                self.last_pickup_text = new_pickup_text

            for sound_name in fDict_kwargs.get("sound_events", []):
                self.audio.play(sound_name)

            # Wave cleared → spawn the leader
            if fDict_kwargs.get("wave_cleared") and not self.runtime.leader_alive:
                self._advance_after_wave_clear()

            if fDict_kwargs.get("trigger_victory"):
                self._advance_after_leader_defeat()

            if fDict_kwargs.get("trigger_gameover"):
                self.runtime.state = "gameover"

            self._handle_state_audio()


            #  Draw HUD on top of entities 
            # RenderSystem drew entities. Now game.py draws UI on top.
            if self.runtime.state in ("play", "paused"):
                self._draw_hud()

            #  Draw state overlays 
            if self.runtime.state == "title":
                self._draw_title_overlay()
            elif self.runtime.state == "transition":
                self._draw_transition_overlay()
            elif self.runtime.state == "paused":
                self._draw_pause_overlay()
            elif self.runtime.state == "gameover":
                self._draw_gameover_overlay()
            elif self.runtime.state == "victory":
                self._draw_victory_overlay()

            if self.show_debug:
                self._draw_debug_panel()

            pygame.display.flip()
            self.clock.tick(FPS)


    def _draw_hud(self) -> None:
        """
        Draw the HUD strip at the top of the screen.
        Score on the left, lives on the right.
        Boss HP bar at the bottom when leader is alive.
        """
       
        #  Score (top-left) 
        score_surf = self.font.render(f"Score: {self.runtime.score}", True, (240, 240, 240))
        self.screen.blit(score_surf, score_surf.get_rect(topleft=(12, 14)))

        level_label = f"L{self.current_level_index + 1}  W{self.current_wave_index + 1}"
        if self.runtime.leader_alive:
            level_label = f"L{self.current_level_index + 1}  LEADER"
        level_surf = self.font.render(level_label, True, (200, 200, 200))
        self.screen.blit(level_surf, level_surf.get_rect(center=(SCREEN_WIDTH // 2, 24)))

        #  Lives (top-right) — shown as heart count  
        for i in range(self.runtime.lives):
            hx = SCREEN_WIDTH - 20 - i * 26
            self.screen.blit(self.heart_img, (hx - 20 , 12))

        # HUD divider line 
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
            pickup_surf = self.font.render(self.runtime.pickup_text, True, (240, 240, 240))
            self.screen.blit(pickup_surf, pickup_surf.get_rect(center=(SCREEN_WIDTH // 2, HUD_H + 18)))

        #  Boss HP bar (bottom strip — only during leader phase) 
        if self.runtime.leader_alive:
            self._draw_boss_bar()


    def _draw_boss_bar(self) -> None:
        """
        Draw the Enemy Leader HP bar at the bottom of the screen.
        Reads HealthComponent from the leader entity directly.
        """
        from components.health import HealthComponent
        from components.tag import TagComponent

        # Find the leader entity to read current HP
        leader_entities = self.world.get_entities_with(TagComponent, HealthComponent)
        leader_hp  = 0
        leader_max = 1  # avoid divide-by-zero

        for eid in leader_entities:
            tag = self.world.get_component(eid, TagComponent)
            if tag.label == "leader":
                health = self.world.get_component(eid, HealthComponent)
                leader_hp  = health.hp
                leader_max = health.max_hp
                break

        # Bar dimensions — centered at the bottom strip
        bar_w   = 300
        bar_h   = 18
        bar_x   = SCREEN_WIDTH // 2 - bar_w // 2
        bar_y   = SCREEN_HEIGHT - BOSS_BAR_H + (BOSS_BAR_H - bar_h) // 2

        # Background track
        track_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        pygame.draw.rect(self.screen, (60, 20, 20), track_rect)

        # Fill — scales with hp / max_hp
        pct      = leader_hp / leader_max
        fill_w   = int(bar_w * pct)
        fill_rect = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
        pygame.draw.rect(self.screen, COLOR_LEADER, fill_rect)

        # Outline
        pygame.draw.rect(self.screen, (200, 200, 200), track_rect, 2)

        # Label
        label = self.font.render(f"LEADER  {leader_hp}/{leader_max}", True, (240, 240, 240))
        self.screen.blit(label, label.get_rect(
            centerx=SCREEN_WIDTH // 2,
            bottom=bar_y - 4,
        ))

    def _get_audio_status(self) -> str:
        if not self.audio.enabled:
            return "OFF"
        if self.audio.muted:
            return "MUTED"
        return "ON"

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
            "F1 Debug  M Mute  Q Quit",
        ]

        y = panel.top + 10
        for line in lines:
            text = self.font.render(line, True, (230, 230, 230))
            self.screen.blit(text, (panel.left + 10, y))
            y += 17


    def _draw_overlay_panel(self) -> pygame.Rect:
        """
        Draw a semi-transparent dark panel in the center of the screen.
        Returns the panel rect so callers can position text inside it.
        """
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 120, 440, 240)
        dark  = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        dark.fill((10, 10, 20, 210))
        self.screen.blit(dark, panel.topleft)
        pygame.draw.rect(self.screen, (100, 100, 140), panel, 2)
        return panel

    def _draw_title_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        title = self.font_title.render("INVASION SPACERS", True, (0, 200, 255))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        sub = self.font_sub.render("Press SPACE to Play", True, (200, 200, 200))
        self.screen.blit(sub, sub.get_rect(centerx=panel.centerx, top=panel.top + 100))

        hint = self.font.render("Move: Arrows / WASD    Fire: Space / Shift    Pause: P", True, (140, 140, 160))
        self.screen.blit(hint, hint.get_rect(centerx=panel.centerx, top=panel.top + 150))

        hint2 = self.font.render("M: Mute / Unmute    Q: Quit    F1: Debug", True, (140, 140, 160))
        self.screen.blit(hint2, hint2.get_rect(centerx=panel.centerx, top=panel.top + 178))

    def _draw_pause_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        paused = self.font_title.render("PAUSED", True, (240, 240, 100))
        self.screen.blit(paused, paused.get_rect(centerx=panel.centerx, top=panel.top + 50))

        resume = self.font_sub.render("Press P or ESC to Resume", True, (200, 200, 200))
        self.screen.blit(resume, resume.get_rect(centerx=panel.centerx, top=panel.top + 118))

        controls = self.font.render("M: Mute / Unmute    Q: Quit    F1: Debug", True, (180, 180, 180))
        self.screen.blit(controls, controls.get_rect(centerx=panel.centerx, top=panel.top + 160))

    def _draw_transition_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        title = self.font_title.render(self.transition_text, True, (240, 240, 240))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 55))

        ready = self.font_sub.render("Get Ready", True, (200, 200, 120))
        self.screen.blit(ready, ready.get_rect(centerx=panel.centerx, top=panel.top + 130))

    def _draw_gameover_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        title = self.font_title.render("GAME OVER", True, (220, 60, 60))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        score = self.font_sub.render(f"Final Score: {self.runtime.score}", True, (240, 240, 240))
        self.screen.blit(score, score.get_rect(centerx=panel.centerx, top=panel.top + 100))

        restart = self.font.render("Press R to Restart", True, (180, 180, 180))
        self.screen.blit(restart, restart.get_rect(centerx=panel.centerx, top=panel.top + 146))

        quit_text = self.font.render("Q: Quit    M: Mute / Unmute    F1: Debug", True, (180, 180, 180))
        self.screen.blit(quit_text, quit_text.get_rect(centerx=panel.centerx, top=panel.top + 178))

    def _draw_victory_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        title = self.font_title.render("VICTORY!", True, (100, 220, 100))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        score = self.font_sub.render(f"Final Score: {self.runtime.score}", True, (240, 240, 240))
        self.screen.blit(score, score.get_rect(centerx=panel.centerx, top=panel.top + 100))

        restart = self.font.render("Press R to Play Again", True, (180, 180, 180))
        self.screen.blit(restart, restart.get_rect(centerx=panel.centerx, top=panel.top + 146))

        quit_text = self.font.render("Q: Quit    M: Mute / Unmute    F1: Debug", True, (180, 180, 180))
        self.screen.blit(quit_text, quit_text.get_rect(centerx=panel.centerx, top=panel.top + 178))

    def shutdown(self) -> None:
        self.audio.shutdown()
