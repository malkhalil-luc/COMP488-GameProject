from ecs_core.system import System
from components.position import PositionComponent
from components.collider import ColliderComponent
from components.tag import TagComponent


def _aabb(pos_a, col_a, pos_b, col_b) -> bool:
    """
    AABB collision - two rectangles overlap when there is NO gap on ANY axis.
    """
    a_left   = pos_a.x
    a_top    = pos_a.y
    a_right  = pos_a.x + col_a.width
    a_bottom = pos_a.y + col_a.height

    b_left   = pos_b.x
    b_top    = pos_b.y
    b_right  = pos_b.x + col_b.width
    b_bottom = pos_b.y + col_b.height

    return (
        a_left   < b_right  and
        a_right  > b_left   and
        a_top    < b_bottom and
        a_bottom > b_top
    )

class CollisionSystem(System):
    """
    Detects AABB overlaps between collidable entity pairs.
    Writes collision events to kwargs for DamageSystem
    """
    def update(self, world, kwargs) -> None:
        """
        Check all meaningful collision pairs and record events.
        """
        if kwargs.get("game_state") != "play":
            return

        # events list — DamageSystem uses it
        kwargs["collision_events"] = []

        all_collidable = world.get_entities_with(
            PositionComponent, ColliderComponent, TagComponent
        )

        player_bullets = []
        enemy_bullets  = []
        enemies        = []
        leaders        = []
        players        = []
        powerups       = []

        for eid in all_collidable:
            tag = world.get_component(eid, TagComponent)
            if tag.label == "player_bullet":
                player_bullets.append(eid)
            elif tag.label == "enemy_bullet":
                enemy_bullets.append(eid)
            elif tag.label == "enemy":
                enemies.append(eid)
            elif tag.label == "leader":
                leaders.append(eid)
            elif tag.label == "player":
                players.append(eid)
            elif tag.label.startswith("powerup_"):
                powerups.append(eid)
        #  Pair 1: bullet × enemy 
        for b_eid in player_bullets:
            b_pos = world.get_component(b_eid, PositionComponent)
            b_col = world.get_component(b_eid, ColliderComponent)

            for e_eid in enemies:
                e_pos = world.get_component(e_eid, PositionComponent)
                e_col = world.get_component(e_eid, ColliderComponent)

                if _aabb(b_pos, b_col, e_pos, e_col):
                    kwargs["collision_events"].append({
                        "type":   "bullet_enemy",
                        "bullet": b_eid,
                        "enemy":  e_eid,
                    })

        #  Pair 2: bullet × leader 
        for b_eid in player_bullets:
            b_pos = world.get_component(b_eid, PositionComponent)
            b_col = world.get_component(b_eid, ColliderComponent)

            for l_eid in leaders:
                l_pos = world.get_component(l_eid, PositionComponent)
                l_col = world.get_component(l_eid, ColliderComponent)

                if _aabb(b_pos, b_col, l_pos, l_col):
                    kwargs["collision_events"].append({
                        "type":   "bullet_leader",
                        "bullet": b_eid,
                        "leader": l_eid,
                    })

        #  Pair 3: enemy × player 
        for e_eid in enemies:
            e_pos = world.get_component(e_eid, PositionComponent)
            e_col = world.get_component(e_eid, ColliderComponent)

            for p_eid in players:
                p_pos = world.get_component(p_eid, PositionComponent)
                p_col = world.get_component(p_eid, ColliderComponent)

                if _aabb(e_pos, e_col, p_pos, p_col):
                    kwargs["collision_events"].append({
                        "type":   "enemy_player",
                        "enemy":  e_eid,
                        "player": p_eid,
                    })

        # Pair 4: leader × player 
        for l_eid in leaders:
            l_pos = world.get_component(l_eid, PositionComponent)
            l_col = world.get_component(l_eid, ColliderComponent)

            for p_eid in players:
                p_pos = world.get_component(p_eid, PositionComponent)
                p_col = world.get_component(p_eid, ColliderComponent)

                if _aabb(l_pos, l_col, p_pos, p_col):
                    kwargs["collision_events"].append({
                        "type":   "leader_player",
                        "leader": l_eid,
                        "player": p_eid,
                    })

        # Pair 5: enemy bullet × player
        for b_eid in enemy_bullets:
            b_pos = world.get_component(b_eid, PositionComponent)
            b_col = world.get_component(b_eid, ColliderComponent)

            for p_eid in players:
                p_pos = world.get_component(p_eid, PositionComponent)
                p_col = world.get_component(p_eid, ColliderComponent)

                if _aabb(b_pos, b_col, p_pos, p_col):
                    kwargs["collision_events"].append({
                        "type": "enemy_bullet_player",
                        "bullet": b_eid,
                        "player": p_eid,
                    })

        # Pair 6: player × powerup
        for powerup_eid in powerups:
            pow_pos = world.get_component(powerup_eid, PositionComponent)
            pow_col = world.get_component(powerup_eid, ColliderComponent)

            for p_eid in players:
                p_pos = world.get_component(p_eid, PositionComponent)
                p_col = world.get_component(p_eid, ColliderComponent)

                if _aabb(pow_pos, pow_col, p_pos, p_col):
                    kwargs["collision_events"].append({
                        "type": "player_powerup",
                        "powerup": powerup_eid,
                        "player": p_eid,
                    })
