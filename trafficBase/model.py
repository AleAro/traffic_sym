#model.py
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json
import random

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, N):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []
        self.destinations = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open('city_files/2022_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.destinations.append((c, self.height - r - 1))  # Add this line

        self.num_agents = N
        self.running = True
    
    def get_edge_cells(self):
        '''Returns the cells at the edge of the grid, excluding duplicates.'''
        cells = set()
        for i in range(self.width):
            cells.add((i, 0))
            cells.add((i, self.height-1))
        for i in range(1, self.height-1):
            cells.add((0, i))
            cells.add((self.width-1, i))
        return list(cells)

    def place_cars_on_edges(self):
        '''Places the cars on the edge cells of the grid.'''
        edge_cells = self.get_edge_cells()
        suitable_edge_cells = [cell for cell in edge_cells if self.is_suitable_for_car(cell)]
        
        for i in range(self.num_agents):
            if suitable_edge_cells and self.destinations:
                start_pos = random.choice(suitable_edge_cells)
                suitable_edge_cells.remove(start_pos)
                destination = random.choice(self.destinations)
                car = Car(f"car_{i}", self, start_pos, destination)
                self.grid.place_agent(car, start_pos)

    def is_suitable_for_car(self, cell):
        '''Determines if a cell is suitable for placing a car.'''
        # Check if the cell is a road and not occupied by obstacles or other unsuitable agents
        cell_contents = self.grid.get_cell_list_contents(cell)
        for agent in cell_contents:
            if isinstance(agent, Obstacle) or isinstance(agent, Traffic_Light) or isinstance(agent, Destination):
                return False  # Cell is not suitable if it contains an obstacle, traffic light, or destination
        return True

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()