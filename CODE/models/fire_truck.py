from models.moving_object import MovingObject
from models.incident import Incident
import time
from utils.constants import FIRE_STATION

class FireTruck(MovingObject):
    def __init__(self, id, fire_incidents, fire_incidents_lock, graph):
        start_node = FIRE_STATION  # Assuming firestation is defined
        super().__init__(id, graph, start_node)
        self.fire_incidents = fire_incidents
        self.fire_incidents_lock = fire_incidents_lock
        self.available = True
        self.at_home_location = True
        self.home_location = FIRE_STATION

    def attend_incident(self, incident):
        with incident.lock:
            incident.status = "attending"
            incident.resolved = False
            super().run()
            print(f"Firetruck {self.id} arrived at incident at {incident.location}")
            time.sleep(5)  # Simulate time to resolve incident
            incident.status = "resolved"
            incident.resolved = True
            print(f"Firetruck {self.id} resolved incident at {incident.location}")
            self.set_route(self.home_location)
            super().run()
            print(f"Firetruck {self.id} returned to station")
            self.at_home_location = True
            self.available = True