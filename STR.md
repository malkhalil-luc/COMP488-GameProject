Main components: 
    - Initialization: start the game engine
    - Game loop: the infinite loop that keeps the game alive
    - Event Handling: Keyboard and mouse inputs, quitting
    - Rendering: drawing everything on teh screen
    - Update step: change the game state each frame


Skeleton: main.py
    1- import pygame #(game engin)
    2- initialize pygame
        ```
        pygame.init()
        ```
    3- create a window 
    ```
        WIDTH, HEIGHT = 800,600
        screen = pygame.display.set_mode(WIDTH, HEIGHT)
        pygame.display.set_caption("First Game ever..")
    ```
    4- Game loop
        4.1 event handling
        4.2 Draw(Render)
        4.3 update display
    5- clean exit
        pygame.quit()
        system.exit()


ecs_game/
│
├── main.py                        ← Entry point only. Calls Game().run()
│
├── config.py                      ← All constants (WIDTH, HEIGHT, FPS, colors, TILE, speeds)
│
├── core/                          ← The ECS engine itself (reusable, game-agnostic)
│   ├── __init__.py
│   ├── world.py                   ← World class (create_entity, add, get, query, destroy)
│   ├── component.py               ← Base class or protocol for components (optional but clean)
│   └── system.py                  ← Base System class with abstract update() method
│
├── components/                    ← All @dataclass components, one file per domain
│   ├── __init__.py                ← Re-exports all components for easy imports
│   ├── physics.py                 ← Position, Velocity, Collider
│   ├── rendering.py               ← Renderable
│   ├── gameplay.py                ← Health, CoinTag
│   └── tags.py                    ← PlayerTag, EnemyTag, StaticTag (marker components)
│
├── systems/                       ← One file per system
│   ├── __init__.py
│   ├── input_system.py            ← PlayerInputSystem
│   ├── enemy_system.py            ← EnemyMovementSystem
│   ├── movement_system.py         ← MovementSystem
│   ├── collision_system.py        ← CollisionSystem
│   └── render_system.py           ← RenderSystem
│
├── entities/                      ← Factory functions that assemble entities
│   ├── __init__.py
│   ├── player.py                  ← create_player()
│   ├── enemies.py                 ← create_enemy()
│   ├── collectibles.py            ← create_coin()
│   └── environment.py             ← create_rock(), create_tree()
│
├── scenes/                        ← Scene/state management
│   ├── __init__.py
│   ├── base_scene.py              ← Abstract Scene with enter(), update(), render()
│   ├── game_scene.py              ← build_world(), spawn_coins(), game loop logic
│   └── gameover_scene.py          ← GameOverSystem rendering + restart logic
│
├── game.py                        ← Game class: owns the Window, Clock, SceneManager
│
└── assets/                        ← Future-proof slot for images, sounds, fonts
    ├── fonts/
    ├── sounds/
    └── sprites/


    1. constants
    2. Entity registry / Id storeage





    │
├── main.py
├── config.py
│
├── ecs/
│   ├── ecs.py
│   ├── entity.py
│   ├── component.py
│   └── system.py
│
├── components/
│   ├── position.py
│   ├── velocity.py
│   ├── health.py
│   ├── collider.py # we might have non for now
│   ├── weapon.py # we might have non for now
│   ├── sprite.py
│   ├── powerup.py #i know we have non for now
│   └── lifetime.py
│
├── systems/
│   ├── input_system.py
│   ├── movement_system.py
│   ├── enemy_ai_system.py # not sure what is enemy ai or if any we have now
│   ├── shooting_system.py
│   ├── collision_system.py 
│   ├── damage_system.py 
│   ├── powerup_system.py
│   ├
│   └── render_system.py
│
├── factories/
│   ├── player_factory.py
│   ├── enemy_factory.py
│   ├── bullet_factory.py
│   └── powerup_factory.py #if any i see nothing for now
│
├── game/
│   ├── game.py
│   ├── world.py
│   └── 
│
├── assets/
│   ├── sprites/ #if any
│   ├── sounds/ #if any
│   └── fonts/ #if any
│
└── utils/#if any
    ├
    └── collision_utils.py #if any
2. What Each Folde



# **ECS_core**
**entity.py**
```
# =============================================================================
# ecs/entity.py
#
# In ECS an entity is nothing but a unique integer ID.
# It holds no data and has no behavior of its own.
# Data lives in Components. Behavior lives in Systems.
# The entity ID is just the key that links them together.
#
# Example of what the World's storage looks like at runtime:
#
#   {
#     0: { PositionComponent: PositionComponent(x=375, y=522),
#          SpriteComponent:   SpriteComponent(w=50, h=30, color=...),
#          TagComponent:      TagComponent(tag="player") },
#
#     1: { PositionComponent: PositionComponent(x=100, y=80),
#          SpriteComponent:   SpriteComponent(w=36, h=24, color=...),
#          TagComponent:      TagComponent(tag="enemy") },
#   }
#
# Entity 0 and Entity 1 are just the integer keys in that dict.
# Nothing more.

# Type alias — tells anyone reading the code "this int is an entity ID"
# Use it in type hints:  def create_player(world) -> Entity:
# =============================================================================

```

**Component.py**
```
# =============================================================================
# ecs/component.py
#
# Base class for every component in the game.
#
# WHY THIS EXISTS
# ───────────────
# All components are different — Position holds x/y, Sprite holds color/size,
# Health holds hp/max_hp. But the registry (ecs.py) needs to handle ALL of
# them generically, without knowing which specific component it has.
#
# Inheriting from Component gives the registry a single type to work with:
#
#   def add_component(self, entity: Entity, component: Component): ...
#
# WHY ABC (Abstract Base Class)?
# ──────────────────────────────
# Marking the base as abstract prevents anyone from doing:
#
#   c = Component()   ← TypeError: can't instantiate abstract class
#
# You can only instantiate concrete children:
#
#   pos = PositionComponent(x=0, y=0)   ← fine
#
# This is the Open/Closed principle:
#   - Closed: you never modify Component itself
#   - Open:   you extend it by creating new component files
# =============================================================================

```

**System.py**
```
# =============================================================================
# ecs/system.py
#
# Base class for every system in the game.
#
# WHY THIS EXISTS
# ───────────────
# Every system has exactly one job: implement update().
# The base class makes that a hard requirement — not a convention.
#
# If you create a new system and forget update(), Python raises a
# TypeError the moment the game starts, not silently mid-game.
#
# WHY @abstractmethod?
# ────────────────────
# @abstractmethod tells Python:
#   "any class that inherits from System MUST implement this method"
#
# Trying to instantiate a system without update() → immediate TypeError.
# This catches the mistake at startup, not buried in a runtime bug.
#
# WHY **kwargs in update()?
# ─────────────────────────
# Different systems need different extra data each frame:
#   RenderSystem  needs: screen surface
#   MovementSystem needs: delta time
#   InputSystem   needs: nothing extra
#
# Rather than forcing every system to accept every possible argument,
# **kwargs lets each system take only what it needs:
#
#   class RenderSystem(System):
#       def update(self, world, **kwargs):
#           screen = kwargs["screen"]   ← takes only what it needs
#
# The caller (game loop) passes everything. Each system unpacks its own.
# =============================================================================

```
**ecs.py**
```
=============================================================================
# ecs/ecs.py  —  the ECS registry
#
# This is the single object that holds the entire game world.
# It knows every entity, every component attached to each entity,
# and every system that runs each frame.
#
# NOTHING in the game creates entities or reads components directly.
# Everything goes through this registry.
#
# WHO USES THIS AND HOW
# ─────────────────────
# Factories call:
#   world.create_entity()              → get a new ID
#   world.add_component(id, component) → attach data to that ID
#
# Systems call:
#   world.get_entities_with(A, B)      → find all entities that have A and B
#   world.get_component(id, Type)      → read one component from one entity
#
# game.py calls:
#   world.add_system(system)           → register a system
#   world.update(**kwargs)             → run all systems once per frame
#   world.remove_entity(id)            → destroy an entity mid-game
#
# STORAGE STRUCTURE
# ─────────────────
# _entities: dict[Entity, dict[type, Component]]
#
#   {
#     0: { PositionComponent: PositionComponent(x=375, y=522),
#          SpriteComponent:   SpriteComponent(w=50, h=30, color=...) },
#
#     1: { PositionComponent: PositionComponent(x=100, y=80),
#          SpriteComponent:   SpriteComponent(w=36, h=24, color=...) },
#   }
#
# The component TYPE is the key — not a string.
# This means lookups are fast and there are no string typos.
# =============================================================================

```

**what does a factory need from ecs.py? What does a system need from it?**
```
A system needs to ask the registry: "give me all entities that have these components" and then read/write those components. So the registry needs a query method.

Factories don't touch systems at all.
A factory's only job is:

Ask the registry for a new entity ID
Attach components to it
Return the ID

That's it. The factory never knows a system exists.
Systems are registered separately — by game.py, not by any factory. The factory builds what an entity is (its data). The game decides what logic runs on it (its systems).
So the methods ecs.py actually needs are:
For factories:

create_entity() → gives back a new ID
add_component(entity, component) → attaches data to that ID

For systems:

get_components(entity, component_type) → reads one component
get_entities_with(...) → query: "all entities that have these component types"

For game.py:

add_system(system) → registers a system
update(**kwargs) → calls every system's update() in order

For cleanup:

remove_entity(entity) → destroys entity and all its components

That's the full surface area of ecs.py. Ready to write it?
```

# **components**
**position.py**
```
# =============================================================================
# components/position.py

#
# Answers: WHERE is this entity in the world?
#
# (x, y) is the TOP-LEFT corner of the entity's bounding box.
# All rendering and collision math uses this as the reference point.
#
# This component is attached to: player, enemies, leader, bullets.
# Any entity that exists somewhere in space gets a PositionComponent.
#
# WHO READS IT:   RenderSystem, CollisionSystem, MovementSystem, EnemyAISystem
# WHO WRITES IT:  MovementSystem (every frame, applies velocity to position)
# =============================================================================
    World-space position of an entity.

    x : float  — horizontal position in pixels, left edge of the entity
    y : float  — vertical   position in pixels, top  edge of the entity

    Why float and not int?
    ──────────────────────
    MovementSystem will do:  pos.x += vel.vx * dt
    delta time (dt) is a float, so the result is a float.
    Storing as float avoids rounding errors accumulating over many frames.
    pygame.draw.rect() will cast to int when it actually draws.

```
