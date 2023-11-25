from models.moving_object import MovingObject
from models.incident import Incident
import time
import logging
from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def update(self, incident):
        pass


class EmergencyVehicle(MovingObject, Observer):
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
        with self.lock:
            self.available = False
        self.set_route(self.incident.location)
        self.at_home_location = False

        # Move to the incident location
        while self.move():
            time.sleep(self.determine_sleep_time())
            with self.lock:
                if self.incident is None or self.incident.resolved:  # Added check for incident resolution
                    self.return_to_station()
                    return  # Exit the method if there's no incident or it's resolved.

        # Attend to the incident
        while not self.incident.resolved:
            with self.incident.lock:
                self.incident.severity -= 3  # Assume this helps resolve the incident
            time.sleep(1)

        # After resolving the incident, or if the incident is resolved by someone else,
        # return to the station.
        self.return_to_station()

    def update(self, incident):
        with self.lock:
            if self.incident and self.incident.id == incident.id and self.vehicle_type in ["Fire-Truck", "Ambulance"]:
                if incident.resolved:
                    self.stop_current_action()
                    self.return_to_station()
            elif self.available and not self.incident:
                self.incident = incident
                self.attend_incident()
    def stop_current_action(self):
        self.route = []
        self.target_node = None

    def return_to_station(self):
        #logging.info(f"{self.vehicle_type} {self.id} is returning to station")
        self.set_route(self.home_location)
        self.at_home_location = False
        while self.move() and not self.incident:
            time.sleep(0.1)
        #logging.info(f"{self.vehicle_type} {self.id} returned to station")
        self.at_home_location = True
        self.available = True
        self.incident = None  # Clearing the incident after returning to the station

    def run(self):
        while not self.done:
            if self.incident and not self.available:
                self.attend_incident()
                # Wait to be available again
                while not self.available:
                    time.sleep(0.1)
            time.sleep(0.1)