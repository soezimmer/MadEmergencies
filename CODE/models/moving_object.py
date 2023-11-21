import threading
import time
import osmnx as ox

class MovingObject(threading.Thread):
    def __init__(self, id, graph, start_node, route=None):
        super().__init__()
        self.id = id
        self.graph = graph
        self.current_node = start_node
        self.lock = threading.Lock() # Lock to prevent multiple threads from accessing the same object
        self.target_node = None  # The destination node
        self.route = route if route is not None else []  # The path to follow
        self.route_index = 0  # Which step we are at in the route
        self.scatter = None  # Reference to the matplotlib scatter object
        self.position = None  # Position for the animation (x, y coordinates)
        

    # Method to calculate the path from the current_node to the target_node
    def set_route(self, target_node, weight='length'):
        self.target_node = target_node
        self.route = ox.shortest_path(self.graph, self.current_node, self.target_node, weight=weight)
        self.route_index = 0
        
    def move(self):
        while self.route_index < len(self.route):
            with self.lock:
                self.current_node = self.route[self.route_index]
                self.route_index += 1
            print(f"{self.id} moved from {self.route[self.route_index - 1]} to {self.current_node}")
            time.sleep(0.2)