#agent.py
import networkx as nx
from mesa import Agent

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)  # Manhattan distance

class Car(Agent):
    """
    Car agent that can find paths using A* algorithm.
    """
    def __init__(self, unique_id, model, start, destination):
        super().__init__(unique_id, model)
        self.start = start
        self.destination = destination
        self.path = []

    def find_path(self):
        G = self.model.get_graph()  
        try:
            self.path = nx.astar_path(G, self.start, self.destination, heuristic)
        except nx.NetworkXNoPath:
            print(f"No path found for {self.unique_id} from {self.start} to {self.destination}")
            self.path = []


    def move(self):
        if self.path:
            next_step = self.path.pop(0)
            self.model.grid.move_agent(self, next_step)
            # Check if destination is reached
            if not self.path:  # Path is empty, meaning the destination is reached
                print(f"Car {self.unique_id} has reached its destination.")
                # Handle arrival, such as stopping the car or removing it

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
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state

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
