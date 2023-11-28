from models.moving_object import MovingObject
import random
import time 
import logging
from utils.constants import NINCIDENTS_PER_CITIZEN, CITIZEN_WAIT_TIME, CITIZEN_REPORT_PROBABILITY

class Citizen(MovingObject):
    def __init__(self, id, graph, emergency_center, city):
        """
        Initializes a Citizen object.

        Args:
            id (int): The unique identifier for the citizen.
            graph (OSMnx Graph): The graph representing the city's road network.
            emergency_center (EmergencyCenter): The emergency center responsible for handling incidents.
            city (City): The city object to which the citizen belongs.
        """
        start_node = random.choice(list(graph.nodes()))
        super().__init__(id, graph, start_node)
        self.num_incidents_reported = 0
        self.emergency_center = emergency_center
        self.city = city

    def report_incident(self):
        """
        Reports an incident to the emergency center.
        """
        incident_location = self.current_node
        self.emergency_center.report_incident(incident_location)
        self.num_incidents_reported += 1
        self.current_node = random.choice(list(self.graph.nodes()))

    def run(self):
        """
        Runs the citizen's behavior of reporting incidents.
        """
        time.sleep(random.randint(CITIZEN_WAIT_TIME[0], CITIZEN_WAIT_TIME[1]))
        while self.num_incidents_reported < NINCIDENTS_PER_CITIZEN:
            if random.random() < CITIZEN_REPORT_PROBABILITY:
                self.report_incident()
            time.sleep(random.random() * 10)
        logging.info(f"Citizen {self.id} reported {self.num_incidents_reported} incidents and is done")
        self.city.citizens.remove(self)
