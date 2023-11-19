import threading
from queue import Queue
import time
import random
from models.incident import Incident

class EmergencyResponseCenter(threading.Thread):
    _instance = None

    @classmethod
    def getInstance(cls, firetrucks=None, police_cars=None):
        if cls._instance is None:
            cls._instance = cls(firetrucks, police_cars)
        return cls._instance

    def __init__(self, firetrucks, police_cars):
        if self._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super().__init__()
            self.incident_queue = Queue()
            self.firetrucks = firetrucks
            self.police_cars = police_cars
            self.active_incidents = {}
            self.lock = threading.RLock()
            self.dispatch_event = threading.Event()
            print("Emergency Response Center activated")
            self._instance = self
    
    def report_incident(self, incident):
        with self.lock:
            self.active_incidents[incident.id] = incident
            self.incident_queue.put(incident.id)
            self.dispatch_event.set()  # Signal to start dispatching

    def run(self):
        while not end.is_set():
            self.dispatch_event.wait()  # Wait for an incident to be reported
            while not self.incident_queue.empty():
                incident_id = self.incident_queue.get()
                with self.lock:
                    incident = self.active_incidents[incident_id]
                if incident:
                    self.dispatch_vehicles(incident)
            self.dispatch_event.clear()

    def handle_incident(self, incident):
        if incident.incident_type == "crime":
            dispatched = self.dispatch_vehicles(self.police_cars, incident, 
                                                self.determine_number_of_vehicles_needed(incident.incident_type), 
                                                self.police_incidents_lock)
        elif incident.incident_type == "fire":
            dispatched = self.dispatch_vehicles(self.firetrucks, incident, 
                                                self.determine_number_of_vehicles_needed(incident.incident_type), 
                                                self.fire_incidents_lock)

        # Monitor incident status
        while not incident.resolved:
            with self.incident_queue_lock:
                if incident.missing_resources and any(v.available and v.at_home_location for v in self.police_cars + self.firetrucks):
                    # Dispatch additional vehicles as they become available
                    self.dispatch_additional_vehicles(incident)
            time.sleep(1)  # Check the status periodically

        # Once resolved, reset vehicle status
        self.reset_vehicle_status(incident)

    def dispatch_vehicles(self, incident):
        # Determine the type of vehicles needed based on the incident type
        vehicles = self.police_cars if incident.incident_type == "crime" else self.firetrucks
        num_vehicles_needed = self.determine_number_of_vehicles_needed(incident.incident_type)
        incident_threads = []
        with self.lock:
            available_vehicles = [v for v in vehicles if v.available]

        for i in range(min(num_vehicles_needed, len(available_vehicles))):
            vehicle = available_vehicles[i]
            with vehicle.lock:
                vehicle.available = False  # Mark the vehicle as unavailable
                vehicle.at_home_location = False
                print(f"Dispatching {vehicle} to incident at {incident.location}")
                vehicle.set_route(incident.location)

            # Start attend_incident in a new thread to avoid blocking
            incident_thread = threading.Thread(target=vehicle.attend_incident, args=(incident,))
            incident_thread.start()
            time.sleep(0.2)  # Wait between dispatching vehicles

        
        for incident_thread in incident_threads:
             incident_thread.join()

        # Wait until incident status is set as resolved
        while not incident.resolved:
            time.sleep(1)

        # Pop the incident from the active incidents dictionary
        with self.lock:
            self.active_incidents.pop(incident.id)
    

    def dispatch_additional_vehicles(self, incident):
    # If the incident is not resolved and missing resources

        if not incident.resolved and incident.missing_resources > 0:
            # Determine the type of vehicles needed based on the incident type
            vehicles = self.police_cars if incident.incident_type == "crime" else self.firetrucks

            with self.police_incidents_lock if incident.incident_type == "crime" else self.fire_incidents_lock:
                # Filter available and at home vehicles
                available_vehicles = [v for v in vehicles if v.available and v.at_home_location]
                
                # Dispatch up to the number of missing resources
                for i in range(min(incident.missing_resources, len(available_vehicles))):
                    vehicle = available_vehicles[i]
                    vehicle.set_route(incident.location)
                    vehicle.available = False
                    vehicle.set_at_home_location(False)
                    vehicle.start()
                    incident.missing_resources -= 1  # Update missing resources

    def reset_vehicle_status(self, incident):
        # Identify the vehicles that were dispatched to this incident
        vehicles = self.police_cars if incident.incident_type == "crime" else self.firetrucks
        
        for vehicle in vehicles:
            # Reset the vehicle status if it was part of this incident
            if not vehicle.available and not vehicle.at_home_location:
                vehicle.available(True)
                vehicle.at_home_location(True)
                # Additional logic can be added here if vehicles need to take time to return to the station

    def determine_number_of_vehicles_needed(self, incident_type):
        return {
            "fire": random.randint(1, 1),  # Randomly choose between 1 and 3 firetrucks
            "crime": random.randint(1, 1)  # Randomly choose between 1 and 2 police cars
        }.get(incident_type, 1)

    def order_secondary_help(self):
        # Handle secondary help in a similar way to the primary help
        if self.to_sort.secondary_help == "fire":
            self.dispatch_vehicles(self.police_cars, self.to_sort, 1, self.police_incidents_lock)
        elif self.to_sort.secondary_help == "crime":
            self.dispatch_vehicles(self.firetrucks, self.to_sort, 1, self.fire_incidents_lock)
