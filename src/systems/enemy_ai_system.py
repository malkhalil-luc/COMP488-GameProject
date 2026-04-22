import random
import math

import pygame

from components.entry import EntryComponent
from components.formation import FormationComponent
from components.health import HealthComponent
from components.leader_move import LeaderMoveComponent
from ecs_core.system import System
from components.velocity import VelocityComponent
from components.tag import TagComponent
from components.position import PositionComponent
from config import SCREEN_WIDTH, FIELD_TOP, FIELD_BOTTOM, ENEMY_WIDTH, ENEMY_HEIGHT
from game_data import DEFAULT_WAVE, DEFAULT_LEADER


class EnemyAISystem(System):
    """
    Updates enemy and leader movement for the current frame.
    """

    def _get_player_center(self, world):
        player_entities = world.get_entities_with(TagComponent, PositionComponent)
        for eid in player_entities:
            tag = world.get_component(eid, TagComponent)
            if tag.label == "player":
                pos = world.get_component(eid, PositionComponent)
                return pygame.Vector2(pos.x + 16, pos.y + 16)
        return None

    def _apply_enemy_bounds(self, pos, steer) -> None:
        if pos.x < 18:
            steer.x += 1.0
        elif pos.x + ENEMY_WIDTH > SCREEN_WIDTH - 18:
            steer.x -= 1.0

        if pos.y < FIELD_TOP + 18:
            steer.y += 0.6
        elif pos.y + ENEMY_HEIGHT > FIELD_BOTTOM - 110:
            steer.y -= 2.4

    def _separation_force(self, eid: int, current, enemies: list[dict], radius: float) -> pygame.Vector2:
        steer = pygame.Vector2(0.0, 0.0)

        for other in enemies:
            if other["eid"] == eid:
                continue

            diff = current - other["pos"]
            distance = diff.length()
            if 0 < distance < radius:
                steer += diff.normalize() * (1.0 - distance / radius)

        if steer.length() > 0:
            return steer.normalize()
        return steer

    def _apply_velocity(self, vel, steer, speed: float, turn_rate: float) -> None:
        if steer.length() == 0:
            return

        desired = steer.normalize() * speed
        vel.vx += (desired.x - vel.vx) * turn_rate
        vel.vy += (desired.y - vel.vy) * turn_rate

    def _update_entry_enemy(self, pos, vel, formation, entry) -> bool:
        if entry.delay > 0:
            entry.delay -= 1
            vel.vx = 0.0
            vel.vy = 0.0
            return False

        target = pygame.Vector2(formation.base_x, formation.base_y)
        current = pygame.Vector2(pos.x, pos.y)
        to_target = target - current

        if to_target.length() < 10:
            pos.x = formation.base_x
            pos.y = formation.base_y
            vel.vx = 0.0
            vel.vy = 0.0
            entry.active = False
            return True

        sway = pygame.Vector2(
            math.sin(pos.y / 23.0 + formation.col_index * 0.9),
            math.cos(pos.x / 29.0 + formation.col_index * 0.6),
        ) * 0.22
        steer = to_target + sway
        self._apply_velocity(vel, steer, entry.speed, 0.12)
        return False

    def _update_drifter_enemy(self, eid, pos, vel, enemies, player_center, wave_config, frame_count) -> None:
        current = pygame.Vector2(pos.x + ENEMY_WIDTH / 2, pos.y + ENEMY_HEIGHT / 2)
        steer = pygame.Vector2(0.0, 0.50)

        if player_center is not None:
            to_player = player_center - current
            if to_player.length() > 0:
                weight = 0.90 if to_player.length() < 220 else 0.40
                steer += to_player.normalize() * weight

        wander = pygame.Vector2(
            math.sin(frame_count / 14.0 + eid * 0.41),
            math.cos(frame_count / 17.0 + eid * 0.29),
        )
        if wander.length() > 0:
            steer += wander.normalize() * 0.55

        separation = self._separation_force(eid, current, enemies, 58.0)
        if separation.length() > 0:
            steer += separation * 1.10

        self._apply_enemy_bounds(pos, steer)
        self._apply_velocity(vel, steer, wave_config.speed, 0.12)

    def _update_swarm_enemy(self, eid, pos, vel, enemies, player_center, wave_config, frame_count) -> None:
        current = pygame.Vector2(pos.x + ENEMY_WIDTH / 2, pos.y + ENEMY_HEIGHT / 2)
        separation = pygame.Vector2(0.0, 0.0)
        alignment = pygame.Vector2(0.0, 0.0)
        cohesion = pygame.Vector2(0.0, 0.0)
        sep_count = 0
        ali_count = 0
        coh_count = 0

        for other in enemies:
            if other["eid"] == eid:
                continue

            diff = current - other["pos"]
            distance = diff.length()

            if 0 < distance < 64:
                separation += diff.normalize() / max(distance, 1.0)
                sep_count += 1
            if distance < 120:
                alignment += other["vel"]
                ali_count += 1
            if distance < 160:
                cohesion += other["pos"]
                coh_count += 1

        steer = pygame.Vector2(0.0, 0.42)

        if sep_count > 0 and separation.length() > 0:
            steer += separation.normalize() * 1.30
        if ali_count > 0:
            alignment /= ali_count
            if alignment.length() > 0:
                steer += alignment.normalize() * 0.70
        if coh_count > 0:
            group_center = cohesion / coh_count
            to_group = group_center - current
            if to_group.length() > 0:
                steer += to_group.normalize() * 0.45

        if player_center is not None:
            to_player = player_center - current
            if to_player.length() > 0:
                steer += to_player.normalize() * 0.70

        wobble = pygame.Vector2(
            math.sin(frame_count / 16.0 + eid * 0.53),
            math.cos(frame_count / 19.0 + eid * 0.31),
        )
        if wobble.length() > 0:
            steer += wobble.normalize() * 0.18

        self._apply_enemy_bounds(pos, steer)
        self._apply_velocity(vel, steer, wave_config.speed, 0.10)

    def _update_shooter_enemy(self, eid, pos, vel, enemies, player_center, wave_config) -> None:
        current = pygame.Vector2(pos.x + ENEMY_WIDTH / 2, pos.y + ENEMY_HEIGHT / 2)
        steer = pygame.Vector2(0.0, 0.0)

        if player_center is not None:
            to_player = player_center - current
            distance = to_player.length()

            if distance > 0:
                player_dir = to_player.normalize()
                if distance < 130:
                    steer += -player_dir * 1.15
                elif distance > 230:
                    steer += player_dir * 0.80
                else:
                    side = pygame.Vector2(-player_dir.y, player_dir.x)
                    if eid % 2 == 0:
                        side *= -1
                    steer += side * 1.00

        separation = self._separation_force(eid, current, enemies, 52.0)
        if separation.length() > 0:
            steer += separation * 0.7

        self._apply_enemy_bounds(pos, steer)
        self._apply_velocity(vel, steer, wave_config.speed, 0.11)

    def _update_tank_enemy(self, eid, pos, vel, enemies, player_center, wave_config, health) -> None:
        current = pygame.Vector2(pos.x + ENEMY_WIDTH / 2, pos.y + ENEMY_HEIGHT / 2)
        steer = pygame.Vector2(0.0, 0.38)

        if player_center is not None:
            to_player = player_center - current
            if to_player.length() > 0:
                steer += to_player.normalize() * 1.35

        separation = self._separation_force(eid, current, enemies, 48.0)
        if separation.length() > 0:
            steer += separation * 0.55

        self._apply_enemy_bounds(pos, steer)

        speed = wave_config.speed
        if health is not None and health.max_hp > 0:
            hp_ratio = health.hp / health.max_hp
            if hp_ratio < 0.4:
                speed += 0.40

        self._apply_velocity(vel, steer, speed, 0.11)

    def _update_enemy_velocity(
        self,
        eid: int,
        pos,
        vel,
        enemies: list[dict],
        player_center,
        wave_config,
        frame_count: int,
        health,
    ) -> None:
        pattern = wave_config.move_pattern

        if pattern == "swarm":
            self._update_swarm_enemy(eid, pos, vel, enemies, player_center, wave_config, frame_count)
        elif pattern == "shooter":
            self._update_shooter_enemy(eid, pos, vel, enemies, player_center, wave_config)
        elif pattern == "tank":
            self._update_tank_enemy(eid, pos, vel, enemies, player_center, wave_config, health)
        else:
            self._update_drifter_enemy(eid, pos, vel, enemies, player_center, wave_config, frame_count)

    def _update_guard_velocity(
        self,
        eid: int,
        pos,
        vel,
        formation,
        guards: list[dict],
        leader_center,
        player_center,
        frame_count: int,
    ) -> None:
        guard_center = pygame.Vector2(pos.x + ENEMY_WIDTH / 2, pos.y + ENEMY_HEIGHT / 2)
        middle_index = (len(guards) - 1) / 2 if guards else 0
        slot_offset = (formation.col_index - middle_index) * (ENEMY_WIDTH + 14)
        sway_x = math.sin(frame_count / 18.0 + formation.col_index * 0.7) * 22
        sway_y = math.sin(frame_count / 20.0 + formation.col_index * 0.5) * 18
        drop_y = 0.0
        if player_center is not None:
            drop_y = min(60.0, max(0.0, (player_center.y - leader_center.y) * 0.18))
        target = pygame.Vector2(
            leader_center.x + slot_offset + sway_x,
            leader_center.y + 54 + sway_y + drop_y,
        )
        steer = pygame.Vector2(0.0, 0.0)

        to_slot = target - guard_center
        if to_slot.length() > 0:
            steer += to_slot.normalize() * 0.95

        separation = pygame.Vector2(0.0, 0.0)
        for other in guards:
            if other["eid"] == eid:
                continue

            diff = guard_center - other["pos"]
            distance = diff.length()
            if 0 < distance < 56:
                separation += diff.normalize() * (1.0 - distance / 56.0)

        if separation.length() > 0:
            steer += separation.normalize() * 1.20

        if player_center is not None:
            block = pygame.Vector2(
                player_center.x - guard_center.x,
                player_center.y - guard_center.y,
            )
            if block.length() > 0:
                steer += block.normalize() * 0.38

        if steer.length() == 0:
            steer = pygame.Vector2(0.0, 1.0)
        else:
            steer = steer.normalize()

        target_vx = steer.x * 2.10
        target_vy = steer.y * 1.10
        vel.vx += (target_vx - vel.vx) * 0.18
        vel.vy += (target_vy - vel.vy) * 0.22

    def _pick_leader_target(self, move, player_center, leader_config) -> None:
        left = 18.0
        right = float(SCREEN_WIDTH - leader_config.width - 18)
        top = float(FIELD_TOP + 16)
        mid = float(FIELD_TOP + 92)
        deep = float(FIELD_TOP + 150)

        if leader_config.move_pattern == "hunter":
            if player_center is not None and random.random() < 0.7:
                target_x = player_center.x - leader_config.width / 2 + random.uniform(-70, 70)
            else:
                target_x = random.uniform(left, right)

            if random.random() < 0.45:
                target_y = random.uniform(mid - 10, deep)
            else:
                target_y = random.uniform(top, mid)

            move.timer = random.randint(28, 54)

        elif leader_config.move_pattern == "weave":
            target_x = random.uniform(left, right)
            target_y = random.uniform(top, mid + 20)
            move.timer = random.randint(34, 62)

        else:
            target_x = random.uniform(left, right)
            target_y = random.uniform(top, mid)
            move.timer = random.randint(42, 76)

        move.target_x = max(left, min(right, target_x))
        move.target_y = max(top, min(deep, target_y))

    def _update_leader_velocity(self, pos, vel, player_center, leader_config, move) -> None:
        if move.timer > 0:
            move.timer -= 1

        target = pygame.Vector2(move.target_x, move.target_y)
        current = pygame.Vector2(pos.x, pos.y)
        to_target = target - current

        if move.timer <= 0 or to_target.length() < 18:
            self._pick_leader_target(move, player_center, leader_config)
            target = pygame.Vector2(move.target_x, move.target_y)
            to_target = target - current

        target_vx = max(-leader_config.speed_x, min(leader_config.speed_x, to_target.x * 0.08))
        target_vy = max(-leader_config.speed_y, min(leader_config.speed_y, to_target.y * 0.08))
        vel.vx += (target_vx - vel.vx) * 0.14
        vel.vy += (target_vy - vel.vy) * 0.14

    def update(self, world, kwargs) -> None:
        """
        Moves regular enemies, guard enemies, and the leader.
        """
        if kwargs.get("game_state") != "play":
            return

        wave_config = kwargs.get("wave_config", DEFAULT_WAVE)
        leader_config = kwargs.get("leader_config", DEFAULT_LEADER)
        frame_count = kwargs.get("frame_count", 0)
        enemy_count = 0
        guard_alive = False
        player_center = self._get_player_center(world)

        tagged_entities = world.get_entities_with(TagComponent, VelocityComponent)
        enemies: list[dict] = []
        guards: list[dict] = []
        leader_data = None

        for eid in tagged_entities:
            tag = world.get_component(eid, TagComponent)
            pos = world.get_component(eid, PositionComponent)
            vel = world.get_component(eid, VelocityComponent)

            if pos is None or vel is None:
                continue

            if tag.label == "enemy":
                enemies.append({
                    "eid": eid,
                    "pos": pygame.Vector2(pos.x + ENEMY_WIDTH / 2, pos.y + ENEMY_HEIGHT / 2),
                    "vel": pygame.Vector2(vel.vx, vel.vy),
                })
            elif tag.label == "leader_guard":
                guards.append({
                    "eid": eid,
                    "pos": pygame.Vector2(pos.x + ENEMY_WIDTH / 2, pos.y + ENEMY_HEIGHT / 2),
                })
                guard_alive = True
            elif tag.label == "leader":
                leader_data = {
                    "eid": eid,
                    "pos": pos,
                    "vel": vel,
                    "move": world.get_component(eid, LeaderMoveComponent),
                }

        leader_center = None
        if leader_data is not None:
            leader_center = pygame.Vector2(
                leader_data["pos"].x + leader_config.width / 2,
                leader_data["pos"].y + leader_config.height / 2,
            )

        for eid in tagged_entities:
            tag = world.get_component(eid, TagComponent)
            pos = world.get_component(eid, PositionComponent)
            vel = world.get_component(eid, VelocityComponent)

            if tag.label == "enemy":
                formation = world.get_component(eid, FormationComponent)
                entry = world.get_component(eid, EntryComponent)
                if formation is not None and entry is not None and entry.active:
                    self._update_entry_enemy(pos, vel, formation, entry)
                    enemy_count += 1
                    continue

                health = world.get_component(eid, HealthComponent)
                self._update_enemy_velocity(
                    eid,
                    pos,
                    vel,
                    enemies,
                    player_center,
                    wave_config,
                    frame_count,
                    health,
                )
                enemy_count += 1

            elif tag.label == "leader_guard":
                formation = world.get_component(eid, FormationComponent)
                if formation is not None and leader_center is not None:
                    self._update_guard_velocity(
                        eid,
                        pos,
                        vel,
                        formation,
                        guards,
                        leader_center,
                        player_center,
                        frame_count,
                    )

                enemy_count += 1

            elif tag.label == "leader":
                if guard_alive:
                    vel.vx = 0.0
                    vel.vy = 0.0
                    continue

                move = world.get_component(eid, LeaderMoveComponent)
                if move is not None:
                    self._update_leader_velocity(pos, vel, player_center, leader_config, move)
                    
        leader_alive = kwargs.get("leader_alive", False)

        if enemy_count == 0 and not leader_alive:
            kwargs["wave_cleared"] = True
