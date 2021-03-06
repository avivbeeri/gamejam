import pygame, random
from pygame.locals import *

class Maze:
	def __init__(self, mazeLayer, cellSize=4):
		self.mazeArray = []
		self.state = "create"
		self.mLayer = mazeLayer
		self.mLayer.fill((0,0,0,0))
		self.cellSize = cellSize
		self.screenSize = 56
		if (self.screenSize/float(self.cellSize)) != (self.screenSize/self.cellSize):
			raise ArithmeticError("Screen size must be a multiple of cell size!")

		#We're saying that each box of the maze is 4px*4px, so there are 16x16 boxes on the screen
		for y in xrange(self.screenSize/self.cellSize):
			pygame.draw.line(self.mLayer, (0,255,0), (0, y*self.cellSize), (self.screenSize, y*self.cellSize))
			for x in xrange(self.screenSize/self.cellSize):
				self.mazeArray.append(0)
				if y==0:
					pygame.draw.line(self.mLayer, (0,255,0), (x*self.cellSize, 0), (x*self.cellSize, self.screenSize))
		self.totalCells = (self.screenSize/self.cellSize)**2
		self.currentCell = random.randint(0, self.totalCells-1)
		self.visitedCells = 1
		self.cellStack = []
		self.compass = [(-1,0),(0,1),(1,0),(0,-1)]
		self._name = "Maze"

	def update(self, entity, dt):
		if self.state == "idle":
			pass
		elif self.state == "create":
			if self.visitedCells >= self.totalCells:
				self.currentCell = 0
				self.cellStack = []
				self.state = "idle"
				return

			while self.visitedCells < self.totalCells:
				x = self.currentCell % (self.screenSize/self.cellSize)
				y = self.currentCell / (self.screenSize/self.cellSize)

				#Find all neighbours of current cell
				neighbors = []
				for i in xrange(4):
					nx = x + self.compass[i][0]
					ny = y + self.compass[i][1]
					#Check if all its walls are intact
					if ((nx >= 0) and (ny >= 0) and (nx < (self.screenSize/self.cellSize)) and (ny < (self.screenSize/self.cellSize))):
						# Has it been visited?
						if (self.mazeArray[(ny*(self.screenSize/self.cellSize)+nx)] & 0x000F) == 0:
							nidx = ny*(self.screenSize/self.cellSize)+nx
							neighbors.append((nidx,1<<i))

				#If one or more neighbours have been found, choose one at random:
				if len(neighbors) > 0:
					idx = random.randint(0,len(neighbors)-1)
					nidx,direction = neighbors[idx]

					#knock down the wall between it and CurrentCell
					dx = x*self.cellSize
					dy = y*self.cellSize
					if direction & 1: # if direction is West
						self.mazeArray[nidx] |= (4) # knock down the East
						pygame.draw.line(self.mLayer, (0,0,0,0), (dx,dy+1),(dx,dy+self.cellSize-1))
					elif direction & 2: # if the direction is South
						self.mazeArray[nidx] |= (8) # knock down the North
						pygame.draw.line(self.mLayer, (0,0,0,0), (dx+1,dy+self.cellSize),(dx+self.cellSize-1,dy+self.cellSize))
					elif direction & 4: # if direction is east
						self.mazeArray[nidx] |= (1) # knock down the West
						pygame.draw.line(self.mLayer, (0,0,0,0), (dx+self.cellSize,dy+1),(dx+self.cellSize,dy+self.cellSize-1))
					elif direction & 8: # if direction is North
						self.mazeArray[nidx] |= (2) # knock down the South
						pygame.draw.line(self.mLayer, (0,0,0,0), (dx+1,dy),(dx+self.cellSize-1,dy))
					self.mazeArray[self.currentCell] |= direction

					#push CurrentCell location on the CellStack
					self.cellStack.append(self.currentCell)
					#make the new cell CurrentCell
					self.currentCell = nidx
					#add 1 to VisitedCells
					self.visitedCells = self.visitedCells + 1

				else:
				#Make the most recent cell the current cell.
					self.currentCell = self.cellStack.pop()

			#After the while loop
			pygame.draw.rect(self.mLayer, (255,0,255,255), Rect(1,1,self.cellSize-1,self.cellSize-1))
			pygame.draw.rect(self.mLayer, (255,0,255,255), Rect(self.screenSize-self.cellSize+1,\
				self.screenSize-self.cellSize+1,self.cellSize-1,self.cellSize-1))
	def draw(self, screen):
		screen.blit(self.mLayer, (3,3))

class Timer:
	# Note: the time paramenter must be in seconds!
	def __init__ (self, screenLayer, time):
		self.timeLayer = screenLayer
		self.period = (time*1000)/float(self.timeLayer.get_width())
		self.stepno = 0
		self.starttime = pygame.time.get_ticks()
		self.endtime = self.starttime + time*1000
		self._name = "MazeTimer"

	def update(self, entity, dt):
		if pygame.time.get_ticks() >= self.endtime:
			#print "You ran out of time!"
			pygame.event.post(pygame.event.Event(USEREVENT, code="TIMERQUIT"))

		pygame.draw.rect(self.timeLayer, (0,255,0,191), Rect(0,0,self.timeLayer.get_width(), 2))
		if pygame.time.get_ticks() > self.starttime + (self.period*self.stepno):
			self.stepno += 1
			#print "Completed step " + str(self.stepno) + " of " + str(self.timeLayer.get_width())
		pygame.draw.rect(self.timeLayer, (255,0,0,191), Rect(0,0,self.stepno,2))

def mazeUpdate(screen, maze, mazeFrame, timer):
	maze.update()
	maze.draw(screen)
	screen.blit(mazeFrame, (0,-1))
	timer.update()
	screen.blit(timer.timeLayer, (4,screen.get_height()-4))
	
def setupMaze(display, (time, cellSize)):
	world = World()

	# Creating the frame that goes around the maze.
	mazeFrame = pygame.image.load(os.path.join('assets', 'images', 'puzzleframe.png'))
	frame = auxFunctions.create(world, position=(0,0), drawable=mazeFrame, layer=1)
	world.addEntity(frame)

	# Creating the object for the timer.
	timeLayer = pygame.Surface((display.get_width()-8, 2))
	timer = auxFunctions.create(world, position=(4,display.get_height()-3), sprite=timeLayer, layer=2)
	timer.addComponent(maze.Timer(timeLayer, time))
	timer.addComponent(component.Script())
	timer.getComponent("Script").attach(timer.getComponent('MazeTimer').update)
	world.addEntity(timer)

	# Creating the object for the maze.
	mazeLayer = pygame.Surface((display.get_width()-8,display.get_height()-8))
	mazeContent = auxFunctions.create(world, position=(4,4), sprite=mazeLayer, layer=-1)
	mazeContent.addComponent(maze.Maze(mazeLayer, cellSize))
	mazeContent.addComponent(component.Script())
	mazeContent.getComponent("Script").attach(mazeContent.getComponent("Maze").update)
	world.addEntity(mazeContent)

	# Setting the walls
	mapData = auxFunctions.TileMap('maze.tmx')
	tileSurface = mapData.getLayerSurface(0)
	mapEntity = auxFunctions.create(world, position=(0,0), sprite=tileSurface, layer=-1)
	world.addEntity(mapEntity)

	# Creating the player
	playerMarker = pygame.Surface((cellSize-1,cellSize-1)).convert()
	playerMarker.fill((255,0,0))
	player = auxFunctions.create(world, sprite=playerMarker, layer=0, position=(5,5),\
								lastPosition=(5,5), dimension=(cellSize-1, cellSize-1))

	collidable = player.addComponent(component.Collidable())
	def handleCollision(entity, event):
		entity.getComponent("Position").value = Vector2(entity.getComponent("LastPosition").value)
	collidable.attach(handleCollision)

	playerEventHandler = player.addComponent(component.EventHandler())
	def move(entity, event):
		currentPosition = entity.getComponent("Position")
		lastPosition = entity.getComponent("LastPosition")
		if event.type == pygame.KEYDOWN:
			if event.key in enums.keys():
				if keys[event.key] == "Up":
					lastPosition.value = Vector2(currentPosition.value)
					currentPosition.value += Vector2(0, -cellSize)
				elif keys[event.key] == "Down":
					lastPosition.value = Vector2(currentPosition.value)
					currentPosition.value += Vector2(0, cellSize)
				elif keys[event.key] == "Left":
					lastPosition.value = Vector2(currentPosition.value)
					currentPosition.value += Vector2(-cellSize, 0)
				elif keys[event.key] == "Right":
					lastPosition.value = Vector2(currentPosition.value)
					currentPosition.value += Vector2(cellSize, 0)
	playerEventHandler.attach(pygame.KEYDOWN, move)
	world.addEntity(player)

	world.addSystem(RenderSystem(display))
	world.addSystem(ScriptSystem())
	world.addSystem(inputSystem)
	world.addSystem(TileCollisionSystem(mapData))
	return world
