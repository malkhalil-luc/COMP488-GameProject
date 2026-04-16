

from ecs_core.entity import Entity
from ecs_core.component import Component
from ecs_core.system import System
class World:
    """
    Stores entities, components, and systems for the game.
    """

    def __init__(self) -> None:
        self._entities: dict[Entity, dict[type, Component]] = {}
        self._systems: list[System] = []
        self._next_id: int = 0

    def create_entity(self) -> Entity:
        """
        Creates a new entity id and stores it.
        """

        entity_id = self._next_id

        self._next_id += 1
        self._entities[entity_id] = {}

        return entity_id

    def remove_entity(self, entity: Entity) -> None:
        """
        Removes an entity and all of its components.
        """
        self._entities.pop(entity, None)

    def add_component(self, entity: Entity, component: Component) -> None:
        """
        Adds one component to an entity.
        """
        self._entities[entity][type(component)] = component

    def get_component(self, entity: Entity, component_type: type) -> Component | None:
        """
        Returns one component from an entity if it exists.
        """
        return self._entities.get(entity, {}).get(component_type)


    def has_component(self, entity: Entity, component_type: type) -> bool:
        """
        Returns True if an entity has a given component type.
        """

        return component_type in self._entities.get(entity, {})

    def get_entities_with(self, *component_type: type) -> list[Entity]:
        """
        Returns all entities that have every listed component type.
        """
        result = []
        for entity, components in self._entities.items():
            if all(ct in components for ct in component_type):
                result.append(entity)
        
        return result

    def add_system(self, system: System) -> None:
        """
        Adds a system to the update order.
        """
        self._systems.append(system)


    def update(self, kwargs) -> None:
        """
        Runs every registered system once for the current frame.
        """

        for system in self._systems:
            system.update(self, kwargs)

    def clear(self) -> None:
        self._entities.clear()
        self._next_id = 0
