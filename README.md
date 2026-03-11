# ECS: Entity Component System. 
**Replaces 'is-a' relation with composition**

## Object rriented design: **Inheretance** (Multiple inheritance: deep , wide)
OOP structures the code around objects that combine data and behavior. Inheritance hierarchies in large systems brings long chains that make adding a new feature force modifying the entire hierarchy or create many new subclasses.

***Problems with OO design***
- **Complexity Management**: Inheritance and encapsulation introduce Rigid and Fragile Code
    - Rigid: hard to make changes (add or remove features not easy)
    - Fragile: Small change brakes things (one bug fix might introduce many new bugs), e.g. base class changes can cause unpredictable brakes.
- **Poor reusability**: Herd to share code (introduce duplicate code)
- **Performance**: Slow as objects are scattered in memory and virtual calls (in games FPS is low ) <> higher CPU usage  <> cache miss
- **Testing**:
    - Fragile tests: Changing anything in a base class (e.g. LivingEntity) can break dozens of tests in derived classes (Player, Enemy, Boss, etc.).
    - Hard to isolate: You often have to create a whole object hierarchy just to test one small behavior.
    - Complex mocking: You need to mock deep inheritance chains and virtual methods.
    - Low reusability of tests: Test code gets duplicated or becomes overly complicated.

- **Debugging**:
    - Deep call stacks: When something breaks, the debugger jumps through many layers of overridden methods.
    - Hidden behavior: It’s hard to know which class actually implements a certain function (Is this coming from Character, Player, or Warrior?).
    - Spooky action at a distance: A bug in a base class can affect many unrelated objects.
    - Difficult to inspect state: You can’t easily see everything an object "is" at runtime.


## What is ECS
ECS structures objects and behavior in a data-oriented and modular way. It separates data, identity, and behavior into three distinct parts:

- **Entities**: Identifiers represents an object, it has no data and no logic (entity_1 = 1, entity_2 = 2 ..etc)
- **Components**: Data 
- **Systems**: Behavior | functions   


Entity representation: 
- Dict (it does not grant the optimal performance as object are still scattered)
- Array (grant higher performance over dict due fast cashing, locality, fast lookup O(1) as arrays elements are stored in contigous locations) 

**Mental Model:**
Entities represent objects in the game world. Components store the data describing those entities. Systems iterate over entities that contain specific components and apply behavior to them.

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