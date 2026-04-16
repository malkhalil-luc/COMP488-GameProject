from dataclasses import dataclass

from config import (
    ENEMY_ROWS,
    ENEMY_COLS,
    ENEMY_GAP_X,
    ENEMY_GAP_Y,
    ENEMY_SPEED,
    LEADER_WIDTH,
    LEADER_HEIGHT,
    LEADER_HP,
    LEADER_SPEED_X,
    LEADER_SPEED_Y,
)


@dataclass
class WaveConfig:
    rows: int
    cols: int
    gap_x: int
    gap_y: int
    speed: float
    formation: str = "grid"
    move_pattern: str = "straight"
    shooter_count: int = 1
    fire_delay: int = 150
    bullet_speed: float = 4.0
    hole_count: int = 0


@dataclass
class LeaderConfig:
    width: int
    height: int
    hp: int
    speed_x: float
    speed_y: float
    fire_delay: int = 90
    bullet_speed: float = 5.0
    shot_count: int = 1


@dataclass
class LevelConfig:
    name: str
    waves: list[WaveConfig]
    leader: LeaderConfig


LEVELS = [
    LevelConfig(
        name="Level 1",
        waves=[
            WaveConfig(2, 6, 18, 18, 0.34, "wide_line", "straight", 1, 160, 4.0, 0),
            WaveConfig(3, 6, 16, 16, 0.40, "v_shape", "sway", 1, 140, 4.0, 0),
            WaveConfig(3, 5, 20, 16, 0.46, "staggered_rows", "sway", 2, 125, 4.5, 1),
        ],
        leader=LeaderConfig(LEADER_WIDTH, LEADER_HEIGHT, LEADER_HP + 1, 3.0, 1.5, 80, 5.0, 1),
    ),
    LevelConfig(
        name="Level 2",
        waves=[
            WaveConfig(3, 6, 18, 18, 0.48, "split_groups", "straight", 2, 115, 4.7, 1),
            WaveConfig(3, 6, 16, 18, 0.54, "v_shape", "zigzag", 2, 100, 5.0, 2),
            WaveConfig(3, 6, 16, 16, 0.60, "staggered_rows", "zigzag", 3, 90, 5.2, 2),
        ],
        leader=LeaderConfig(LEADER_WIDTH + 8, LEADER_HEIGHT + 6, LEADER_HP + 2, 3.6, 1.8, 68, 5.4, 3),
    ),
    LevelConfig(
        name="Level 3",
        waves=[
            WaveConfig(3, 7, 14, 16, 0.62, "split_groups", "sway", 3, 85, 5.4, 2),
            WaveConfig(3, 7, 14, 16, 0.68, "v_shape", "zigzag", 4, 78, 5.8, 3),
            WaveConfig(3, 7, 14, 14, 0.74, "staggered_rows", "zigzag", 4, 72, 6.0, 3),
        ],
        leader=LeaderConfig(LEADER_WIDTH + 12, LEADER_HEIGHT + 10, LEADER_HP + 4, 4.2, 2.2, 56, 6.2, 3),
    ),
]

DEFAULT_WAVE = LEVELS[0].waves[0]
DEFAULT_LEADER = LEVELS[0].leader
