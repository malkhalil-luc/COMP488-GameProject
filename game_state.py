from dataclasses import dataclass

from config import STARTING_LIVES


@dataclass
class GameRuntime:
    state: str = "title"
    score: int = 0
    lives: int = STARTING_LIVES
    leader_alive: bool = False
    leader_hit_cooldown: int = 0
    player_flash_timer: int = 0
    rapid_fire_timer: int = 0
    shield_timer: int = 0
    pickup_text: str = ""
    pickup_text_timer: int = 0

    def reset_run_values(self) -> None:
        self.score = 0
        self.lives = STARTING_LIVES
        self.leader_alive = False
        self.leader_hit_cooldown = 0
        self.player_flash_timer = 0
        self.rapid_fire_timer = 0
        self.shield_timer = 0
        self.pickup_text = ""
        self.pickup_text_timer = 0
