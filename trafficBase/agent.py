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
    def __init__(self, unique_id, model, start, destination, graph):
        super().__init__(unique_id, model)
        self.start = start
        self.graph = graph
        self.destination = destination
        print(f"Car {self.unique_id} created with start {self.start} and destination {self.destination}")
        self.path = []

    def find_path(self):
        # Directly access the graph
        G = self.model.G
        print(G)
        try:
            self.path = nx.astar_path(self.graph, self.start, self.destination, heuristic)
            print(f"Car {self.unique_id} found path from {self.start} to {self.destination}")
        except nx.NetworkXNoPath:
            print(f"No path found for {self.unique_id} from {self.start} to {self.destination}")
            self.path = []

    def move(self):
        # Get cell in front of the car
        directions = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
        direction = self.get_direction()
        if direction:
            dx, dy = directions[direction]
            front_x, front_y = self.pos[0] + dx, self.pos[1] + dy
            # Ensure next_cell is a list, even if empty
            next_cell = self.model.grid.get_cell_list_contents([(front_x, front_y)]) if self.model.valid_position(front_x, front_y) else []
        else:
            # If there's no direction, set next_cell as an empty list
            next_cell = []

        # Check if the next cell is a traffic light or another car
        if any(isinstance(obj, Traffic_Light) and not obj.state for obj in next_cell) or any(isinstance(obj, Car) for obj in next_cell):
            return  # Stop the car

        if self.path:
            next_step = self.path.pop(0)
            self.model.grid.move_agent(self, next_step)
            if self.pos == self.destination:
                print(f"Car {self.unique_id} has reached its destination.")
                self.model.schedule.remove(self)
                self.model.grid.remove_agent(self)

        if self.pos is None:
            return

    # Rest of the original code...


    # Rest of the original code for checking cars in the next three cells...


        # Checamos si hay mas de 3 carros en frente
        neighborhood_three = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False, radius=3)
        if direction:
            dx, dy = directions[direction]
            front_three_x = [self.pos[0] + dx, self.pos[0] + 2*dx, self.pos[0] + 3*dx]
            front_three_y = [self.pos[1] + dy, self.pos[1] + 2*dy, self.pos[1] + 3*dy]
            valid_positions = [(x,y) for x,y in zip(front_three_x, front_three_y) if self.model.valid_position(x,y)]
            next_three_cells = [self.model.grid.get_cell_list_contents(pos) for pos in valid_positions]

            next_three_cells_occupied = [any([isinstance(c, Car)]) for cell in next_three_cells for c in cell]
            if all(next_three_cells_occupied):
                print(next_three_cells_occupied)
                if direction == 'Up':
                    lane_change_step = (self.pos[0] - 1, self.pos[1])
                elif direction == 'Down':
                    lane_change_step = (self.pos[0] + 1, self.pos[1])
                elif direction == 'Left':
                    lane_change_step = (self.pos[0], self.pos[1] - 1)
                elif direction == 'Right':
                    lane_change_step = (self.pos[0], self.pos[1] + 1)

                if self.model.valid_position(*lane_change_step):
                    self.recalculate_path(start=lane_change_step)
                    next_step = lane_change_step
                else:
                    next_step = self.pos

    def recalculate_path(self, start=None, destination=None):
            # Recalculate the path from the current position to the destination
            if start:
                self.start = start
            if destination:
                self.destination = destination

            # Ensure that the car uses its own graph for recalculating the path
            try:
                self.path = nx.astar_path(self.graph, self.start, self.destination, heuristic)
                print(f"Car {self.unique_id} recalculated path from {self.start} to {self.destination}")
            except nx.NetworkXNoPath:
                print(f"No path could be recalculated for {self.unique_id} from {self.start} to {self.destination}")
                self.path = []

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
