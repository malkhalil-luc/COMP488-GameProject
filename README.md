```
main.py
  └── Game.__init__()
        ├── World() created (empty)
        └── 7 systems registered

game.run() ──────────────────────────── loop
  │
  ├── collect events
  ├── handle state transitions (game.py only)
  ├── _reset() if needed → world.clear() + factories
  ├── build fDict_kwargs (shared dict)
  │
  ├── world.update(fDict_kwargs)
  │     ├── InputSystem    → writes vel.vx
  │     ├── FireSystem     → creates bullet entities
  │     ├── EnemyAISystem  → writes vel.vy, checks wave_cleared
  │     ├── MovementSystem → moves all, clamps player, removes offscreen
  │     ├── CollisionSystem→ detects hits, writes collision_events
  │     ├── DamageSystem   → processes hits, removes entities, updates score/lives
  │     └── RenderSystem   → draws all visible entities
  │
  ├── read signals from fDict_kwargs
  ├── draw HUD
  ├── draw overlay if needed
  └── display.flip() + clock.tick(60)
  ```