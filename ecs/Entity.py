class Entity:
    # Represents a game entity, which can be given components.

    def __init__(self, id, world):
        self.id = id
        self._world = world
        self.components = {}

    def addComponent(self, component):
        if hasattr(component, '_name'):
            self.components[component._name] = component
            setattr(component, 'entity', self)
        else:
            raise ValueError('Attempted to add an object which isn\'t a component')
        return component

    def removeComponent(self, component):
        if isinstance(component, basestring):
            del self.components[component]
        elif hasattr(component, '_name'):
            del self.components[component._name]
        else:
            raise ValueError('Attempted to remove an object which isn\'t a component')

    def hasComponent(self, component):
        if isinstance(component, basestring):
            return component in self.components
        elif hasattr(component, '_name'):
            return component._name in self.components
        else:
            raise ValueError('Attempted to lookup an object which isn\'t a component')

    def getComponent(self, componentName):
        return self.components[componentName]
