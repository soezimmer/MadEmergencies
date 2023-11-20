from models.moving_object import MovingObject
import random
import time 

class Citizen(MovingObject):
    def __init__(self, id, graph, emergency_center):
        start_node = random.choice(list(graph.nodes()))
        super().__init__(id, graph, start_node)
        self.num_incidents_reported = 0
        self.emergency_center = emergency_center

    def report_incident(self):
        incident_location = self.current_node
        self.emergency_center.report_incident(incident_location)
        self.num_incidents_reported += 1
        self.current_node = random.choice(list(self.graph.nodes()))

    def run(self):
        while self.num_incidents_reported < 3:
            if random.random() < 0.2:
                self.report_incident()
            time.sleep(10)