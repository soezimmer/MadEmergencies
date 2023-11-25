import threading
from queue import PriorityQueue
import time
import random
from models.incident import Incident
from utils.constants import INCIDENTS
import logging

class EmergencyResponseCenter(threading.Thread):
    _instance = None

    @classmethod
    def getInstance(cls, firetrucks=None, police_cars=None, ambulances=None):
        if cls._instance is None:
            cls._instance = cls(firetrucks, police_cars, ambulances)
        return cls._instance

    def __init__(self, firetrucks, police_cars, ambulances, city):
        if self._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super().__init__()
            self.incident_queue = PriorityQueue()
            self.firetrucks = firetrucks
            self.police_cars = police_cars
            self.ambulances = ambulances
            self.incident_id_counter = 0
            self.active_incidents = {}
            self.resolved_incidents = {}
            self.logged_incidents = {}
            self.locks = {
                            "active_incidents": threading.RLock(),
                            "resolved_incidents": threading.RLock(),
                            "logged_incidents": threading.RLock(),
                            "incident_queue": threading.RLock()
                        }
            self._instance = self
            self.city = city
    
    def run(self):
        logging.info("Emergency Response Center activated")
        while self.city.citizens == []:
            time.sleep(0.2)
        self.queue_listener()


    def queue_listener(self):
        while self.city.citizens != [] or not self.active_incidents == {}:
            try:
                if not self.incident_queue.empty():
                    #logging.info(f"The queue is: {self.incident_queue.queue}")
                    #logging.info(f"The active incidents are: {self.active_incidents}")
                    with self.locks['incident_queue']:
                        priority, incident_id = self.incident_queue.get()
                    with self.locks['active_incidents'] and self.locks['logged_incidents']:
                        incident = self.active_incidents[incident_id] if incident_id in self.active_incidents else self.logged_incidents[incident_id]
                    #logging.info(f"Dispatching incident {incident.id} with priority {priority}")
                    self.dispatch_vehicles(incident, priority)
            except Exception as e:
                logging.error(f"There was an ERROR: {e}")

            with self.locks['active_incidents']:
                incidents_to_remove = []
                for incident_id, incident in self.active_incidents.items():
                    if incident.resolved:
                        incidents_to_remove.append(incident_id)
                        self.resolved_incidents[incident_id] = incident
                        #logging.info(f"Resolved incident {incident_id} and removed it from active incidents")
                # Remove the resolved incidents from active_incidents
                for incident_id in incidents_to_remove:
                    self.active_incidents.pop(incident_id)
                    with self.locks['incident_queue']:
                        if (priority, incident_id) in self.incident_queue.queue:
                            self.incident_queue.queue.remove((priority, incident_id))
                            #logging.info(f"Removed incident {incident_id} from incident queue as it is resolved")

            self.update_priorities()
            time.sleep(0.1)
        
        logging.info("All citizens are done, shutting down Emergency Response Center")
        self.city.shutdown()


    def update_priorities(self):
        with self.locks['incident_queue']:
            updated_incidents = []
            while not self.incident_queue.empty():
                priority, incident_id = self.incident_queue.get()
                if priority > 0:
                    priority = round(priority - 0.1, 2) 
                updated_incidents.append((priority, incident_id))  # Increase priority

            # Put the updated incidents back in the queue
            for incident in updated_incidents:
                self.incident_queue.put(incident)


    def report_incident(self, incident_location):
        incidents = INCIDENTS
        incident_types = list(incidents.keys())
        probabilities = [incidents[incident]['probability'] for incident in incident_types]

        incident_type = random.choices(incident_types, weights=probabilities, k=1)[0]
        self.incident_id_counter += 1
        id = self.incident_id_counter
        reported = time.time()
        incident = Incident(id, incident_location, incident_type, reported, incidents[incident_type]['severity'])
        incident_priority = self.determine_incident_priority(incident_type, incident)
        logging.info(f"New incident {incident.id}  reported at {incident_location} with type {incident_type}, severity {incident.severity}, and priority {incident_priority} \n Firetrucks needed: {incident.vehicles_needed[1]} \n Police cars needed: {incident.vehicles_needed[0]} \n Ambulances needed: {incident.vehicles_needed[2]}")

        with self.locks["logged_incidents"]:
            self.logged_incidents[incident.id] = incident
        with self.locks["incident_queue"]:
            self.incident_queue.put((incident_priority, incident.id))

            
    def determine_incident_priority(self, incident_type, incident):
        incident_details = INCIDENTS.get(incident_type, {})

        # Get severity and required resources for the incident
        severity = incident_details.get('severity', 0)
        required_police_cars = incident_details.get('required_police_cars', 0)
        required_firetrucks = incident_details.get('required_firetrucks', 0)
        required_ambulances = incident_details.get('required_ambulances', 0)
        incident.vehicles_needed = [required_police_cars, required_firetrucks, required_ambulances]

        # Calculate the number of available vehicles
        available_police_cars = sum(1 for car in self.police_cars if car.available)
        available_firetrucks = sum(1 for truck in self.firetrucks if truck.available)
        available_ambulances = sum(1 for ambulance in self.ambulances if ambulance.available)

        # Adjust priority based on availability of resources
        # If fewer vehicles are available than required, the priority increases (yes its not in the moment of deployment, but it is a good approximation)
        priority_adjustment = 0
        if available_police_cars < required_police_cars:
            priority_adjustment -= (required_police_cars - available_police_cars) * 10
        if available_firetrucks < required_firetrucks:
            priority_adjustment -= (required_firetrucks - available_firetrucks) * 10
        if available_ambulances < required_ambulances:
            priority_adjustment -= (required_ambulances - available_ambulances) * 10

        # Final priority calculation
        priority = 100 - severity + priority_adjustment
        return priority

    def dispatch_vehicles(self, incident, priority):
        # determine the number of vehicles needed for the incident
        needed_police_cars = incident.vehicles_needed[0]
        needed_firetrucks = incident.vehicles_needed[1]
        needed_ambulances = incident.vehicles_needed[2]

        # Attempt to dispatch vehicles
        dispatched_police_cars = self.dispatch_specific_vehicle(self.police_cars, needed_police_cars, incident)
        dispatched_firetrucks = self.dispatch_specific_vehicle(self.firetrucks, needed_firetrucks, incident)
        dispatched_ambulances = self.dispatch_specific_vehicle(self.ambulances, needed_ambulances, incident)

        incident.vehicles_dispatched = [dispatched_police_cars, dispatched_firetrucks, dispatched_ambulances]
        incident.vehicles_needed = [needed_police_cars - dispatched_police_cars, needed_firetrucks - dispatched_firetrucks, needed_ambulances - dispatched_ambulances]

        if incident.vehicles_needed == [0, 0, 0]:
            # Option 1: All cars dispatched
            incident.status = "dispatched"
            #logging.info(f"All required vehicles dispatched to incident {incident.id}")
            with self.locks['logged_incidents']:
                self.logged_incidents[incident.id] = incident
            with self.locks['active_incidents']:
                self.active_incidents[incident.id] = incident
        elif incident.vehicles_dispatched != [0, 0, 0]:
            # Option 2: Not enough cars dispatched
            incident.status = "more vehicles needed"
            priority = priority - 0.3 if priority > 0 else priority
            with self.locks['incident_queue']:
                self.incident_queue.put((priority, incident.id))
            with self.locks['active_incidents']:
                self.active_incidents[incident.id] = incident
            #logging.info(f"Re-queued incident {incident.id} with updated priority {priority}")
        else:
            # Option 3: No cars dispatched
            incident.status = "no vehicles available"
            priority = priority - 5 if priority > 0 else priority
            with self.locks['incident_queue']:
                self.incident_queue.put((priority, incident.id))
            #logging.info(f"Re-queued incident {incident.id} with significantly increased priority {priority}")
        

    def dispatch_specific_vehicle(self, vehicles, needed, incident):
        dispatched_count = 0
        for vehicle in vehicles:
            with vehicle.lock:
                if vehicle.available and dispatched_count < needed:
                    vehicle.incident = incident
                    vehicle.available = False
                    dispatched_count += 1
        return dispatched_count
