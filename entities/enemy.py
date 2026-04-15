# factory: build the enemy entities

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
from components.collider import ColliderComponent


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
        return positions

    if wave_config.formation == "staggered_rows":
        step_x = ENEMY_WIDTH + wave_config.gap_x
        for row in range(wave_config.rows):
            y = start_y + row * (ENEMY_HEIGHT + wave_config.gap_y)
            offset_x = step_x // 2 if row % 2 == 1 else 0
            _add_row_positions(positions, wave_config.cols, y, wave_config.gap_x, offset_x)
        return positions

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
        return positions

    if wave_config.formation == "v_shape":
        for row in range(wave_config.rows):
            y = start_y + row * (ENEMY_HEIGHT + wave_config.gap_y)
            row_count = max(2, wave_config.cols - 2 * (wave_config.rows - row - 1))
            row_count = min(row_count, wave_config.cols)
            _add_row_positions(positions, row_count, y, wave_config.gap_x)
        return positions

    for row in range(wave_config.rows):
        y = start_y + row * (ENEMY_HEIGHT + wave_config.gap_y)
        _add_row_positions(positions, wave_config.cols, y, wave_config.gap_x)

    return positions


def create_enemy_formation(
    world: World,
    wave_config: WaveConfig = DEFAULT_WAVE,
) -> list[Entity]:
    """
    """
    enemy_ids = []

    for x, y in _build_wave_positions(wave_config):
        eid = world.create_entity()

        world.add_component(eid, PositionComponent(x=x, y=y))
        world.add_component(eid, VelocityComponent(vx=0.0, vy=0.0))
        world.add_component(eid, TagComponent(label="enemy"))
        world.add_component(eid, SpriteComponent(
            width=ENEMY_WIDTH,
            height=ENEMY_HEIGHT,
            color=COLOR_ENEMY,
        ))
        world.add_component(eid, ColliderComponent(
            width=ENEMY_WIDTH,
            height=ENEMY_HEIGHT,
        ))

        enemy_ids.append(eid)

    return enemy_ids
