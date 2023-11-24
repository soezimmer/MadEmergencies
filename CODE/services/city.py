import osmnx as ox
import threading
from models.citizen import Citizen
from models.emergency_vehicle import EmergencyVehicle
from utils.constants import *
from services.emergency_response_center import EmergencyResponseCenter
import time
import logging


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
            citizen = Citizen(i, self.graph, self.emergency_response, self)
            self.citizens.append(citizen)
            citizen.name = "Citizen " + str(citizen.id)
            citizen.start()


    def deploy_emergency_services(self):
        # First, initialize the lists for firetrucks and police cars
        self.firetrucks_onsite = [EmergencyVehicle(i, self.graph, "Fire-Truck", FIRE_STATION) for i in range(FIRE_TRUCKS)]
        self.police_onsite = [EmergencyVehicle(i, self.graph, "Police-Car", POLICE_STATION) for i in range(POLICE_CARS)]
        self.ambulances_onsite = [EmergencyVehicle(i, self.graph, "Ambulance", AMBULANCE_STATION) for i in range(AMBULANCES)]
        
        # Now you can pass these lists to the EmergencyResponseCenter
        self.emergency_response = EmergencyResponseCenter(self.firetrucks_onsite, self.police_onsite, self.ambulances_onsite, self)
        self.emergency_response.name = "Emergency Response Center"
        self.emergency_response.start()

        # Start the firetrucks and police cars threads
        for firetruck in self.firetrucks_onsite:
            firetruck.name = "Fire-Truck " + str(firetruck.id)
            firetruck.start()

        for police_car in self.police_onsite:
            police_car.name = "Police-Car " + str(police_car.id)
            police_car.start()

        for ambulance in self.ambulances_onsite:
            ambulance.name = "Ambulance " + str(ambulance.id)
            ambulance.start()

    def start_services(self):
        self.deploy_emergency_services()
        self.deploy_citizens()

    def shutdown(self):
        logging.info("CITY SHUTTING DOWN")
        time.sleep(5)
        # Join all threads once every vehicle is done with its job

        while self.emergency_response.active_incidents:
            logging.info(f"Waiting for {self.emergency_response.active_incidents} incidents to be resolved")
            time.sleep(0.1)
        
        logging.info("All incidents resolved, shutting down threads")

        while self.firetrucks_onsite or self.police_onsite or self.ambulances_onsite:

            for firetruck in self.firetrucks_onsite:
                firetruck.done = True
                firetruck.join()
                self.firetrucks_onsite.remove(firetruck)
            
            for police_car in self.police_onsite:
                police_car.done = True
                police_car.join()
                self.police_onsite.remove(police_car)
            
            for ambulance in self.ambulances_onsite:
                ambulance.done = True
                ambulance.join()
                self.ambulances_onsite.remove(ambulance)

        logging.info("All vehicles are shut down, shutting down Emergency Response Center")