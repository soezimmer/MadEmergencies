from .moving_object import MovingObject
from .incident import Incident
import random

class Citizen(MovingObject):
    def __init__(self, id, graph, emergency_center):
        start_node = random.choice(list(graph.nodes()))
        super().__init__(id, graph, start_node)
        self.num_incidents_reported = 0
        self.emergency_center = emergency_center

    def report_incident(self):
        incident_type = random.choice(["fire", "crime"])
        incident_location = self.current_node
        secondary_help = incident_type if random.random() < 0.1 else None
        print(f"Citizen {self.id} has reported an {incident_type} at {incident_location}")

        # Create a new Incident object with a unique ID, location, type, and whether secondary help is needed
        incident_id = f"{incident_type}_{self.id}_{self.num_incidents_reported}"
        incident_class = Incident(incident_id, incident_location, incident_type, secondary_help)
        # Report the incident to the Emergency Response Center
        self.emergency_center.report_incident(incident_class)
        self.num_incidents_reported += 1

    def run(self):
        while self.num_incidents_reported < 3:
            if random.random() < 0.2:
                self.report_incident()
            time.sleep(10)