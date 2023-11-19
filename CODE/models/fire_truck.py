from .moving_object import MovingObject
from .incident import Incident
import random
from services import constants

firestation = constants.FIRE_STATION

class FireTruck(MovingObject):
    def __init__(self, id, fire_incidents, fire_incidents_lock, graph):
        start_node = firestation  # Assuming firestation is defined
        super().__init__(id, graph, start_node)
        self.fire_incidents = fire_incidents
        self.fire_incidents_lock = fire_incidents_lock
        self.available = True
        self.at_home_location = True

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
            self.set_route(firestation)
            super().run()
            print(f"Firetruck {self.id} returned to station")
            self.at_home_location = True
            self.available = True