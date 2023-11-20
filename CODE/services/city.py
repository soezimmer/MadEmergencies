import osmnx as ox
import threading
from models.citizen import Citizen
from models.emergency_vehicle import EmergencyVehicle
from utils.constants import *
from services.emergency_response_center import EmergencyResponseCenter


class City:
    def __init__(self, citizens_number):
        self.citizens_number = citizens_number
        self.citizens = []
        self.firetrucks_onsite = []
        self.police_onsite = []
        self.ambulances_onsite = []
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
        self.firetrucks_onsite = [EmergencyVehicle(i, self.graph, "Fire-Truck", FIRE_STATION) for i in range(FIRE_TRUCKS)]
        self.police_onsite = [EmergencyVehicle(i, self.graph, "Police-Car", POLICE_STATION) for i in range(POLICE_CARS)]
        self.ambulances_onsite = [EmergencyVehicle(i, self.graph, "Ambulance", AMBULANCE_STATION) for i in range(AMBULANCES)]
        
        # Now you can pass these lists to the EmergencyResponseCenter
        self.emergency_response = EmergencyResponseCenter(self.firetrucks_onsite, self.police_onsite, self.ambulances_onsite)
        self.emergency_response.start()

        # Start the firetrucks and police cars threads
        for firetruck in self.firetrucks_onsite:
            firetruck.start()

        for police_car in self.police_onsite:
            police_car.start()

        for ambulance in self.ambulances_onsite:
            ambulance.start()

    def start_services(self):
        self.deploy_emergency_services()
        self.deploy_citizens()