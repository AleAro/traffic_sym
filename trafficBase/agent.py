#agent.py
import networkx as nx
from mesa import Agent
import math

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

class Car(Agent):
    """
    Car agent that can find paths using A* algorithm.
    """
    def __init__(self, unique_id, model, start, destination):
        super().__init__(unique_id, model)
        self.start = start
        self.destination = destination
        print(f"Car {self.unique_id} created with start {self.start} and destination {self.destination}")
        self.path = []

    def find_path(self):
        # Directly access the graph
        G = self.model.G
        print(G)
        try:
            self.path = nx.astar_path(G, self.start, self.destination, heuristic)
            print(f"Car {self.unique_id} found path from {self.start} to {self.destination}")
        except nx.NetworkXNoPath:
            print(f"No path found for {self.unique_id} from {self.start} to {self.destination}")
            self.path = []

    def move(self):
        # Get cell in front of the car
        directions = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
        direction = self.get_direction()
        next_cell = None
        if direction:
            dx, dy = directions[direction]
            front_x, front_y = self.pos[0] + dx, self.pos[1] + dy
            next_cell = self.model.grid.get_cell_list_contents([(front_x, front_y)])
        # If the cell is a traffic light, and it is red, do not move
        if next_cell and isinstance(next_cell[0], Traffic_Light) and not next_cell[0].state:
            next_step = self.pos
            return
        if self.path:
            next_step = self.path.pop(0)
            self.model.grid.move_agent(self, next_step)
            if self.pos == self.destination:
                print(f"Car {self.unique_id} has reached its destination.")

        # Checamos si hay mas de 3 carros en frente
        #neighborhood_three = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False, radius=3)
        # if direction:
        #     dx, dy = directions[direction]
        #     front_three_x = [self.pos[0] + dx, self.pos[0] + 2*dx, self.pos[0] + 3*dx]
        #     front_three_y = [self.pos[1] + dy, self.pos[1] + 2*dy, self.pos[1] + 3*dy]
        #     next_three_cells = [self.model.grid.get_cell_list_contents([front_three_x[i], front_three_y[i]]) for i in range(3)]
        #     next_three_cells = [True if next_three_cells[i] and isinstance(next_three_cells[i][0], Car) else False for i in range(3)]
        #     if all(next_three_cells):
        #         # Change lanes
        #         if direction == 'Up':
        #             self.path = self.path[:1] + [(self.pos[0] - 1, self.pos[1] + 1)] + self.path[1:]
        #         elif direction == 'Down':
        #             self.path = self.path[:1] + [(self.pos[0] + 1, self.pos[1] - 1)] + self.path[1:]
        #         elif direction == 'Left':
        #             self.path = self.path[:1] + [(self.pos[0] - 1, self.pos[1] - 1)] + self.path[1:]
        #         elif direction == 'Right':
        #             self.path = self.path[:1] + [(self.pos[0] + 1, self.pos[1] + 1)] + self.path[1:]
        #         return

    def get_direction(self):
        # get the direction from the path the car is following
        if self.path:
            dx = self.path[0][0] - self.pos[0]
            dy = self.path[0][1] - self.pos[1]
            if dx == 1:
                return 'Right'
            elif dx == -1:
                return 'Left'
            elif dy == 1:
                return 'Up'
            elif dy == -1:
                return 'Down'

    def step(self):
        if not self.path:
            self.find_path()
        self.move()

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green (True) or red (False)
            timeToChange: After how many step should the traffic light change color
        """
        self.state = state
        self.timeToChange = timeToChange
        self.direction = None


    def step(self):
        """
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state
            self.model.update_graph_edge_weights(self)

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass
