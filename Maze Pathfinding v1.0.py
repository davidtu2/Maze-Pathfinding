'''
Name: David Tu
Email: david.tu2@csu.fullerton.edu
Description: Game using A* Search
'''

import pygame
import random
import heapq # Based on my research, heapq is faster since it doesn't have the locking mechanisms that PriorityQueue() has

# Chosen pygame colors
GREEN4 = (0, 139, 0)
DARKSLATEGRAY4 = (82, 139, 139)

# Directions in pygame. In pygame, the origin starts on the top-left corner of the screen with increasing x going right and increasing y going down (not up)
EAST = (1, 0) # RIGHT
WEST = (-1, 0) # LEFT
SOUTH = (0, 1) # DOWN
NORTH = (0, -1) # UP
SOUTHEAST = (1, 1) # RIGHT_DOWN
SOUTHWEST = (-1, 1) # LEFT_DOWN
NORTHEAST = (1, -1) # RIGHT_UP
NORTHWEST = (-1, -1) # LEFT_UP
DIRECTIONS = [EAST, WEST, SOUTH, NORTH, SOUTHEAST, SOUTHWEST, NORTHEAST, NORTHWEST]

# Graph properties
NODE_SIZE = 48
GRAPH_WIDTH = 28
GRAPH_HEIGHT = 15
WIDTH = NODE_SIZE * GRAPH_WIDTH # = 1344
HEIGHT = NODE_SIZE * GRAPH_HEIGHT # = 720

# Nodes in which the player shouldn't be able to pass
WALLS = [(2,0),(0,11),(23,14),(0,0),(1,0),(3,0),(17,0),(18,0),(19,0),(20,0),(22,0),(23,0),(24,0),(27,3),(27,4),(27,5),(27,12),(24,14),(22,14),(21,14),(19,14),(18,14),(10,14),(9,14),(8,14),
(7,14),(6,14),(3,14),(4,14),(2,14),(0,14),(0,13),(0,12),(0,9),(0,8),(0,7),(0,5),(0,4),(0,3),(0,1),(19,6),(15,5),(15,7),(17,10),(17,8),(17,6),(17,5),(17,4),(22,5),(23,7),(22,10),(24,10),(24,9),
(24,7),(25,5),(26,5),(22,8),(19,10),(13,12),(6,5),(4,8),(5,12),(7,12),(7,10),(6,8),(3,5),(3,3),(4,3),(10,3),(11,4),(15,6),(15,8),(14,5),(11,7),(11,6),(11,5),(12,5),(22,2),(24,2),(24,5),(24,6),
(22,7),(22,3),(22,4),(23,2),(26,3),(25,3),(24,3),(20,6),(19,5),(19,7),(19,8),(19,9),(20,10),(21,10),(20,8),(25,9),(26,8),(26,9),(17,9),(17,11),(17,3),(17,2),(13,10),(13,11),(7,11),(6,12),(5,8),
(7,8),(7,9),(4,7),(3,4),(5,5),(4,5),(7,5),(8,5),(9,5),(11,3),(13,2),(13,3),(15,3),(14,3),(15,1),(6,6),(8,8),(10,8),(9,12),(10,12),(11,12),(9,11),(9,10),(15,12),(16,12),(17,12),(13,13),(15,13),
(17,14),(11,14),(5,1),(26,2),(26,0),(19,2),(20,2),(20,3),(20,4),(19,4),(26,7),(19,12),(20,12),(21,12),(22,12),(23,12),(24,12),(24,11),(26,12),(26,11),(3,10),(4,9),(4,10),(5,10),(2,10),(2,9),
(2,8),(2,7),(2,11),(2,12),(3,12),(2,5),(1,3),(2,1),(4,2),(5,2),(7,2),(9,3),(13,1),(12,1),(11,1),(6,4),(8,3),(8,2),(10,1),(27,14),(26,14),(8,7),(11,8),(11,9),(12,9),(13,9),(14,9),(15,9),(11,11),
(15,10),(10,7),(7,1),(7,0),(10,0),(9,0)]

# Initialize pygame, set the screen, determine file directory
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # 1344 x 720

INITIAL_START = pygame.math.Vector2(26, 1)
ENEMY_INITIAL_START = pygame.math.Vector2(26, 10)
ENEMY_INITIAL_START2 = pygame.math.Vector2(0, 2)
INITIAL_GOAL = pygame.math.Vector2(13, 7)

# Initial speeds for the player and the enemy. As of now, speed values can only be INT data types
INITIAL_PLAYER_SPEED = 1
INITIAL_ENEMY_SPEED = 2

# GLOBAL Utility function which convert's a given node's graph coordinates into pygame's rectangular coordinates
def convert(node):
    x = node.x * NODE_SIZE + (NODE_SIZE / 2) # Multiply by NODE_SIZE to find the graph's index, then add by half of the NODE_SIZE to go to the middle of the NODE; The same computation applies to y
    y = node.y * NODE_SIZE + (NODE_SIZE / 2)
    return x, y

def get_random_coordinates(graph):
    start = graph.walls[0]
    
    while start in graph.walls:
        x = random.randint(0, GRAPH_WIDTH - 1)
        y = random.randint(0, GRAPH_HEIGHT - 1)
        start = pygame.math.Vector2(x, y)
        
    return start

# A priority queue implementation using heapq
class PriorityQueue():
    def __init__(self):
        self.nodes = []

    def push(self, priority, value):
        '''
        Params:
        1st: a collection to push the priority-value combination into
        2nd: (a priority, a value): values to be used for comparision since everytime this function is invoked,
        the collection will RESORT by priority, THEN by value (to be used if priorities match)
        '''
        heapq.heappush(self.nodes, (priority, value))

    def pop(self):
        return heapq.heappop(self.nodes)[1] # THIS IS NOT 0 because the 0th index is the root node

    def empty(self):
        if len(self.nodes) == 0:
            return True
        else:
            return False

class Node():
    def __init__(self, value):
        self.value = value
        self.g = 0 # Initial cost is 0 since it takes no effort to get to where you are now
        self.f = 0 # The priority value
        self.path = pygame.math.Vector2(0, 0) # Normally a direction
        self.children = []

    '''
    Abstract Data Types (ADTs) such as this Node clas, are NOT comparable,
    so I have to redefine how to handle the "less than" operation for the PriorityQueue class to work
    '''
    def __lt__(self, other):
        self_vals = (self.f, tuple(self.value))
        other_vals = (other.f, tuple(other.value))
        return self_vals < other_vals

    def get_children(self, graph):
        child_values = []

        # Add the coordinate value of this node with every item in from the directions list
        for direction in DIRECTIONS:
            child_value = self.value + pygame.math.Vector2(direction)
            child_values.append(child_value)
            
        # Remove the coordinates that are not within the screen and are walls by using python's filter function   
        child_values = filter(graph.in_bounds, child_values)
        child_values = filter(graph.passable, child_values)

        '''
        Now that we know what child coordinates to consider, make new nodes for the unvisted and use existing ones if they have been visited
        (The exisitng ones are later found from the nodes dictionary, right after this function call)
        '''
        for value in child_values:
            child = Node(value)
            self.children.append(child)

        return self.children
        
    '''
    Computes the distance cost, g, from f = h + g to get from one node to the next using the distance formula: sqrt((x2 - x1)**2 + (y2 - y1)**2)
    Pygame does this by using length_squared(), but this omits the square root part to avoid floats
    Note that the params are flipped when the function is CALLED
    That is because a_star search actually searches for a path from the GOAL to the START
    This implies that self.value is CLOSER to the AGENT's goal and should be where we want to go from child_value' coordinate
    '''
    def cost_to(self, child_value):
        '''
        If the nodes are adjacent from each other, the distance = 1 due to distance formula of a 45-45-90 degree triangle
        1 is then multiplied by 10 to avoid floats: 1 * 10 = 10
        '''
        if (self.value - child_value).length_squared() == 1:
            return self.g + 10 # return the cost to get to yourself plus the cost to get to the child
        else:
            '''
            If the nodes are diagonal from each other, the distance = hypoteneuse: 1.4 = c from a**2 + b**2 = c**2, where a = b = 1
            10 is then multiplied to avoid floats: 1.4 * 10 = 14, the cost to get to the next DIAGONAL node
            '''
            return self.g + 14
        
class Agent(pygame.sprite.Sprite): # Inherit's pygame's Sprite class
    def __init__(self, position, goal, speed, name): # Python's eqivalent of a constructor
        pygame.sprite.Sprite.__init__(self) # First initialize the Sprite class since it is inherited
        self.image = pygame.image.load('icons/laserBlue08.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50)) # With the retrived icon above, make it bigger by scaling it up
        self.rect = self.image.get_rect() # In pygame, each image is on a rectangle which the programmer can manipulate
        self.speed = speed # Contraint: use INTs for now
        self.current = position # Agent's start coordinates in GRAPH COORDINATES
        self.goal = goal # Agent's goal coordinates in GRAPH COORDINATES
        self.name = name
        self.state = 'Searching'
        
        # Find the agent's center in pygame's rectangular coordinates FROM graph coordinates
        center = convert(position)
        self.rect.center = center # Set the center of the rectangle

        # Store arrow images into a dictionary for drawing a path
        self.arrows = {}
        arrow_img = pygame.image.load('icons/fire01.png').convert_alpha()
        
        # For every direction, rotate one arrow image
        for direction in DIRECTIONS:
            '''
            The function, angle_to returns an angle between the directions: a given direction and the vector: (1, 0), the EAST direction
            For example, if direction returns (0,1), then angle_to returns -90 degrees, which is the angle between (0, 1) to (1, 0)
            '''
            angle = pygame.math.Vector2(direction).angle_to(pygame.math.Vector2(EAST))
            self.arrows[direction] = pygame.transform.rotate(arrow_img, angle)

    # Draws the path to the goal
    def draw_path(self):
        current = self.current
        goal = self.goal

        while current != goal:
            direction = self.closed[tuple(current)].path # get the direction of the current node in vector form; This direction will point towards the goal
            
            center = convert(current)
        
            # Draw the arrow image for a node
            image = self.arrows[tuple(direction)] # Refer to the arrows dictionary to get the arrow IMAGE for the given direction
            rectangle = image.get_rect()
            rectangle.center = center
            screen.blit(image, rectangle)
            
            current = current + direction # Traverse to the next node by adding the direction

            # Consider creating a solution path collection

    # Player's moving function
    def update(self):
        if self.current != self.goal:
            # First, determine the next node
            direction = self.closed[tuple(self.current)].path
            next_node = self.current + direction

            # Get the RECTANGULAR CENTER of the next node
            next_center = convert(next_node)

            # Now get the difference between the next node's center AND the position of the player - This will help determine which direction to move
            difference = (next_center[0] - self.rect.center[0], next_center[1] - self.rect.center[1])
            
            center = list(self.rect.center) # Assignment is neccessary due to rectangle's center attribute being immutable, since it is a tuple

            # The normal cardinal directions
            if difference[0] > 0 and difference[1] == 0:
                center[0] += self.speed # East
            elif difference[0] < 0 and difference[1] == 0:
                center[0] -= self.speed # West
            elif difference[0] == 0 and difference[1] > 0:
                center[1] += self.speed # South
            elif difference[0] == 0 and difference[1] < 0:
                center[1] -= self.speed # North

            # The diagonal directions
            elif difference[0] > 0 and difference[1] > 0: # Southeast
                center[0] += self.speed
                center[1] += self.speed
            elif difference[0] > 0 and difference[1] < 0: # Northeast
                center[0] += self.speed
                center[1] -= self.speed
            elif difference[0] < 0 and difference[1] > 0: # Southwest
                center[0] -= self.speed
                center[1] += self.speed
            elif difference[0] < 0 and difference[1] < 0: # Northwest
                center[0] -= self.speed
                center[1] -= self.speed
            elif difference[0] == 0 and difference[1] == 0: # When the player reaches the node:
                self.current = next_node # Going nowhere, so move to the next node

            self.rect.center = center # Once the player's stride is complete, reset the center coordinate for the player

    # Updates the Player's position in both GRAPH and RECTANGULAR COORDINATES
    def position(self, start):
        self.current = start
        
        center = convert(start)
        self.rect.center = center

    '''
    The manhattan distance, h2, from the lecture slides, scaled to have a bigger effect on the priority calculation
    Note that order doesn't matter since we are using the absolute value
    '''
    def heuristic(self, goal, child):
        return (abs(goal.value.x - child.value.x) + abs(goal.value.y - child.value.y)) * 10

    def a_star_search(self, graph):
        self.state = 'Searching'
        # SWITCHED because search will find a path from the goal TO THE start positions
        start = Node(self.goal)
        goal = Node(self.current)

        # The open and closed queues
        openPriorityQueue = PriorityQueue()
        openPriorityQueue.push(0, start) # root node has 0 priority, that is why pop uses the 1st index instead of 0th
        self.closed = {} # This dictionary will help me keep track of all instances of nodes I have explored
        self.closed[tuple(start.value)] = start

        while not openPriorityQueue.empty():
            # Will always pop, and subsequently, examine the node with the lowest priority, f, thereby, drasticly reducing the search space
            current = openPriorityQueue.pop()
            
            if current.value == goal.value:
                self.state = 'Moving'
                break
            else:
                children = current.get_children(graph) # Passing info about the environment, graph, to the agent to get a colllection of empty child nodes
                
                for child in children:
                    # Grab an earlier reference to the child, if any, else the child that we are dealing will be one of the newly created nodes
                    if tuple(child.value) in self.closed:
                        child = self.closed[tuple(child.value)]
                        
                    # Calculate the distance cost, g, from f = g + h to get from one node to the next
                    cost = current.cost_to(child.value)

                    # Case 1: If child is unvisited
                    if tuple(child.value) not in self.closed:
                        child.g = cost
                        
                        '''
                        Calculate the priority, f, from f = g + h, then push the child into the priority queue
                        Pushing will ALSO resort the queue, since the PriorityQueue class uses Python's heapq
                        '''
                        child.f = cost + self.heuristic(goal, child)
                        child.path = current.value - child.value # Set child with a vector that comes FROM the child TO current (Think: "head minus tail")
                        
                        self.closed[tuple(child.value)] = child # I need to keep track of all the state of the children for future reference
                        openPriorityQueue.push(child.f, child)
                        
                    # Case 2: If child has been visited but it's cost, g, is too large
                    elif cost < child.g:
                        child.g = cost # update with the better cost
                        child.f = cost + self.heuristic(goal, child)
                        child.path = current.value - child.value

                        self.closed[tuple(child.value)] = child # Replace the older version with this updated child
                        openPriorityQueue.push(child.f, child) #What about removing the old version of the child first?
                        
                    # Case 3: If child has been visited but it's cost, g, is too small
                        # Do nothing!

class Enemy(Agent):
    def __init__(self, position, goal, speed, name):
        Agent.__init__(self, position, goal, speed, name)
        
        self.image = pygame.image.load('icons/laserRed08.png').convert_alpha()
        
        arrow_img = pygame.image.load('icons/fire02.png').convert_alpha()
        for direction in DIRECTIONS:
            angle = pygame.math.Vector2(direction).angle_to(pygame.math.Vector2(EAST))
            self.arrows[direction] = pygame.transform.rotate(arrow_img, angle)
        
        
class Graph:
    def __init__(self, width, height, goal):
        self.width = width
        self.height = height

        self.walls = [] # Collection of walls to check against to prevent user from running into them
        for wall in WALLS:
            self.walls.append(pygame.math.Vector2(wall))

        self.goal_image = pygame.image.load('icons/ufoBlue.png').convert_alpha()
        self.goal_image = pygame.transform.scale(self.goal_image, (50, 50))

        # Set the GOAL's center coordinate by calling this' position() function
        self.position(goal)
        self.home = goal

    # Checks to see if the given node is within my screen
    def in_bounds(self, node):
        return 0 <= node.x < self.width and 0 <= node.y < self.height # Is x is between 0 and the width? Is y between 0 and the height?

    # Checks if a node is a wall from the walls list
    def passable(self, node):
        return node not in self.walls

    def position(self, goal):
        self.home = goal
        center = convert(goal)

        self.rectangle = self.goal_image.get_rect()
        self.rectangle.center = (center)

    # Print out a list of the walls for easy updating
    def print_walls(self):
        for wall in self.walls:
            print('(' + str(int(wall.x)) + ',' + str(int(wall.y)) + ')')

    # Draws the ground, the walls, and the goal icon
    def draw(self):
        # First, let's draw the ground
        screen.fill(GREEN4)
        
        # Then, let's draw the walls
        for wall in self.walls:
            '''
             Rect function signature:
             1st param: Where to draw the wall
             2nd param: The width and height of the wall
            '''
            position = wall * NODE_SIZE
            rectangle = pygame.Rect(position, (NODE_SIZE, NODE_SIZE))
            pygame.draw.rect(screen, DARKSLATEGRAY4, rectangle) # Draw the rectangle onto the screen, with the given color

        # Now let's draw the goal icon
        screen.blit(self.goal_image, self.rectangle)
    
# Set up the game
print('Loading game. Please wait...\n')

# Maze Setup
maze = Graph(GRAPH_WIDTH, GRAPH_HEIGHT, INITIAL_GOAL)

# Player setup
player = Agent(INITIAL_START, maze.home, INITIAL_PLAYER_SPEED, 'Ready Player One') # We want to step 1 node at a time, so use NODE_SIZE as the speed:
players = pygame.sprite.RenderUpdates() # Instantiate a Pygame sprite collection in order for it to iterate through each added sprite to update them all simultaneously when needed
players.add(player)

# Enemy setup
enemy = Enemy(ENEMY_INITIAL_START, player.current, INITIAL_ENEMY_SPEED, 'Enemy One')
enemy2 = Enemy(ENEMY_INITIAL_START2, player.current, INITIAL_ENEMY_SPEED, 'Enemy Two')
enemies = pygame.sprite.RenderUpdates()
enemies.add(enemy)
enemies.add(enemy2)

# Group which contains ALL the sprites
all_sprites = pygame.sprite.RenderUpdates()
all_sprites.add(player)
all_sprites.add(enemy)
all_sprites.add(enemy2)

# Controls the game screen I am in
on = True
running = True

# Start the game
while on:
    retry = True
    barrier = (-1, -1)

    player.a_star_search(maze)
    print('Load complete. Starting game...\n')
    
    while running:
        # Check for player input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Check if the 'w' key is pressed
                if event.key == pygame.K_w:
                    maze.print_walls()
                
            if event.type == pygame.MOUSEBUTTONDOWN: # Get the screen coords of the mouseclick, then int divide by NODE_SIZE to get the graph coordinates
                mouse_position = pygame.math.Vector2(pygame.mouse.get_pos()) // NODE_SIZE

                if event.button == 1: # if there is a left mouse click, toggle the wall at the specified location
                    if mouse_position in maze.walls:
                        maze.walls.remove(mouse_position)
                    elif mouse_position == enemy.current or mouse_position == player.current:
                        print("You can't place a wall on top of an agent!")
                    else:
                        if mouse_position not in maze.walls:
                            if barrier in maze.walls:
                                maze.walls.remove(barrier)
                            maze.walls.append(mouse_position)
                            barrier = mouse_position

                if event.button == 2: # if there is a middle mouse click, update the start position of the player
                    player.position(mouse_position)

                if event.button == 3: # Finally, if there is a right mouse click, update the goal
                    maze.position(mouse_position) # Eventually updates the image of the home base through the maze.draw() command
                    player.goal = mouse_position

                # Recalculate search whenever MOUSEBUTTONDOWN
                player.a_star_search(maze)

        for enemy in enemies:
            enemy.goal = player.current
            enemy.a_star_search(maze) # Will this process ever stop in the case that the enemy is trapped?

        # Start drawing after all the updates have been applied
        maze.draw()
        if player.state == 'Moving':
             player.draw_path()
             player.update()
        for enemy in enemies:
            if enemy.state == 'Moving':
                enemy.draw_path()
                enemy.update()
        #players.update()
        #enemies.update()
        #all_sprites.update()

        '''
        Collision Detection: Finds collisions between members of each group
        If either the 3rd/4th parameter is True, the collided members will be removed from their group
        3rd param applies to the group in the 1st param
        4th param applies to the group in the 2nd param
        '''
        for enemy in pygame.sprite.groupcollide(players, enemies, True, True):
            '''
            Reset/Initialize procedure
            WORKAROUND: Pygame's groupcollide() seems to prevent me from re-using references of player and enemy, as a set to be used together
            As a workaround, I have to declare new instances - In this case, a new enemies are created
            Hypothesis: According to the documentation on groupcollide(), when a collision occurs, a dictionary entry will be added linking the collided sprites
            This may be the reason why they instantly collide, when re-running the game
            '''
            enemies.empty()
            all_sprites.empty()

            start = get_random_coordinates(maze)
            enemy = Enemy(start, player.current, INITIAL_ENEMY_SPEED, 'New Enemy One')
            start = get_random_coordinates(maze)
            enemy2 = Enemy(start, player.current, INITIAL_ENEMY_SPEED, 'New Enemy Two')

            enemies.add(enemy)
            enemies.add(enemy2)
            all_sprites.add(enemy)
            all_sprites.add(enemy2)

            player.position(INITIAL_START)
            players.add(player) # After player collision, players container is already emptied
            all_sprites.add(player)

            running = False

        #players.draw(screen)
        #enemies.draw(screen)
        all_sprites.draw(screen)
        pygame.display.flip()

    while retry:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                on = False
                retry = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    on = False
                    retry = False
                
                if event.key == pygame.K_SPACE:
                    running = True
                    retry = False

                '''if event.key == pygame.K_w:
                    maze.print_walls()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.math.Vector2(pygame.mouse.get_pos()) // NODE_SIZE

                if event.button == 1: # if there is a left mouse click, toggle the wall at the specified location
                    if mouse_position in maze.walls:
                        maze.walls.remove(mouse_position)
                    elif mouse_position == enemy.current or mouse_position == player.current:
                        print("You can't place a wall on top of an agent")
                    else:
                        if barrier in maze.walls:
                            maze.walls.remove(barrier)
                        maze.walls.append(mouse_position)
                        barrier = mouse_position'''

            maze.draw()
            pygame.display.flip()

print('Exiting...\n')
pygame.quit()
