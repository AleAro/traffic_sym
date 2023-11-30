#model.py
import networkx as nx
import json
import random
import matplotlib.pyplot as plt
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import Car, Road, Traffic_Light, Obstacle, Destination  # Assuming these are defined in 'agent.py'

class CityModel(Model):
    def __init__(self, N):
        map_file = 'city_files/2023_base.txt'
        map_dict_file = 'city_files/mapDictionary.json'
        self.dataDictionary = json.load(open(map_dict_file))
        self.traffic_lights = []
        self.destinations = []
        self.G = nx.DiGraph()  # Graph representing the city
        self.car_id_counter = 0

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
        # Add code to place edges
        self.add_edges()

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
                    car_graph = self.generate_graph_for_car("car_" + str(self.car_id_counter))  # Use the counter for unique ID
                    car = Car("car_" + str(self.car_id_counter), self, start_pos, destination, car_graph)
                    self.grid.place_agent(car, start_pos)
                    self.schedule.add(car)
                    self.car_id_counter += 1  # Increment the counter after adding a car

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
        diagonal_directions = {
            'Up': [('Up', 'Right'), ('Up', 'Left')],
            'Down': [('Down', 'Right'), ('Down', 'Left')],
            'Left': [('Left', 'Up'), ('Left', 'Down')],
            'Right': [('Right', 'Up'), ('Right', 'Down')]
        }

        for x in range(self.width):
            for y in range(self.height):
                contents = self.grid.get_cell_list_contents((x, y))
                if self.is_destination(x, y):
                    # Add edges for destinations
                    self.add_destination_edges(x, y, directions)
                elif self.is_road(x, y):
                    # Add edges for roads, including diagonal edges
                    road = next((c for c in contents if isinstance(c, Road)), None)
                    if road:
                        self.add_road_edges(x, y, road, directions, diagonal_directions)
                elif self.is_traffic_light(x, y):
                    self.add_traffic_light_edges(x, y, directions)

    def add_road_edges(self, x, y, road, directions, diagonal_directions):
        road_directions = road.direction if isinstance(road.direction, list) else [road.direction]
        for direction in road_directions:
            dx, dy = directions[direction]
            nx, ny = x + dx, y + dy
            if self.valid_position(nx, ny) and not self.is_traffic_light(nx, ny):
                weight = self.calculate_edge_weight(x, y, nx, ny)
                self.G.add_edge((x, y), (nx, ny), weight=weight)
                # Add diagonal edges in the direction of the road
                if direction in diagonal_directions:
                    for diag in diagonal_directions[direction]:
                        ddx, ddy = (directions[diag[0]][0] + directions[diag[1]][0], directions[diag[0]][1] + directions[diag[1]][1])
                        nnx, nny = x + ddx, y + ddy
                        if self.valid_position(nnx, nny) and not self.is_traffic_light(nnx, nny):
                            self.G.add_edge((x, y), (nnx, nny), weight=weight * 3)

    def add_traffic_light_edges(self, x, y, directions):
        for dir_name, (dx, dy) in directions.items():
            adjacent_x, adjacent_y = x + dx, y + dy

            if self.valid_position(adjacent_x, adjacent_y) and self.is_road(adjacent_x, adjacent_y):
                adjacent_contents = self.grid.get_cell_list_contents((adjacent_x, adjacent_y))
                road = next((c for c in adjacent_contents if isinstance(c, Road)), None)
                if road:
                    if self.aligns_with_road_direction(road, x, y, adjacent_x, adjacent_y):
                        self.G.add_edge((adjacent_x, adjacent_y), (x, y), weight=self.calculate_edge_weight(adjacent_x, adjacent_y, x, y))
                    else:
                        self.G.add_edge((x, y), (adjacent_x, adjacent_y), weight=self.calculate_edge_weight(x, y, adjacent_x, adjacent_y))

    def aligns_with_road_direction(self, road, tl_x, tl_y, road_x, road_y):
        if road.direction == "Up" and road_y < tl_y:
            return True
        if road.direction == "Down" and road_y > tl_y:
            return True
        if road.direction == "Left" and road_x > tl_x:
            return True
        if road.direction == "Right" and road_x < tl_x:
            return True
        return False

    def add_destination_edges(self, x, y, directions):
        for direction in directions.values():
            dx, dy = direction
            nx, ny = x + dx, y + dy
            if self.valid_position(nx, ny) and self.is_road(nx, ny):
                weight = self.calculate_edge_weight(x, y, nx, ny)
                self.G.add_edge((nx, ny), (x, y), weight=weight)

    def valid_position(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and (self.is_road(x, y) or self.is_traffic_light(x, y) or self.is_destination(x, y))

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
        # Add edge weights
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=10)
        plt.axis('off')
        plt.show()

    def step(self):
        self.schedule.step()
        if self.schedule.steps % 5 == 1:
            self.place_single_car()

    def update_graph_edge_weights(self, agent):
        for edge in self.G.edges:
            start_node, end_node = edge
            start_x, start_y = start_node
            end_x, end_y = end_node
            self.G.edges[edge]['weight'] = self.calculate_edge_weight(start_x, start_y, end_x, end_y)

    def recalculate_paths(self):
        for agent in self.schedule.agents:
            if isinstance(agent, Car):
                agent.recalculate_path()

    def is_traffic_light(self, x, y):
        contents = self.grid.get_cell_list_contents((x, y))
        return any(isinstance(content, Traffic_Light) for content in contents)

    def get_agent_data(self):
        agent_data = []
        for agent in self.schedule.agents:
            if isinstance (agent, Car):
                agent_info = {
                    "id": agent.unique_id,
                    "x": agent.pos[0],
                    "y": agent.pos[1],
                }
                agent_data.append(agent_info)
        return agent_data

    def generate_graph_for_car(self, car_id):
        return self.G.copy()



if __name__ == "__main__":
    model = CityModel(N=1, map_file='city_files/2023_base.txt', map_dict_file='city_files/mapDictionary.json')
    model.add_edges()
    model.visualize_graph()
