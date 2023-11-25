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
        self.done = False

    def attend_incident(self):
        self.available = False
        #logging.info(f"{self.vehicle_type} {self.id} is attending incident {self.incident.id}")
        self.set_route(self.incident.location)
        self.at_home_location = False
        while self.move():
            time.sleep(0.1)
        #logging.info(f"{self.vehicle_type} {self.id} arrived at incident at {self.incident.location}")
        while not self.incident.resolved:
            with self.incident.lock:
                self.incident.severity -= 3
            time.sleep(1)
            if self.incident.severity <= 0:
                with self.incident.lock:
                    self.incident.resolved = True
                    self.incident.status = "resolved"    
                #logging.info(f"{self.vehicle_type} {self.id} resolved incident at {self.incident.location}")
        self.target_node = self.home_location
        self.route = self.set_route(self.home_location)
        while self.move():
            time.sleep(0.1)
        #logging.info(f"{self.vehicle_type} {self.id} returned to station")
        self.at_home_location = True
        self.available = True
        self.incident = None

    def run(self):
        while not self.done:
            if self.incident and not self.available:
                self.attend_incident()
                # Wait to be available again
                while not self.available:
                    time.sleep(0.1)
            time.sleep(0.1)