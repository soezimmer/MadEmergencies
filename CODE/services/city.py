import osmnx as ox
import threading
from ..models import Citizen, FireTruck, PoliceCar
from ..utils.constants import NORTH, SOUTH, EAST, WEST
from ..services import EmergencyResponseCenter


class City:
    def __init__(self, citizens_number):
        self.citizens_number = citizens_number
        self.citizens = []
        self.firetrucks_onsite = []
        self.police_onsite = []
        self.emergency_response = None
        self.graph = ox.graph_from_bbox(NORTH, SOUTH, EAST, WEST, network_type='drive')
        self.fire_incidents = list()
        self.fire_incidents_lock = threading.Lock()
        self.police_incidents = list()
        self.police_incidents_lock = threading.Lock()

    def deploy_citizens(self):
        for i in range(self.citizens_number):
            self.citizens.append(Citizen(i, self.graph, self.emergency_response))
            self.citizens[i].start()

    def deploy_emergency_services(self):
        # First, initialize the lists for firetrucks and police cars
        self.firetrucks_onsite = [FireTruck(i, self.fire_incidents, self.fire_incidents_lock, self.graph) for i in range(5)]  
        self.police_onsite = [PoliceCar(i, self.police_incidents, self.police_incidents_lock, self.graph) for i in range(5)]  

        # Now you can pass these lists to the EmergencyResponseCenter
        self.emergency_response = EmergencyResponseCenter(self.firetrucks_onsite, self.police_onsite)
        self.emergency_response.start()

        # Start the firetrucks and police cars threads
        for firetruck in self.firetrucks_onsite:
            firetruck.start()

        for police_car in self.police_onsite:
            police_car.start()

    def start_services(self):
        self.deploy_emergency_services()
        self.deploy_citizens()