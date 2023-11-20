import threading
from queue import PriorityQueue
import time
import random
from models.incident import Incident
from utils.constants import INCIDENTS

class EmergencyResponseCenter(threading.Thread):
    _instance = None

    @classmethod
    def getInstance(cls, firetrucks=None, police_cars=None, ambulances=None):
        if cls._instance is None:
            cls._instance = cls(firetrucks, police_cars, ambulances)
        return cls._instance

    def __init__(self, firetrucks, police_cars, ambulances):
        if self._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super().__init__()
            self.incident_queue = PriorityQueue()
            self.firetrucks = firetrucks
            self.police_cars = police_cars
            self.ambulances = ambulances
            self.active_incidents = {}
            self.lock = threading.RLock()
            print("Emergency Response Center activated")
            self._instance = self
    
    def run(self):
        self.queue_listener()


    def queue_listener(self):
        while True:
            if not self.incident_queue.empty():
                priority, incident_id = self.incident_queue.get()
                print(f"The queue is: {self.incident_queue.queue}")
                incident = self.active_incidents[incident_id]
                print(f"Dispatching incident {incident.id} with priority {priority}")
                if incident and incident.vehicles_needed != []:
                    threading.Thread(target=self.dispatch_vehicles, args=(incident,)).start()
            time.sleep(0.1)

    def update_priorities(self):
        with self.lock:
            # Temporarily store updated incidents to put them back in the queue
            updated_incidents = []
            while not self.incident_queue.empty():
                priority, incident_id = self.incident_queue.get()
                updated_incidents.append((priority + 1, incident_id))  # Increase priority

            # Put the updated incidents back in the queue
            for incident in updated_incidents:
                self.incident_queue.put(incident)


    def report_incident(self, incident_location):
        # Now I will set the type of incident
        incidents = INCIDENTS
        incident_types = list(incidents.keys())
        probabilities = [incidents[incident]['probability'] for incident in incident_types]

        incident_type = random.choices(incident_types, weights=probabilities, k=1)[0]
        id = len(self.active_incidents)
        reported = time.time()
        incident = Incident(id, incident_location, incident_type, reported, incidents[incident_type]['hardness'])
        incident_priority = self.determine_incident_priority(incident_type, incident)
        print(f"New incident reported at {incident_location} with type {incident_type} and priority {incident_priority}")

        with self.lock:
            self.active_incidents[id] = incident
            self.incident_queue.put((incident_priority, incident.id))

            
    def determine_incident_priority(self, incident_type, incident):
        incident_details = INCIDENTS.get(incident_type, {})

        # Get hardness and required resources for the incident
        hardness = incident_details.get('hardness', 0)
        required_police_cars = incident_details.get('required_police_cars', 0)
        required_firetrucks = incident_details.get('required_firetrucks', 0)
        required_ambulances = incident_details.get('required_ambulances', 0)
        incident.vehicles_needed = [required_police_cars, required_firetrucks, required_ambulances]

        # Calculate the number of available vehicles
        available_police_cars = sum(1 for car in self.police_cars if car.available)
        available_firetrucks = sum(1 for truck in self.firetrucks if truck.available)
        available_ambulances = sum(1 for ambulance in self.ambulances if ambulance.available)

        # Adjust priority based on availability of resources
        # If fewer vehicles are available than required, the priority increases
        priority_adjustment = 0
        if available_police_cars < required_police_cars:
            priority_adjustment += (required_police_cars - available_police_cars) * 10
        if available_firetrucks < required_firetrucks:
            priority_adjustment += (required_firetrucks - available_firetrucks) * 10
        if available_ambulances < required_ambulances:
            priority_adjustment += (required_ambulances - available_ambulances) * 10

        # Final priority calculation
        priority = 100 - hardness + priority_adjustment

        return priority

    def dispatch_vehicles(self, incident):
        # determine the number of vehicles needed for the incident
        needed_police_cars = incident.vehicles_needed[0]
        needed_firetrucks = incident.vehicles_needed[1]
        needed_ambulances = incident.vehicles_needed[2]

        # dispatch vehicles
        dispatched_police_cars = 0
        dispatched_firetrucks = 0
        dispatched_ambulances = 0

        # dispatch police cars
        for car in self.police_cars:
            car.lock.acquire()
            if car.available and dispatched_police_cars < needed_police_cars:
                car.attend_incident(incident)
                dispatched_police_cars += 1
            car.lock.release()

        # dispatch firetrucks
        for truck in self.firetrucks:
            truck.lock.acquire()
            if truck.available and dispatched_firetrucks < needed_firetrucks:
                truck.attend_incident(incident)
                dispatched_firetrucks += 1
            truck.lock.release()

        # dispatch ambulances
        for ambulance in self.ambulances:
            ambulance.lock.acquire()
            if ambulance.available and dispatched_ambulances < needed_ambulances:
                ambulance.attend_incident(incident)
                dispatched_ambulances += 1
            ambulance.lock.release()

        # update incident status
        incident.status = "dispatched"
        incident.vehicles_dispatched = [dispatched_police_cars, dispatched_firetrucks, dispatched_ambulances]
        incident.vehicles_needed = [needed_police_cars - dispatched_police_cars, needed_firetrucks - dispatched_firetrucks, needed_ambulances - dispatched_ambulances]

        print(f"Dispatched {dispatched_police_cars} police cars, {dispatched_firetrucks} firetrucks, and {dispatched_ambulances} ambulances to incident {incident.id}")