from models.moving_object import MovingObject
from models.incident import Incident
import time
import logging


class EmergencyVehicle(MovingObject):
    """
    Represents an emergency vehicle that can attend incidents.

    Attributes:
        id (int): The unique identifier of the emergency vehicle.
        graph (OSMnx Graph): The graph representing the road network.
        vehicle_type (str): The type of the emergency vehicle.
        home_location (int): The OSM home location of the emergency vehicle.
        incident (Incident): The incident that the emergency vehicle is attending.
        available (bool): Indicates whether the emergency vehicle is available or not.
        at_home_location (bool): Indicates whether the emergency vehicle is at its home location or not.
        done (bool): Indicates whether the emergency vehicle has completed its tasks or not (Simulation End Condition)
    """

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
        """
        Attends the incident by setting the route to the incident location and resolving the incident.

        This method moves the emergency vehicle to the incident location, reduces the severity of the incident,
        and resolves the incident when the severity reaches zero. Finally, it returns the emergency vehicle to its
        home location.
        """
        self.available = False
        self.set_route(self.incident.location)
        self.at_home_location = False
        while self.move():
            time.sleep(0.1)
        while not self.incident.resolved:
            with self.incident.lock:
                self.incident.severity -= 3
            time.sleep(1)
            if self.incident.severity <= 0:
                with self.incident.lock:
                    self.incident.resolved = True
                    self.incident.status = "resolved"
        self.target_node = self.home_location
        self.route = self.set_route(self.home_location)
        while self.move():
            time.sleep(0.1)
        self.at_home_location = True
        self.available = True
        self.incident = None

    def run(self):
        """
        Runs the emergency vehicle's tasks.

        This method continuously checks for incidents and attends them if the emergency vehicle is available.
        It waits until the emergency vehicle becomes available again before checking for new incidents.
        """
        while not self.done:
            if self.incident and not self.available:
                self.attend_incident()
                while not self.available:
                    time.sleep(0.1)
            time.sleep(0.1)