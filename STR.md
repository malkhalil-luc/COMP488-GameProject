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