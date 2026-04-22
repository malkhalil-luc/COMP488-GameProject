import random

from components.entry import EntryComponent
from components.formation import FormationComponent
from config import (
    SCREEN_WIDTH,
    FIELD_TOP,
    ENEMY_WIDTH,
    ENEMY_HEIGHT,
    COLOR_ENEMY,
)
from game_data import WaveConfig, DEFAULT_WAVE
from ecs_core.entity import Entity
from ecs_core.ecs import World
from components.position import PositionComponent
from components.velocity import VelocityComponent
from components.tag import TagComponent
from components.sprite import SpriteComponent
from components.health import HealthComponent
from components.collider import ColliderComponent


def _enemy_sprite_path(level_index: int) -> str:
    return f"assets/sprites/enemy_level{level_index + 1}.png"


def _guard_sprite_path(level_index: int) -> str:
    return f"assets/sprites/leader_line_level{level_index + 1}.png"


def _add_row_positions(
    positions: list[tuple[float, float]],
    count: int,
    y: float,
    gap_x: int,
    extra_offset_x: int = 0,
) -> None:
    if count <= 0:
        return

    row_w = count * ENEMY_WIDTH + (count - 1) * gap_x
    start_x = (SCREEN_WIDTH - row_w) // 2 + extra_offset_x

    for col in range(count):
        x = start_x + col * (ENEMY_WIDTH + gap_x)
        positions.append((float(x), float(y)))


def _build_wave_positions(wave_config: WaveConfig) -> list[tuple[float, float]]:
    positions: list[tuple[float, float]] = []
    start_y = FIELD_TOP + 20

    if wave_config.formation == "wide_line":
        for row in range(wave_config.rows):
            y = start_y + row * (ENEMY_HEIGHT + wave_config.gap_y)
            _add_row_positions(positions, wave_config.cols, y, wave_config.gap_x)
        return _apply_holes(positions, wave_config)

    if wave_config.formation == "staggered_rows":
        step_x = ENEMY_WIDTH + wave_config.gap_x
        for row in range(wave_config.rows):
            y = start_y + row * (ENEMY_HEIGHT + wave_config.gap_y)
            offset_x = step_x // 2 if row % 2 == 1 else 0
            _add_row_positions(positions, wave_config.cols, y, wave_config.gap_x, offset_x)
        return _apply_holes(positions, wave_config)

    if wave_config.formation == "split_groups":
        left_count = wave_config.cols // 2
        right_count = wave_config.cols - left_count
        big_gap = wave_config.gap_x + 70

        for row in range(wave_config.rows):
            y = start_y + row * (ENEMY_HEIGHT + wave_config.gap_y)

            left_w = left_count * ENEMY_WIDTH + max(0, left_count - 1) * wave_config.gap_x
            right_w = right_count * ENEMY_WIDTH + max(0, right_count - 1) * wave_config.gap_x
            total_w = left_w + big_gap + right_w
            start_x = (SCREEN_WIDTH - total_w) // 2

            for col in range(left_count):
                x = start_x + col * (ENEMY_WIDTH + wave_config.gap_x)
                positions.append((float(x), float(y)))

            right_start_x = start_x + left_w + big_gap
            for col in range(right_count):
                x = right_start_x + col * (ENEMY_WIDTH + wave_config.gap_x)
                positions.append((float(x), float(y)))
        return _apply_holes(positions, wave_config)

    if wave_config.formation == "v_shape":
        for row in range(wave_config.rows):
            y = start_y + row * (ENEMY_HEIGHT + wave_config.gap_y)
            row_count = max(2, wave_config.cols - 2 * (wave_config.rows - row - 1))
            row_count = min(row_count, wave_config.cols)
            _add_row_positions(positions, row_count, y, wave_config.gap_x)
        return _apply_holes(positions, wave_config)

    for row in range(wave_config.rows):
        y = start_y + row * (ENEMY_HEIGHT + wave_config.gap_y)
        _add_row_positions(positions, wave_config.cols, y, wave_config.gap_x)

    return _apply_holes(positions, wave_config)


def _apply_holes(
    positions: list[tuple[float, float]],
    wave_config: WaveConfig,
) -> list[tuple[float, float]]:
    if wave_config.hole_count <= 0:
        return positions

    rows: dict[float, list[tuple[float, float]]] = {}
    for x, y in positions:
        rows.setdefault(y, []).append((x, y))

    row_keys = list(rows.keys())
    removed = 0
    attempts = 0

    while removed < wave_config.hole_count and attempts < wave_config.hole_count * 8:
        attempts += 1
        row_y = random.choice(row_keys)
        row_positions = rows[row_y]

        if len(row_positions) <= 2:
            continue

        remove_index = random.randrange(len(row_positions))
        row_positions.pop(remove_index)
        removed += 1

    result: list[tuple[float, float]] = []
    for row_y in sorted(rows.keys()):
        row_positions = sorted(rows[row_y], key=lambda item: item[0])
        result.extend(row_positions)

    return result


def create_enemy_formation(
    world: World,
    wave_config: WaveConfig = DEFAULT_WAVE,
    level_index: int = 0,
) -> list[Entity]:
    """
    Creates one full enemy wave from the wave config.
    """
    enemy_ids = []

    for index, (x, y) in enumerate(_build_wave_positions(wave_config)):
        target_x = x + random.uniform(-8, 8)
        target_y = y + random.uniform(-4, 4)
        spawn_x, spawn_y = _pick_entry_spawn(target_x, target_y)
        eid = world.create_entity()

        world.add_component(eid, PositionComponent(x=spawn_x, y=spawn_y))
        world.add_component(eid, VelocityComponent(vx=0.0, vy=0.0))
        world.add_component(eid, FormationComponent(
            base_x=target_x,
            base_y=target_y,
            col_index=index,
        ))
        world.add_component(eid, EntryComponent(
            active=True,
            speed=random.uniform(1.3, 4.8),
            delay=random.randint(0, 30),
        ))
        world.add_component(eid, TagComponent(label="enemy"))
        world.add_component(eid, SpriteComponent(
            width=ENEMY_WIDTH,
            height=ENEMY_HEIGHT,
            color=COLOR_ENEMY,
            image_path=_enemy_sprite_path(level_index),
        ))
        world.add_component(eid, HealthComponent(
            hp=wave_config.enemy_hp,
            max_hp=wave_config.enemy_hp,
        ))
        world.add_component(eid, ColliderComponent(
            width=ENEMY_WIDTH,
            height=ENEMY_HEIGHT,
        ))

        enemy_ids.append(eid)

    return enemy_ids


def _pick_entry_spawn(target_x: float, target_y: float) -> tuple[float, float]:
    side = random.choice(["top", "left", "right"])
    playfield_top = FIELD_TOP + 2

    if side == "left":
        return (
            float(-ENEMY_WIDTH - random.randint(90, 240)),
            float(playfield_top + random.randint(72, 230)),
        )

    if side == "right":
        return (
            float(SCREEN_WIDTH + random.randint(90, 240)),
            float(playfield_top + random.randint(72, 230)),
        )

    return (
        float(target_x + random.randint(-220, 220)),
        float(FIELD_TOP - ENEMY_HEIGHT - random.randint(24, 140)),
    )


def create_leader_guard_line(world: World, level_index: int = 0, count: int = 5) -> list[Entity]:
    guard_ids = []
    gap_x = 18
    start_y = FIELD_TOP + 96
    row_w = count * ENEMY_WIDTH + (count - 1) * gap_x
    start_x = (SCREEN_WIDTH - row_w) // 2

    for col in range(count):
        x = start_x + col * (ENEMY_WIDTH + gap_x)
        eid = world.create_entity()

        world.add_component(eid, PositionComponent(x=float(x), y=float(start_y)))
        world.add_component(eid, VelocityComponent(vx=0.0, vy=0.0))
        world.add_component(eid, FormationComponent(
            base_x=float(x),
            base_y=float(start_y),
            col_index=col,
        ))
        world.add_component(eid, TagComponent(label="leader_guard"))
        world.add_component(eid, SpriteComponent(
            width=ENEMY_WIDTH,
            height=ENEMY_HEIGHT,
            color=(255, 210, 120),
            image_path=_guard_sprite_path(level_index),
        ))
        world.add_component(eid, HealthComponent(
            hp=2,
            max_hp=2,
        ))
        world.add_component(eid, ColliderComponent(
            width=ENEMY_WIDTH,
            height=ENEMY_HEIGHT,
        ))

        guard_ids.append(eid)

    return guard_ids
