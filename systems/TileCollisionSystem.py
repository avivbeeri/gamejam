# -*- coding: utf-8 -*-
from newvector import Vector2
import pygame
from ecs import System
import math
from util import enums


class TileCollisionSystem(System):

    def __init__(self, tileMap):
        super(TileCollisionSystem, self).__init__();
        self.requirements = ('Collidable', 'Position')
        self.tileMap = tileMap
        self.tileEntityMap = {}
        self.entityCollisionSet = {}

    def getEntityCollisions(self, id):
        if id in self.entityCollisionSet:
            return self.entityCollisionSet[id]
        else:
            return []

    def getEntitiesInTile(self, x, y):
        if (x, y) in self.tileEntityMap:
            return self.tileEntityMap[int(x), int(y)]
        else:
            return []

    def getTilePosition(self, vector):
        tileX = math.floor(vector.x / self.tileMap.cellSize[0])
        tileY = math.floor(vector.y / self.tileMap.cellSize[1])
        return Vector2(tileX, tileY)

    def isRaycastClear(self, start, end):
        # Bresenham Algorithm
        # http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm#Python
        solid = False
        tiles = []
        startTile = self.getTilePosition(start)
        endTile = self.getTilePosition(end)
        delta = endTile - startTile


        isSteep = abs(delta.y) > abs(delta.x)
        if isSteep:
            startTile.x, startTile.y = startTile.y, startTile.x
            endTile.x, endTile.y = endTile.y, endTile.x

        swapped = False
        if (startTile.x > endTile.x):
            startTile.x, endTile.x = endTile.x, startTile.x
            startTile.y, endTile.y = endTile.y, startTile.y

        delta = endTile - startTile
        error = int(delta.x / 2.0)
        y = startTile.y
        ystep = 1 if startTile.y < endTile.y else -1

        for x in range(int(startTile.x), int(endTile.x + 1)):
            coord = (y, x) if isSteep else (x, y)
            tiles.append(coord)
            tileX, tileY = coord
            if self.tileMap.isTileSolid(tileX, tileY):
                return False
            error -= abs(delta.y)
            while error < 0:
                y = y + ystep
                error += delta.x

        return True


    def process(self, entities, dt):
        # Dictionary to store items who we need to correct the physics of
        tileCollidedEntities = set()

        # Reset the entity collision sets for this frame.
        self.entityCollisionSet = {}

        # Reset our knowledge of which entities are in which tiles
        self.tileEntityMap = {}

        # Process entities
        for entity in entities:
            # Initalise the entityCollisionSet
            self.entityCollisionSet[entity.id] = set()

            # Retrieve relevant components
            positionComponent = entity.getComponent('Position')
            position = positionComponent.value
            collidable = entity.getComponent('Collidable')
            collidable.collisionSet.clear()
            # Does entity have a size?
            dimension = entity.getComponent('Dimension').value \
                    if entity.hasComponent('Dimension') \
                    else Vector2(1, 1)

            # Calculate the number of tiles entity overlaps
            maxPosition = position + dimension
            startTile = self.getTilePosition(position)
            endTile = self.getTilePosition(maxPosition)

            # Test collisions in tiles which entity overlaps
            for tileX in range(int(startTile.x), int(endTile.x + 1)):
                for tileY in range(int(startTile.y), int(endTile.y)):
                    # Record the tile location for the entity
                    if (tileX, tileY) not in self.tileEntityMap:
                        self.tileEntityMap[tileX, tileY] = set()
                    self.tileEntityMap[tileX, tileY].add(entity)
                    if self.tileMap.isTileSolid(tileX, tileY):
                        tileCollidedEntities.add(entity)

        # Dispatch events and correct the physics
        # This method is really dumb and should be improved
        # for high-speed objects
        # NOTE: We currently don't update the tileEntityMap with physics corrections
        for entity in tileCollidedEntities:
            # Dispatch a collision event
            if self.isOffscreen(entity) is not None:
                event = pygame.event.Event(enums.OFFSCREEN, { 'entity': entity.id, 'edge': self.isOffscreen(entity) })
            else:
                event = pygame.event.Event(enums.COLLISION, {'collisionType': 'tile'})
            self.world.post(event)

            if entity.hasComponent('Velocity'):
                # Correct entity position
                positionComponent = entity.getComponent('Position')
                position = positionComponent.value
                velocityComponent = entity.getComponent('Velocity')
                position -= velocityComponent.value
                velocityComponent.value = Vector2()
            elif entity.hasComponent('LastPosition'):
                positionComponent.value = Vector2(entity.getComponent('LastPosition').value)

        # Process E-E collisions
        # This will eventually be refactored into its own system
        # For simplification reasons
        for key in self.tileEntityMap:
            checkedEntities = set()
            entities = self.tileEntityMap[key]
            while len(entities) > 1:
                currentEntity = entities.pop()
                checkedEntities.add(currentEntity)
                for other in entities:
                    # Check if the two entities are actually colliding
                    if other not in self.entityCollisionSet[currentEntity.id] and \
                        areEntitiesColliding(currentEntity, other):
                        # Update the component collision sets
                        self.entityCollisionSet[currentEntity.id].add(other)
                        self.entityCollisionSet[other.id].add(currentEntity)

                        # Dispatch a collision event
                        event = pygame.event.Event(enums.COLLISION, {'collisionType': 'entity', 'other': entity.id})
                        self.world.post(event)

                        currentEntity.getComponent('Collidable').collisionSet = self.entityCollisionSet[currentEntity.id]
                        other.getComponent('Collidable').collisionSet = self.entityCollisionSet[other.id]
                self.tileEntityMap[key] = checkedEntities

    def isOffscreen(self, entity):
        position = entity.getComponent('Position').value
        dimension = getEntityDimension(entity)

        tilePosition = self.getTilePosition(position)
        tileDimension = self.getTilePosition(dimension)

        if tilePosition.x < -1:
            return 'LEFT'
        elif tilePosition.x + tileDimension.x >= self.tileMap.getWidthInTiles() + 1:
            return 'RIGHT'
        elif tilePosition.y < -1:
            return 'TOP'
        elif tilePosition.y + tileDimension.y >= self.tileMap.getHeightInTiles() + 1:
            return 'BOTTOM'
        else:
            return None

def areEntitiesColliding(entity1, entity2):
    position1 = entity1.getComponent('Position').value
    dimension1 = getEntityDimension(entity1)
    position2 = entity2.getComponent('Position').value
    dimension2 = getEntityDimension(entity2)

    return (int(position1.x) < int(position2.x) + dimension2.x) and \
        (int(position1.x) + dimension1.x > int(position2.x)) and \
        (int(position1.y) < int(position2.y) + dimension2.y) and \
        (int(position1.y) + dimension1.y > int(position2.y))

def getEntityDimension(entity):
    return entity.getComponent('Dimension').value \
            if entity.hasComponent('Dimension') \
            else Vector2(0, 0)
