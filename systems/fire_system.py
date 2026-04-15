import pygame
from config import PLAYER_WIDTH, BULLET_W, COLOR_ENEMY, COLOR_LEADER
from ecs_core.system import System
from components.position import PositionComponent
from components.input import InputComponent
from components.sprite import SpriteComponent
from components.tag import TagComponent
from entities.bullet import create_bullet


class FireSystem(System):
    """
    Listens for KEYDOWN Space or Shift and spawns a bullet at the
    player's nose position.
    """

    def _fire_player_bullet(self, world, events, frame_count, rapid_fire_timer) -> None:
        keys = pygame.key.get_pressed()
        holding_fire = keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        if rapid_fire_timer > 0:
            if not holding_fire:
                return
            if frame_count % 6 != 0:
                return
        else:
            fire_pressed = False
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
                        fire_pressed = True
                        break

            if not fire_pressed:
                return

        player_entities = world.get_entities_with(InputComponent, PositionComponent)

        for eid in player_entities:
            pos = world.get_component(eid, PositionComponent)
            bullet_x = pos.x + PLAYER_WIDTH // 2 - BULLET_W // 2
            bullet_y = pos.y
            create_bullet(world, bullet_x, bullet_y)
            return True

        return False

    def _fire_enemy_bullets(self, world, wave_config, frame_count) -> None:
        if wave_config.fire_delay <= 0 or frame_count == 0:
            return

        if frame_count % wave_config.fire_delay != 0:
            return

        enemy_entities = world.get_entities_with(TagComponent, PositionComponent, SpriteComponent)
        shooters = []
        for eid in enemy_entities:
            tag = world.get_component(eid, TagComponent)
            if tag.label == "enemy":
                shooters.append(eid)

        if not shooters:
            return False

        shooters.sort(key=lambda eid: world.get_component(eid, PositionComponent).x)
        shot_count = min(wave_config.shooter_count, len(shooters))
        start_index = (frame_count // wave_config.fire_delay) % len(shooters)

        for offset in range(shot_count):
            eid = shooters[(start_index + offset) % len(shooters)]
            pos = world.get_component(eid, PositionComponent)
            sprite = world.get_component(eid, SpriteComponent)
            bullet_x = pos.x + sprite.width // 2 - BULLET_W // 2
            bullet_y = pos.y + sprite.height
            create_bullet(
                world,
                bullet_x,
                bullet_y,
                vy=wave_config.bullet_speed,
                label="enemy_bullet",
                color=COLOR_ENEMY,
            )
        return True

    def _fire_leader_bullets(self, world, leader_config, frame_count) -> None:
        if leader_config.fire_delay <= 0 or frame_count == 0:
            return

        if frame_count % leader_config.fire_delay != 0:
            return

        leader_entities = world.get_entities_with(TagComponent, PositionComponent)

        for eid in leader_entities:
            tag = world.get_component(eid, TagComponent)
            if tag.label != "leader":
                continue

            pos = world.get_component(eid, PositionComponent)
            bullet_x = pos.x + leader_config.width // 2 - BULLET_W // 2
            bullet_y = pos.y + leader_config.height

            if leader_config.shot_count >= 3:
                for vx in (-1.5, 0.0, 1.5):
                    create_bullet(
                        world,
                        bullet_x,
                        bullet_y,
                        vx=vx,
                        vy=leader_config.bullet_speed,
                        label="enemy_bullet",
                        color=COLOR_LEADER,
                    )
            else:
                create_bullet(
                    world,
                    bullet_x,
                    bullet_y,
                    vy=leader_config.bullet_speed,
                    label="enemy_bullet",
                    color=COLOR_LEADER,
                )
            return True

        return False

    def update(self, world, kwargs) -> None:
        """
        Scan this frame's events for a fire key press.
        If found, spawn one bullet at the player's nose.

        """
        if kwargs.get("game_state") != "play":
            return

        events = kwargs.get("events", [])
        frame_count = kwargs.get("frame_count", 0)
        wave_config = kwargs.get("wave_config")
        leader_config = kwargs.get("leader_config")
        rapid_fire_timer = kwargs.get("rapid_fire_timer", 0)
        kwargs["sound_events"] = kwargs.get("sound_events", [])

        if self._fire_player_bullet(world, events, frame_count, rapid_fire_timer):
            kwargs["sound_events"].append("fire")

        if wave_config is not None:
            if self._fire_enemy_bullets(world, wave_config, frame_count):
                kwargs["sound_events"].append("enemy_fire")

        if leader_config is not None:
            if self._fire_leader_bullets(world, leader_config, frame_count):
                kwargs["sound_events"].append("leader_fire")
