# parent type of the components, PositionComponent, VelocityComponent, HealthComponent are child types.abs
# Polymorphism, so one signature can handle all subtypes

#The ECS registry  does not need to know which specific component it holds, it just need to be a component, 
# in which any type of it(component) can be stored.

#ABC class: Abstract Base Class, python module used to define a base class, which is the template or contract 
# with other classes. |type safety and structure| 

from abc import ABC

class Component(ABC):
    """
    Base class for all components.
    It does not contain any fields or methods
    """
    pass