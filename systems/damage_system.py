import random

from config import SCORE_ENEMY, SCORE_LEADER
from ecs_core.system import System
from components.health import HealthComponent
from components.position import PositionComponent
from components.tag import TagComponent
from entities.effect import create_burst_effect
from entities.powerup import create_powerup


class DamageSystem(System):

    def update(self, world, kwargs) -> None:
        if kwargs.get("game_state") != "play":
            return

        events = kwargs.get("collision_events", [])
        escaped_enemies = kwargs.get("escaped_enemies", [])
        kwargs["sound_events"] = kwargs.get("sound_events", [])
        if not events:
            if not escaped_enemies:
                return

        score = kwargs.get("score", 0)
        lives = kwargs.get("lives", 3)
        rapid_fire_bonus = 0
        shield_bonus = 0
        pickup_text = ""

        # Track entities destroyed this frame to prevent double processing
        destroyed = set()

        # Leader hit cooldown — counts down in frames
        leader_hit_cooldown = kwargs.get("leader_hit_cooldown", 0)
        shield_timer = kwargs.get("shield_timer", 0)

        for _eid in escaped_enemies:
            lives -= 1
            if lives <= 0:
                lives = 0
                kwargs["trigger_gameover"] = True

        for event in events:
            event_type = event["type"]

            #  bullet × enemy 
            if event_type == "bullet_enemy":
                bullet_eid = event["bullet"]
                enemy_eid  = event["enemy"]

                if bullet_eid in destroyed or enemy_eid in destroyed:
                    continue

                enemy_pos = world.get_component(enemy_eid, PositionComponent)
                enemy_tag = world.get_component(enemy_eid, TagComponent)
                enemy_health = world.get_component(enemy_eid, HealthComponent)
                world.remove_entity(bullet_eid)
                destroyed.add(bullet_eid)

                if enemy_health is not None:
                    enemy_health.hp -= 1
                    kwargs["sound_events"].append("hit_enemy")
                    if enemy_health.hp > 0:
                        continue

                world.remove_entity(enemy_eid)
                destroyed.add(enemy_eid)
                score += SCORE_ENEMY

                if enemy_pos is not None:
                    create_burst_effect(
                        world,
                        enemy_pos.x + 8,
                        enemy_pos.y + 8,
                        (255, 180, 80),
                    )

                if enemy_pos is not None and enemy_tag is not None and enemy_tag.label == "enemy" and random.random() < 0.20:
                    drop_kind = random.choice([
                        "powerup_life",
                        "powerup_rapid",
                        "powerup_shield",
                    ])
                    create_powerup(world, enemy_pos.x, enemy_pos.y, drop_kind)

            #  bullet × leader 
            elif event_type == "bullet_leader":
                bullet_eid = event["bullet"]
                leader_eid = event["leader"]

                if bullet_eid in destroyed:
                    continue

                world.remove_entity(bullet_eid)
                destroyed.add(bullet_eid)
                score += SCORE_LEADER

                if leader_eid not in destroyed:
                    health = world.get_component(leader_eid, HealthComponent)
                    if health is not None:
                        health.hp -= 1
                        if health.hp <= 0:
                            leader_pos = world.get_component(leader_eid, PositionComponent)
                            world.remove_entity(leader_eid)
                            destroyed.add(leader_eid)
                            if leader_pos is not None:
                                create_burst_effect(
                                    world,
                                    leader_pos.x + 20,
                                    leader_pos.y + 20,
                                    (255, 120, 120),
                                )
                                create_burst_effect(
                                    world,
                                    leader_pos.x + 36,
                                    leader_pos.y + 24,
                                    (255, 220, 100),
                                )
                            kwargs["trigger_victory"] = True

            #  enemy × player 
            elif event_type == "enemy_player":
                enemy_eid  = event["enemy"]
                player_eid = event["player"]

                if enemy_eid in destroyed or player_eid in destroyed:
                    continue

                # Enemy destroyed on contact — one touch = one life lost
                world.remove_entity(enemy_eid)
                destroyed.add(enemy_eid)

                if shield_timer <= 0:
                    lives -= 1
                    kwargs["sound_events"].append("player_hurt")
                    if lives <= 0:
                        lives = 0
                        kwargs["trigger_gameover"] = True

            #  leader × player 
            elif event_type == "leader_player":
                player_eid = event["player"]

                if player_eid in destroyed:
                    continue

                # Only damage if cooldown expired
                if leader_hit_cooldown > 0 or shield_timer > 0:
                    continue

                lives -= 1
                leader_hit_cooldown = 90  # 90 frames = 1.5 sec at 60 FPS
                kwargs["sound_events"].append("player_hurt")

                if lives <= 0:
                    lives = 0
                    kwargs["trigger_gameover"] = True

            # enemy bullet × player
            elif event_type == "enemy_bullet_player":
                bullet_eid = event["bullet"]

                if bullet_eid in destroyed:
                    continue

                world.remove_entity(bullet_eid)
                destroyed.add(bullet_eid)

                if shield_timer <= 0:
                    lives -= 1
                    kwargs["sound_events"].append("player_hurt")
                    if lives <= 0:
                        lives = 0
                        kwargs["trigger_gameover"] = True

            elif event_type == "player_powerup":
                powerup_eid = event["powerup"]

                if powerup_eid in destroyed:
                    continue

                tag = world.get_component(powerup_eid, TagComponent)
                world.remove_entity(powerup_eid)
                destroyed.add(powerup_eid)

                if tag is None:
                    continue

                if tag.label == "powerup_life":
                    lives = min(lives + 1, 5)
                    pickup_text = "EXTRA LIFE"
                elif tag.label == "powerup_rapid":
                    rapid_fire_bonus += 360
                    pickup_text = "RAPID FIRE"
                elif tag.label == "powerup_shield":
                    shield_bonus += 300
                    pickup_text = "SHIELD"

        # Write everything back so game.py read it
        kwargs["score"]               = score
        kwargs["lives"]               = lives
        kwargs["leader_hit_cooldown"] = leader_hit_cooldown
        kwargs["rapid_fire_bonus"]    = rapid_fire_bonus
        kwargs["shield_bonus"]        = shield_bonus
        kwargs["pickup_text"]         = pickup_text
