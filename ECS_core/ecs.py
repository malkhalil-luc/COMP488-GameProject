# Registry
# give new entity ids, store components and let system query,
#e.g. system ask: give me everything with Position + Velocity
# THE WHOLE WORLD GAME IS HELD HERE IN THIS SINGLE OBJECT.
# NO OTHER THING IN THE GAME CREATE ENTITIES IR READ COMPONENTS DIRECTLY, EVERYTHING GOES THROUGH THIS REGISTRY:
#   FACTORY CALLS
#   SYSTEMS CALLS
#   GAME,PY CALLS

#STORAGE STRUCTURE
# _entities: dict[ entity, dict[type, component]]. > component type is a key

# components, systems, factories will use this

from ecs_core.entity import Entity, Component, System

class World:
    """
    The ECS registry, stores all entities, all components all systems.
    Runs all systems each frame using update().
    """

    def __init__(self) -> None:
        
        self._entities: dict [Entity,dict[type,Component]] = {} # maps each entity ID to a dict {componentType: component_instance}
        
        self._systems: list[System] = [] #order list of systems, called in registration order each frame
        
        self._next_id: int = 0 #counter for generating unique IDs



    def create_entity(self) -> Entity:
        """
        Create and reserve a new unique entity ID and register it in storage
        entity starts with no components 
        """

        entity_id = self._next_id

        self._next_id += 1
        self._entities[entity_id] = {} # new entity with id but no components

        return entity_id

    def remove_entity (self, entity:Entity) -> None:
        """
        Delete an entity with all its components
        used during play when enemy is destroyed, fire goes off screen.
        """
        self._entities.pop(entity, None) # None means don't rais an error if the entity was already removed (removed twice in teh same frame)

    def add_component(self, entity:Entity, component: Component)-> None:
        """
        Attach a component instance to an entity.
        Uses teh component type as a key so each entity can only have one component of each type: 
            ( one position, one velocity)
            {
                entity_id: {
                ComponentType: component_instance,
                ComponentType: component_instance,
                }
            }
        E.g.
            {
            0: { PositionComponent: PositionComponent(x=375, y=522),
                SpriteComponent:   SpriteComponent(w=50, h=30) },
            1: { PositionComponent: PositionComponent(x=100, y=80) }
            }
        """
        self._entities[entity][type(component)]= component


    def get_component (self, entity: Entity, component_type: type) -> Component | None:
        """
        Returns the component of the type related to this entity
        E.g:
            position = world.get_component(player_id, PositionComponent)
            position.x += 5
        """
        return self._entities.get(entity,{}).get(component_type) 
        #_entities.get(entity,{}) returns the dict of that entity, {} if empty
        # get(component_type) returns the components of that entity


    def has_component (self, entity: Entity, component_type: type) -> bool:
        """
        Returns True if this entity has the given component type.
        Used in conditional checks inside systems
        E.g: if world.has_component(eid, HealthComponent):
        """

        return component_type in self._entities.get(entity, {})

    def get_entiteis_with (self, *component_type: type)-> list[Entity]: # * accept any number of types can be passed
        """
        Returns a list of all entities ids that have all the listed components
        the system use: ask the world to give everything that has these types of components to act on it
        
        - it loops every registered entity
        - check its component dict has all the types
        - if yes, include it in the list.
        """
        result = []
        for entity, components in self._entities.items():
            if all(ct in components for ct in component_type):
                result.append(entity)
        
        return result

    def add_system (self, system: System) -> None:
        """
        Register a system to run each frame.
        System are called in the order they are added:

        1. InputSystem - read keyboard
        2. MovementSystem - apply velocity to position
        3. CollisionSystem - detect hits
        4. DamageSystem - apply hit results
        5. RenderSystem - always last to draw everything
        """
        self._systems.append(system)


    def update (self, **kwargs) -> None:
        """
        Run every registered system one time, 
        called once every frame from the game loop. 

        kwargs has the frame data that the systems need, e.g:
        - dt -> float, needed by movement system
        - screen -> pygame.Surface needed by the render system

        each system will obtain what it needs only from kwargs, extras are ignored
        """

        for system in self._systems:
            system.update(self, **kwargs)
