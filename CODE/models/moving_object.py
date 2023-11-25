import threading
import time
import osmnx as ox
import logging

class MovingObject(threading.Thread):
    def __init__(self, id, graph, start_node, route=[]):
        super().__init__()
        self.id = id
        self.graph = graph
        self.current_node = start_node
        self.lock = threading.Lock() # Lock to prevent multiple threads from accessing the same object
        self.target_node = None  # The destination node
        self.route = route
        self.route_index = 0  # Which step we are at in the route
        self.scatter = None  # Reference to the matplotlib scatter object
        self.position = None  # Position for the animation (x, y coordinates)
        

    # Method to calculate the path from the current_node to the target_node
    def set_route(self, target_node, weight='length'):
        self.target_node = target_node
        self.route = ox.shortest_path(self.graph, self.current_node, self.target_node, weight=weight)
        self.route_index = 0
        return self.route
        
    def move(self):
        if self.route and self.route_index < len(self.route):
            self.current_node = self.route[self.route_index]
            self.route_index += 1
            self.position = (self.graph.nodes[self.current_node]['x'], self.graph.nodes[self.current_node]['y'])
            return True
        else:
            return False  
        
    def determine_sleep_time(self):
        if self.route_index == 0 or self.route_index == len(self.route):
            return 0.1
        time_to_sleep = self.graph.edges[self.route[self.route_index - 1], self.route[self.route_index], 0]['length'] / 1000
        return time_to_sleep