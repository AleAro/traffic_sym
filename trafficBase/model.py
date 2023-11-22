from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import Car, Road, Traffic_Light, Obstacle, Destination
import json
import random
import networkx as nx
import matplotlib.pyplot as plt

class CityModel(Model):
    """ 
    Creates a model based on a city map with one-way streets.
    Args:
        N: Number of agents in the simulation (assuming 1 for a single car)
    """
    def __init__(self, N):
        self.dataDictionary = json.load(open("city_files/mapDictionary.json"))
        self.traffic_lights = []
        self.destinations = []

        with open('city_files/2022_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0].strip())
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus=False)
            self.schedule = RandomActivation(self)

            for r, row in enumerate(lines):
                for c, col in enumerate(row.strip()):
                    self.process_cell(r, c, col)

        self.num_agents = N
        self.running = True
        self.place_single_car()

    def process_cell(self, r, c, col):
        if col in ["v", "^", ">", "<"]:
            agent = Road(f"r_{r*self.width+c}", self, self.dataDictionary[col])
            self.grid.place_agent(agent, (c, self.height - r - 1))

        elif col in ["S", "s"]:
            agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(self.dataDictionary[col]))
            self.grid.place_agent(agent, (c, self.height - r - 1))
            self.schedule.add(agent)
            self.traffic_lights.append(agent)

        elif col == "#":
            agent = Obstacle(f"ob_{r*self.width+c}", self)
            self.grid.place_agent(agent, (c, self.height - r - 1))

        elif col == "D":
            agent = Destination(f"d_{r*self.width+c}", self)
            self.grid.place_agent(agent, (c, self.height - r - 1))
            self.destinations.append((c, self.height - r - 1))

    def get_edge_cells(self):
        cells = set()
        for i in range(self.width):
            cells.add((i, 0))
            cells.add((i, self.height-1))
        for i in range(1, self.height-1):
            cells.add((0, i))
            cells.add((self.width-1, i))
        return list(cells)

    def place_single_car(self):
        corners = [(0, 0), (self.width - 1, 0), (0, self.height - 1), (self.width - 1, self.height - 1)]
        suitable_corners = [corner for corner in corners if self.is_suitable_for_car(corner)]

        if suitable_corners and self.destinations:
            start_pos = random.choice(suitable_corners)
            destination = random.choice(self.destinations)
            car = Car("car_0", self, start_pos, destination)
            self.grid.place_agent(car, start_pos)

    def is_suitable_for_car(self, cell):
        cell_contents = self.grid.get_cell_list_contents(cell)
        return any(isinstance(agent, Road) for agent in cell_contents) and not any(isinstance(agent, (Obstacle, Traffic_Light, Destination)) for agent in cell_contents)

    def get_graph(self):
        G = nx.DiGraph()
        for x in range(self.width):
            for y in range(self.height):
                if self.is_road(x, y):
                    G.add_node((x, y))
                    self.add_edges(G, x, y)
        return G

    def is_road(self, x, y):
        contents = self.grid.get_cell_list_contents((x, y))
        return any(isinstance(content, Road) for content in contents)

    def add_edges(self, G, x, y):
        road = next(content for content in self.grid.get_cell_list_contents((x, y)) if isinstance(content, Road))
        directions = {'Up': (0, -1), 'Down': (0, 1), 'Left': (-1, 0), 'Right': (1, 0)}
        dx, dy = directions[road.direction]
        nx, ny = x + dx, y + dy
        if 0 <= nx < self.width and 0 <= ny < self.height and self.is_road(nx, ny):
            G.add_edge((x, y), (nx, ny))

    def step(self):
        self.schedule.step()

    def visualize_graph(self):
        G = self.get_graph()
        pos = {node: (node[0], -node[1]) for node in G.nodes()} 
        nx.draw(G, pos, node_color="lightblue", with_labels=True, node_size=50)
        plt.show()

    

if __name__ == "__main__":
        model = CityModel(N=1)
        model.visualize_graph() 