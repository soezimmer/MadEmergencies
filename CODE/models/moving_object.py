import threading
import time
import osmnx as ox
import logging

class MovingObject(threading.Thread):
    """
    Represents a moving object in a graph.

    Attributes:
        id (int): The ID of the moving object.
        graph (OSMnx Graph): The graph representing the environment.
        start_node (int): The starting node of the moving object.
        route (list): The route of the moving object.
        route_index (int): The index of the current step in the route.
        scatter (object): The reference to the matplotlib scatter object.
        position (tuple): The position of the moving object (x, y coordinates).
    """

    def __init__(self, id, graph, start_node, route=[]):
        """
        Initializes a MovingObject instance.

        Args:
            id (int): The ID of the moving object.
            graph (networkx.Graph): The graph representing the environment.
            start_node (int): The starting node of the moving object.
            route (list, optional): The route of the moving object. Defaults to an empty list.
        """
        super().__init__()
        self.id = id
        self.graph = graph
        self.current_node = start_node
        self.lock = threading.Lock()  # Lock to prevent multiple threads from accessing the same object
        self.target_node = None  # The destination node
        self.route = route
        self.route_index = 0  # Which step we are at in the route
        self.scatter = None  # Reference to the matplotlib scatter object
        self.position = None  # Position for the animation (x, y coordinates)

    def set_route(self, target_node, weight='length'):
        """
        Sets the route for the moving object from the current node to the target node.

        Args:
            target_node (int): The target node.
            weight (str, optional): The weight attribute to use for calculating the route. Defaults to 'length'.

        Returns:
            list: The calculated route.
        """
        self.target_node = target_node
        self.route = ox.shortest_path(self.graph, self.current_node, self.target_node, weight=weight)
        self.route_index = 0
        return self.route

    def move(self):
        """
        Moves the moving object to the next step in the route.

        Returns:
            bool: True if the moving object successfully moved to the next step, False otherwise.
        """
        if self.route and self.route_index < len(self.route):
            self.current_node = self.route[self.route_index]
            self.route_index += 1
            self.position = (self.graph.nodes[self.current_node]['x'], self.graph.nodes[self.current_node]['y'])
            return True
        else:
            self.route = []
            self.route_index = 0
            return False

    def determine_sleep_time(self):
        """
        Determines the sleep time for the moving object based on the length of the edge.

        Returns:
            float: The sleep time in seconds.
        """
        if self.route_index == 0 or self.route_index == len(self.route):
            return 0.1
        time_to_sleep = self.graph.edges[self.route[self.route_index - 1], self.route[self.route_index], 0]['length'] / 1000
        return time_to_sleep