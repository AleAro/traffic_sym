import networkx as nx
import json
import random
import matplotlib.pyplot as plt
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import Car, Road, Traffic_Light, Obstacle, Destination  # Assuming these are defined in 'agent.py'

class CityModel(Model):
    def __init__(self, N, map_file, map_dict_file):
        self.dataDictionary = json.load(open(map_dict_file))
        self.traffic_lights = []
        self.destinations = []
        self.G = nx.DiGraph()  # Graph representing the city

        with open(map_file) as baseFile:
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
        if col in ["v", "^", ">", "<", "u", "g", "h", "k"]:
            agent = Road(f"r_{r*self.width+c}", self, self.dataDictionary[col])
            self.grid.place_agent(agent, (c, self.height - r - 1))
            self.G.add_node((c, self.height - r - 1), type='road')

        elif col in ["S", "s"]:
            agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(self.dataDictionary[col]))
            self.grid.place_agent(agent, (c, self.height - r - 1))
            self.schedule.add(agent)
            self.traffic_lights.append(agent)
            self.G.add_node((c, self.height - r - 1), type='traffic_light')

        elif col == "#":
            agent = Obstacle(f"ob_{r*self.width+c}", self)
            self.grid.place_agent(agent, (c, self.height - r - 1))

        elif col == "D":
            agent = Destination(f"d_{r*self.width+c}", self)
            self.grid.place_agent(agent, (c, self.height - r - 1))
            self.destinations.append((c, self.height - r - 1))
            self.G.add_node((c, self.height - r - 1), type='destination')

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

    def is_road(self, x, y):
        contents = self.grid.get_cell_list_contents((x, y))
        return any(isinstance(content, Road) for content in contents)

    def is_destination(self, x, y):
        contents = self.grid.get_cell_list_contents((x, y))
        return any(isinstance(content, Destination) for content in contents)

    def add_edges(self):
        directions = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
        for x in range(self.width):
            for y in range(self.height):
                contents = self.grid.get_cell_list_contents((x, y))
                if self.is_destination(x, y):
                    for direction in directions.values():
                        dx, dy = direction
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if self.is_road(nx, ny):
                                weight = self.calculate_edge_weight(x, y, nx, ny)
                                self.G.add_edge((nx, ny), (x, y), weight=weight)
                if self.is_road(x, y):
                    road = next(c for c in contents if isinstance(c, Road))
                    road_directions = road.direction if isinstance(road.direction, list) else [road.direction]
                    for direction in (road_directions if isinstance(road_directions, list) else [road_directions]):
                        dx, dy = directions[direction]
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if self.is_road(nx, ny) or self.is_traffic_light(nx, ny):
                                weight = self.calculate_edge_weight(x, y, nx, ny)
                                self.G.add_edge((x, y), (nx, ny), weight=weight)

    def calculate_edge_weight(self, x, y, nx, ny):
        base_weight = 1
        next_contents = self.grid.get_cell_list_contents((nx, ny))
        if any(isinstance(c, Traffic_Light) and c.state == "on" for c in next_contents):
            return base_weight * 10
        return base_weight

    def visualize_graph(self):
        pos = {node: (node[0], - node[1]) for node in self.G.nodes()}
        road_nodes = [node for node, attr in self.G.nodes(data=True) if attr.get('type') == 'road']
        traffic_light_nodes = [node for node, attr in self.G.nodes(data=True) if attr.get('type') == 'traffic_light']
        destination_nodes = [node for node, attr in self.G.nodes(data=True) if attr.get('type') == 'destination']

        plt.figure(figsize=(12, 12))
        nx.draw_networkx_nodes(self.G, pos, nodelist=road_nodes, node_color="lightblue", node_size=50)
        nx.draw_networkx_nodes(self.G, pos, nodelist=traffic_light_nodes, node_color="red", node_size=100)
        nx.draw_networkx_nodes(self.G, pos, nodelist=destination_nodes, node_color="green", node_size=100)
        nx.draw_networkx_edges(self.G, pos, arrowstyle='->', arrowsize=15, edge_color="gray")
        plt.axis('off')
        plt.show()

    def step(self):
        self.schedule.step()

    def update_graph_edge_weights(self, tl):
        for edge in self.G.edges(tl.pos):
            self.G.edges[edge]['weight'] = self.calculate_edge_weight(*edge)

    def recalculate_paths(self):
        for agent in self.schedule.agents:
            if isinstance(agent, Car):
                agent.recalculate_path()  # Assuming each car has a method to recalculate its path

    def is_traffic_light(self, x, y):
        contents = self.grid.get_cell_list_contents((x, y))
        return any(isinstance(content, Traffic_Light) for content in contents)


if __name__ == "__main__":
    model = CityModel(N=1, map_file='city_files/2022_base.txt', map_dict_file='city_files/mapDictionary.json')
    model.add_edges()
    model.visualize_graph()
