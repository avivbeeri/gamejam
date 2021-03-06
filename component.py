import pygame
from newvector import Vector2
from ecs import Component
from util import enums
from util import Asset

class Visible(Component):
    pass

class Concealable(Component):
    def __init__(self):
        super(Concealable, self).__init__()
        self.cover = None

class Cover(Component):
    def __init__(self):
        super(Cover, self).__init__()
        self.occupant = None

class PlayerInput(Component):
    def __init__(self):
        super(PlayerInput, self).__init__()
        self.enabled = True

class Facing(Component):
    LEFT, RIGHT = 'left', 'right'
    def __init__(self, direction=None):
        super(Facing, self).__init__()
        self.direction = direction if direction is not None else Facing.RIGHT

class Camera(Component):
    def __init__(self, viewportSize, viewportPosition=(0, 0), layer=0):
        super(Camera, self).__init__()
        self.setViewport(viewportSize)
        self.viewportPosition = viewportPosition
        self.layer = layer
        self.type = None

    def getViewport(self):
        return self.viewport

    def setViewport(self, viewportSize):
        self.viewport = pygame.Surface(viewportSize, pygame.locals.SRCALPHA)

class Constant(Component):
    def __init__(self, value=0):
        super(Constant, self).__init__()
        self.value = value

class AccelerationConstant(Constant):
    def __init__(self, value):
        super(AccelerationConstant, self).__init__(value)
        self._name = 'Acceleration'

class Vector(Component):
    def __init__(self, vector=Vector2()):
        super(Vector, self).__init__()
        self.value = Vector2(vector)

class Acceleration(Vector):
    pass

class Position(Vector):
    pass

class LastPosition(Vector):
    pass

class Velocity(Vector):
    pass

class Dimension(Vector):
    pass

class TargetVelocity(Vector):
    pass

class Drawable(Component):
    def __init__(self, sprite, layer = 0, offset=(0,0)):
        super(Drawable, self).__init__()
        self.set(sprite, layer)
        self.flipped = False
        self.offset = Vector2(offset)

    def set(self, sprite, layer=None, offset=None):
        self.sprite = sprite
        self.image = sprite.current()

        if layer is not None:
            self.layer = layer
        if offset is not None:
            self.offset = Vector2(offset)

    def flip(self, flip=None):
        if flip is None:
            self.flipped = not self.flipped
        else:
            self.flipped = flip


class Animation(Component):
    def __init__(self, framerate=12):
        super(Animation, self).__init__()
        self.framerate = framerate
        self.loop = True
        self.accumulator = 0
        self.currentFrame = 0

class EventHandler(Component):
    def __init__(self):
        super(EventHandler, self).__init__()
        self.handlers = {}

    def attach(self, eventName, handler):
        if not eventName in self.handlers:
            self.handlers[eventName] = []
        self.handlers[eventName].append(handler)

    def handle(self, event):
        eventName = event.type
        if eventName in self.handlers and len(self.handlers[eventName]) > 0:
            for handler in self.handlers[eventName]:
                handler(self.entity, event)


class Interactable(EventHandler):
    def __init__(self, handler=None):
        super(Interactable, self).__init__()
        if handler is not None:
            self.attach(handler)

    def attach(self, handler):
        eventName = enums.INTERACT
        super(Interactable, self).attach(eventName, handler)


class State(Component):
    def __init__(self, **kwargs):
        super(State, self).__init__()
        self.state = kwargs if kwargs is not None else {}

    def __getitem__(self, key):
        return self.state[key]
    def __setitem__(self, key, value):
        self.state[key] = value


class SpriteState(State):
    def __init__(self, **kwargs):
        super(SpriteState, self).__init__(**kwargs)
        self.current = None
        self.last = None


class Collidable(Component):
    def __init__(self):
        super(Collidable, self).__init__()
        self.collisionSet = set()

class Script(Component):
    def __init__(self):
        super(Script, self).__init__()
        self.scripts = []

    def attach(self, script):
        self.scripts.append(script)

class Radar(Component):
    def __init__(self, targetGroups):
        super(Radar, self).__init__()
        self.targetGroups = targetGroups
        self.targets = {}

    def getTargetGroups(self):
        return self.targetGroups
