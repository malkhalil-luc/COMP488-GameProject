from config import SCORE_ENEMY, SCORE_LEADER
from ecs_core.system import System
from components.health import HealthComponent


class DamageSystem(System):

    def update(self, world, kwargs) -> None:
        if kwargs.get("game_state") != "play":
            return

        events = kwargs.get("collision_events", [])
        if not events:
            return

        score = kwargs.get("score", 0)
        lives = kwargs.get("lives", 3)

        # Track entities destroyed this frame to prevent double processing
        destroyed = set()

        # Leader hit cooldown — counts down in frames
        leader_hit_cooldown = kwargs.get("leader_hit_cooldown", 0)

        for event in events:
            event_type = event["type"]

            #  bullet × enemy 
            if event_type == "bullet_enemy":
                bullet_eid = event["bullet"]
                enemy_eid  = event["enemy"]

                if bullet_eid in destroyed or enemy_eid in destroyed:
                    continue

                world.remove_entity(bullet_eid)
                world.remove_entity(enemy_eid)
                destroyed.add(bullet_eid)
                destroyed.add(enemy_eid)
                score += SCORE_ENEMY

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
                            world.remove_entity(leader_eid)
                            destroyed.add(leader_eid)
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

                lives -= 1
                if lives <= 0:
                    lives = 0
                    kwargs["trigger_gameover"] = True

            #  leader × player 
            elif event_type == "leader_player":
                player_eid = event["player"]

                if player_eid in destroyed:
                    continue

                # Only damage if cooldown expired
                if leader_hit_cooldown > 0:
                    continue

                lives -= 1
                leader_hit_cooldown = 90  # 90 frames = 1.5 sec at 60 FPS

                if lives <= 0:
                    lives = 0
                    kwargs["trigger_gameover"] = True

        # Write everything back so game.py read it
        kwargs["score"]               = score
        kwargs["lives"]               = lives
        kwargs["leader_hit_cooldown"] = leader_hit_cooldown

