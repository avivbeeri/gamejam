import auxFunctions
import component
import pygame, os
from util.enums import keys
from util import enums
from newvector import Vector2
from util import resource_path
from util import Asset, SpriteData

# Load assets
# Stairs
stairSprite = 'stairs.png'

# Plants
plantSprite = 'plant.png'
plantHidingSprite = 'plant_hiding.png'

# Bins
binSprite = 'bin.png'
binFullSprite = 'bin_full.png'

# Guards
guardSprite = 'guard.png'
guardSurprisedSprite = 'guard_surprised.png'
guardAlertSprite = 'guard_alert.png'

# Terminal
termWin = 'terminalwin.png'
termSprite = 'terminal.png'

# Text
assetManager = Asset.Manager.getInstance()
silkScreen = assetManager.getFont('silkscreen.ttf')

ghostSprite = 'ghost.png'
ghostRunningSprite = 'ghost_run-sheet.png'
assetManager.putSprite(ghostRunningSprite, Asset.SpriteData(Asset.Manager.loadImage(ghostRunningSprite), 8, (8, 1), (6, 12)))
assetManager.getAllSprites([ghostSprite, termWin, termSprite, guardAlertSprite, guardSurprisedSprite, guardSprite, binSprite, binFullSprite, plantSprite, plantHidingSprite, stairSprite])

def createGhost(world, position):
    groupManager = world.getManager('Group')

    playerEntity = auxFunctions.create(world, position=position, sprite=ghostSprite, layer=1, dimension=(4,12), offset=(-1, 0))
    playerEntity.addComponent(component.Velocity((0, 0)))
    playerEntity.addComponent(component.Acceleration())
    playerEntity.addComponent(component.Visible())
    playerState = playerEntity.addComponent(component.State(hiding=False, moving=False))
    playerSpriteState = playerEntity.addComponent(component.SpriteState(idle=ghostSprite, moving=ghostRunningSprite))
    playerEntity.addComponent(component.Collidable())
    playerEntity.addComponent(component.TargetVelocity())
    playerEntity.addComponent(component.Animation(14))
    playerEntity.addComponent(component.PlayerInput())
    facing = playerEntity.addComponent(component.Facing())

    # Demonstration of how to handle input.
    def handleInput(entity, event):
        targetVelocityComponent = entity.getComponent('TargetVelocity')
        velocityComponent = entity.getComponent('Velocity')
        player = entity.getComponent('PlayerInput')
        playerState = entity.getComponent('State')
        playerSpriteState = entity.getComponent('SpriteState')
        if player.enabled and event.type == pygame.KEYDOWN \
        and keys[event.key] in ("Up", "Down"):
            collisions = entity.getComponent('Collidable').collisionSet
            for other in collisions:
                if groupManager.check(other, 'lift') and keys[event.key] in ("Up", "Down"):
                    originalLiftId = other.id
                    liftPosition = other.getComponent('Position').value
                    lifts = []
                    for lift in groupManager.get('lift'):
                        newPosition = lift.getComponent('Position').value
                        if newPosition.x == liftPosition.x and lift.id != originalLiftId:
                            lifts.append((lift, newPosition.y, abs(newPosition.y - liftPosition.y)))

                    selfPosition = entity.getComponent('Position').value
                    valid = True
                    if keys[event.key] == "Up":
                        lifts = sorted(lifts, key=lambda lift: (not (lift[1] < liftPosition.y), lift[2]))
                        target = lifts[0][0].getComponent('Position').value
                        valid = target.y < liftPosition.y
                    elif keys[event.key] == "Down":
                        lifts = sorted(lifts, key=lambda lift: (not (lift[1] > liftPosition.y), lift[2]))
                        target = lifts[0][0].getComponent('Position').value
                        valid = target.y > liftPosition.y
                    if valid:
                        selfPosition.y, selfPosition.x = target.y,  target.x

    playerInputHandler = playerEntity.addComponent(component.EventHandler())
    playerInputHandler.attach(pygame.KEYDOWN, handleInput)
    playerInputHandler.attach(pygame.KEYUP, handleInput)
    groupManager.add('player', playerEntity)
    world.addEntity(playerEntity)
    return playerEntity

def createBin(world, position):
    groupManager = world.getManager('Group')
    binEntity = auxFunctions.create(world, position=position, dimension=(10,12), sprite=binSprite, layer=0)
    binEntity.addComponent(component.Collidable())
    binEntity.addComponent(component.Interactable())
    binEntity.addComponent(component.Cover())
    binState = binEntity.addComponent(component.SpriteState(empty=binSprite, occupied=binFullSprite))
    groupManager.add('hidable', binEntity)
    groupManager.add('bin', binEntity)
    world.addEntity(binEntity)
    return world.addEntity(binEntity)

def createPlant(world, position):
    groupManager = world.getManager('Group')
    plantEntity = auxFunctions.create(world, position=position, dimension=(10,12), sprite=plantSprite, layer=0)
    plantEntity.addComponent(component.Collidable())
    plantEntity.addComponent(component.Interactable())
    plantEntity.addComponent(component.Cover())
    binState = plantEntity.addComponent(component.SpriteState(empty=plantSprite, occupied=plantHidingSprite))
    groupManager.add('hidable', plantEntity)
    groupManager.add('plant', plantEntity)
    world.addEntity(plantEntity)
    return world.addEntity(plantEntity)

def createStairs(world, position):
    groupManager = world.getManager('Group')
    stairEntity = auxFunctions.create(world, position=position, dimension=(6,12), sprite=stairSprite, layer=0, offset=(-1, -1))
    stairEntity.addComponent(component.Collidable())
    groupManager.add('lift', stairEntity)
    world.addEntity(stairEntity)
    return stairEntity

def createTerminal(world, position):
    groupManager = world.getManager('Group')
    terminal = auxFunctions.create(world, position=position, dimension=(4,8), sprite=termSprite, layer=0)
    terminal.addComponent(component.Collidable())
    termState = terminal.addComponent(component.SpriteState(locked=termSprite, win=termWin))
    termState.current = 'locked'

    def interactHandler(entity, event):
        termState.current = "win"
        world.post(pygame.event.Event(enums.SOUNDEVENT, code="terminal"))
    terminal.addComponent(component.Interactable(interactHandler))

    groupManager.add('terminal', terminal)
    world.addEntity(terminal)
    return terminal

def createGuard(world, position, accOffset=0, cycleTime=5):
    groupManager = world.getManager('Group')
    guardEntity = auxFunctions.create(world, position=position, dimension=(4,14), sprite=guardSprite, layer=1)
    guardEntity.addComponent(component.Velocity((0, 0)))
    guardEntity.addComponent(component.Facing(component.Facing.RIGHT))
    guardEntity.addComponent(component.Acceleration())
    guardEntity.addComponent(component.Radar('player'))
    guardEntity.addComponent(component.SpriteState(patrol=guardSprite, surprised=guardSurprisedSprite, alert=guardAlertSprite))
    guardState = guardEntity.addComponent(component.State())
    guardState['mode'] = 'patrol'
    guardState['modeTime'] = accOffset

    def guardScript(entity, dt):
        global worlds
        radar = entity.getComponent('Radar')
        state = entity.getComponent('State')
        spriteState = entity.getComponent('SpriteState')
        drawable = entity.getComponent('Drawable')
        facing = entity.getComponent('Facing')

        def isVisible(entity, radar):
            if 'player' not in radar.targets or len(radar.targets['player']) == 0:
                return False

            playerPing = next(iter(radar.targets['player']))
            player = playerPing.entity

            entityPosition  = entity.getComponent('Position').value
            entityDirection = facing.direction
            playerPosition  = player.getComponent('Position').value
            if (entityDirection == facing.RIGHT and entityPosition.x <= playerPosition.x) or \
                    (entityDirection == facing.LEFT and entityPosition.x > playerPosition.x):
                return playerPing.visible
            else:
                return False

        def getPlayerDirection(radar):
            playerPing = next(iter(radar.targets['player']))
            player = playerPing.entity
            return playerPing.distance.normalize() * 0.3

        state['modeTime'] += dt
        if state['mode'] == 'patrol':
            if state['modeTime'] > cycleTime:
                state['modeTime'] = 0
                facing.direction = facing.LEFT if facing.direction == facing.RIGHT else facing.RIGHT

            if isVisible(entity, radar):
                state['mode'] = 'surprised'
                state['modeTime'] = 0
        elif state['mode'] == 'surprised':
            if state['modeTime'] > 0.6:
                if isVisible(entity, radar):
                    state['mode'] = 'alert'
                    state['modeTime'] = 0
                else:
                    state['mode'] = 'patrol'
        elif state['mode'] == 'alert':
            if isVisible(entity, radar):
                if state['modeTime'] > 0.4:
                    event = pygame.event.Event(enums.GAMEOVER)
                    world.post(pygame.event.Event(enums.SOUNDEVENT, code="shoot"))
                    world.post(event)
            else:
                state['mode'] = 'surprised'
                state['modeTime'] = 0
        elif state['mode'] == 'chase':
            # We aren't currently using this, but it is useful!
            velocity = entity.getComponent('Velocity')
            if isVisible(entity, radar):
                velocity.value = getPlayerDirection(radar)
            else:
                velocity.value = Vector2()
                state['mode'] = 'patrol'
        spriteState.current = state['mode']


    guardEntity.addComponent(component.Script()).attach(guardScript)
    guardEntity.addComponent(component.Collidable())
    world.addEntity(guardEntity)
    return guardEntity

def createText(world, position, text):
    renderedText = silkScreen.render(text, False, (255,255,255))
    Asset.Manager.getInstance().putSprite(text, SpriteData(renderedText))
    blittedText = auxFunctions.create(world, position=position, sprite=text, layer=6)
    world.addEntity(blittedText)
    return blittedText
