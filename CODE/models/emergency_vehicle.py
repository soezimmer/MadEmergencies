from models.moving_object import MovingObject
from models.incident import Incident
import time
import logging


class EmergencyVehicle(MovingObject):
    def __init__(self, id, graph, vehicle_type, home_location):
        super().__init__(id, graph, home_location)
        self.id = id
        self.incident = None
        self.vehicle_type = vehicle_type
        self.available = True
        self.at_home_location = True
        self.home_location = home_location

    def attend_incident(self, incident):
        self.available = False
        logging.info(f"{self.vehicle_type} {self.id} is attending incident {incident.id}")
        self.incident = incident
        self.set_route(incident.location)
        super().move()
        logging.info(f"{self.vehicle_type} {self.id} now is at {self.current_node} and the incident is at {incident.location}")
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
        super().move()
        print(f"{self.vehicle_type} {self.id} returned to station")
        self.at_home_location = True
        self.available = True
        self.incident = None

    def run(self):
        while True:
            if self.incident and not self.available:
                self.attend_incident(self.incident)
                # Wait to be available again
                while not self.available:
                    time.sleep(0.1)
            time.sleep(0.1)