from __future__ import annotations

import pygame
from components.entry import EntryComponent
from config import PLAYER_WIDTH, BULLET_W, COLOR_ENEMY, COLOR_LEADER
from ecs_core.system import System
from components.position import PositionComponent
from components.input import InputComponent
from components.sprite import SpriteComponent
from components.tag import TagComponent
from entities.bullet import create_bullet


class FireSystem(System):
    """
    Spawns player bullets, enemy bullets, guard volleys, and leader shots.
    """

    def _player_bullet_image(self, level_index: int) -> str:
        return f"assets/sprites/player_fire_level{level_index + 1}.png"

    def _enemy_bullet_image(self, level_index: int) -> str:
        return f"assets/sprites/enemy_fire_level{level_index + 1}.png"

    def _leader_bullet_image(self, level_index: int) -> str:
        return f"assets/sprites/line_fire_level{level_index + 1}.png"

    def _get_player_center(self, world):
        player_entities = world.get_entities_with(InputComponent, PositionComponent)
        for eid in player_entities:
            pos = world.get_component(eid, PositionComponent)
            return (pos.x + PLAYER_WIDTH // 2, pos.y + 16)
        return None

    def _spawn_targeted_bullet(
        self,
        world,
        bullet_x,
        bullet_y,
        speed,
        color,
        player_center,
        image_path: str | None = None,
        vx_offset: float = 0.0,
    ) -> None:
        bullet_vx = vx_offset
        bullet_vy = speed

        if player_center is not None:
            dx = player_center[0] - bullet_x
            dy = max(40, player_center[1] - bullet_y)
            length = max((dx * dx + dy * dy) ** 0.5, 0.01)
            bullet_vx = dx / length * speed + vx_offset
            bullet_vy = dy / length * speed

        create_bullet(
            world,
            bullet_x,
            bullet_y,
            vx=bullet_vx,
            vy=bullet_vy,
            label="enemy_bullet",
            color=color,
            image_path=image_path,
        )

    def _fire_player_bullet(self, world, events, frame_count, rapid_fire_timer, level_index) -> None:
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
            create_bullet(
                world,
                bullet_x,
                bullet_y,
                image_path=self._player_bullet_image(level_index),
            )
            return True

        return False

    def _fire_enemy_bullets(self, world, wave_config, frame_count, level_index) -> None:
        if wave_config.fire_delay <= 0 or frame_count == 0:
            return

        if frame_count % wave_config.fire_delay != 0:
            return

        player_center = self._get_player_center(world)

        enemy_entities = world.get_entities_with(TagComponent, PositionComponent, SpriteComponent)
        shooters = []
        for eid in enemy_entities:
            tag = world.get_component(eid, TagComponent)
            if tag.label == "enemy":
                entry = world.get_component(eid, EntryComponent)
                if entry is not None and entry.active:
                    continue
                shooters.append(eid)

        if not shooters:
            return False

        if player_center is not None:
            def shooter_score(eid):
                pos = world.get_component(eid, PositionComponent)
                sprite = world.get_component(eid, SpriteComponent)
                center_x = pos.x + sprite.width / 2
                return (abs(center_x - player_center[0]), -pos.y)

            shooters.sort(key=shooter_score)
        else:
            shooters.sort(key=lambda eid: world.get_component(eid, PositionComponent).x)

        shot_count = min(wave_config.shooter_count, len(shooters))
        shooter_ids = shooters[:shot_count]

        for eid in shooter_ids:
            pos = world.get_component(eid, PositionComponent)
            sprite = world.get_component(eid, SpriteComponent)
            bullet_x = pos.x + sprite.width // 2 - BULLET_W // 2
            bullet_y = pos.y + sprite.height

            bullet_vx = 0.0
            bullet_vy = wave_config.bullet_speed
            pattern = wave_config.move_pattern

            if player_center is not None and pattern in ("swarm", "shooter", "tank"):
                dx = player_center[0] - (pos.x + sprite.width / 2)
                dy = max(40, player_center[1] - (pos.y + sprite.height))

                if pattern in ("shooter", "tank"):
                    length = max((dx * dx + dy * dy) ** 0.5, 0.01)
                    bullet_vx = dx / length * wave_config.bullet_speed
                    bullet_vy = dy / length * wave_config.bullet_speed
                    if pattern == "tank":
                        bullet_vx *= 0.75
                        bullet_vy *= 0.92
                else:
                    bullet_vx = max(-1.0, min(1.0, dx / 120.0)) * 0.9

            create_bullet(
                world,
                bullet_x,
                bullet_y,
                vx=bullet_vx,
                vy=bullet_vy,
                label="enemy_bullet",
                color=COLOR_ENEMY,
                image_path=self._enemy_bullet_image(level_index),
            )
        return True

    def _fire_guard_bullets(self, world, frame_count, level_index, player_center) -> None:
        if frame_count == 0 or frame_count % 78 != 0:
            return False

        guard_entities = world.get_entities_with(TagComponent, PositionComponent, SpriteComponent)
        guards = []
        for eid in guard_entities:
            tag = world.get_component(eid, TagComponent)
            if tag.label == "leader_guard":
                guards.append(eid)

        if not guards:
            return False

        guards.sort(key=lambda eid: world.get_component(eid, PositionComponent).x)
        if len(guards) == 1:
            shooter_ids = [guards[0]]
        elif len(guards) == 2:
            shooter_ids = [guards[0], guards[1]]
        else:
            shooter_pairs = [
                (0, len(guards) - 1),
                (1, len(guards) - 2),
            ]
            pair_index = (frame_count // 70) % len(shooter_pairs)
            left_index, right_index = shooter_pairs[pair_index]
            shooter_ids = [guards[left_index], guards[right_index]]

        if level_index <= 0:
            bullet_pattern = [(-0.5, 4.3), (0.0, 4.3), (0.5, 4.3)]
        elif level_index == 1:
            bullet_pattern = [(-0.8, 4.5), (0.0, 4.5), (0.8, 4.5)]
        else:
            bullet_pattern = [(-1.0, 4.7), (0.0, 4.7), (1.0, 4.7)]

        for eid in shooter_ids:
            pos = world.get_component(eid, PositionComponent)
            sprite = world.get_component(eid, SpriteComponent)
            bullet_x = pos.x + sprite.width // 2 - BULLET_W // 2
            bullet_y = pos.y + sprite.height

            for vx, vy in bullet_pattern:
                self._spawn_targeted_bullet(
                    world,
                    bullet_x,
                    bullet_y,
                    vy,
                    COLOR_LEADER,
                    player_center,
                    image_path=self._leader_bullet_image(level_index),
                    vx_offset=vx,
                )
        return True

    def _fire_leader_bullets(self, world, leader_config, frame_count, player_center, level_index) -> None:
        if leader_config.fire_delay <= 0 or frame_count == 0:
            return

        tagged_entities = world.get_entities_with(TagComponent)
        for eid in tagged_entities:
            tag = world.get_component(eid, TagComponent)
            if tag.label == "leader_guard":
                return False

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
                    self._spawn_targeted_bullet(
                        world,
                        bullet_x,
                        bullet_y,
                        leader_config.bullet_speed,
                        COLOR_LEADER,
                        player_center,
                        image_path=self._leader_bullet_image(level_index),
                        vx_offset=vx,
                    )
            else:
                self._spawn_targeted_bullet(
                    world,
                    bullet_x,
                    bullet_y,
                    leader_config.bullet_speed,
                    COLOR_LEADER,
                    player_center,
                    image_path=self._leader_bullet_image(level_index),
                )
            return True

        return False

    def update(self, world, kwargs) -> None:
        """
        Handles all shooting for the current frame.
        """
        if kwargs.get("game_state") != "play":
            return

        events = kwargs.get("events", [])
        frame_count = kwargs.get("frame_count", 0)
        level_index = kwargs.get("level_index", 0)
        wave_config = kwargs.get("wave_config")
        leader_config = kwargs.get("leader_config")
        rapid_fire_timer = kwargs.get("rapid_fire_timer", 0)
        player_center = self._get_player_center(world)
        kwargs["sound_events"] = kwargs.get("sound_events", [])

        if self._fire_player_bullet(world, events, frame_count, rapid_fire_timer, level_index):
            kwargs["sound_events"].append("fire")

        if wave_config is not None:
            if self._fire_enemy_bullets(world, wave_config, frame_count, level_index):
                kwargs["sound_events"].append("enemy_fire")

        if self._fire_guard_bullets(world, frame_count, level_index, player_center):
            kwargs["sound_events"].append("leader_fire")

        if leader_config is not None:
            if self._fire_leader_bullets(world, leader_config, frame_count, player_center, level_index):
                kwargs["sound_events"].append("leader_fire")
