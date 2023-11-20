from models.moving_object import MovingObject
from models.incident import Incident
import time


class EmergencyVehicle(MovingObject):
    def __init__(self, id, graph, vehicle_type, home_location):
        super().__init__(id, graph, home_location)  # Assuming starting location is the first incident's location
        self.id = id
        self.incident = None
        self.vehicle_type = vehicle_type
        self.available = True
        self.at_home_location = True
        self.home_location = None

    def attend_incident(self, incident):
        self.set_route(incident.location)
        super().run()
        print(f"{self.vehicle_type} {self.id} arrived at incident at {incident.location}")
        while not incident.resolved:
            with incident.lock:
                incident.hardness -= 3
            time.sleep(1)
            if incident.hardness <= 0:
                with incident.lock:
                    incident.resolved = True    
                print(f"{self.vehicle_type} {self.id} resolved incident at {incident.location}")
        self.set_route(self.home_location)
        super().run()
        print(f"{self.vehicle_type} {self.id} returned to station")
        self.at_home_location = True
        self.available = True