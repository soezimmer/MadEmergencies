from models.moving_object import MovingObject
import random
import time 
import logging
from utils.constants import NINCIDENTS_PER_CITIZEN, CITIZEN_WAIT_TIME, CITIZEN_REPORT_PROBABILITY

class Citizen(MovingObject):
    def __init__(self, id, graph, emergency_center, city):
        start_node = random.choice(list(graph.nodes()))
        super().__init__(id, graph, start_node)
        self.num_incidents_reported = 0
        self.emergency_center = emergency_center
        self.city = city

    def report_incident(self):
        incident_location = self.current_node
        self.emergency_center.report_incident(incident_location)
        self.num_incidents_reported += 1
        self.current_node = random.choice(list(self.graph.nodes()))

    def run(self):
        time.sleep(random.randint(CITIZEN_WAIT_TIME[0], CITIZEN_WAIT_TIME[1]))
        while self.num_incidents_reported < NINCIDENTS_PER_CITIZEN:
            if random.random() < CITIZEN_REPORT_PROBABILITY:
                self.report_incident()
            time.sleep(random.random() * 10)
        logging.info(f"Citizen {self.id} reported {self.num_incidents_reported} incidents and is done")
        self.city.citizens.remove(self)
