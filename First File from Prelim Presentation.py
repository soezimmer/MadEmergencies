# Imports
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import osmnx as ox
import threading
import time
import random
import numpy as np
from queue import Queue
north, south, east, west = 40.501416, 40.459202, -3.606143, -3.711698
firestation = 55243514
ambulancestation = 26207177
policestation = 2421410285
end = threading.Event()


# Parent Class for all moving objects (Citizens, Police, Firemen)
class MovingObject(threading.Thread):
    def __init__(self, id, graph, start_node, route=None):
        super().__init__()
        self.id = id
        self.graph = graph
        self.current_node = start_node
        self.lock = threading.Lock()
        self.target_node = None  # The destination node (can be set later)
        self.route = route if route is not None else []  # The path to follow
        self.route_index = 0  # Which step we are at in the route
        self.scatter = None  # Reference to the matplotlib scatter object
        self.position = None  # Position for the animation (x, y coordinates)
        

    # Method to calculate the path from the current_node to the target_node
    def set_route(self, target_node, weight='length'):
        self.target_node = target_node
        self.route = ox.shortest_path(self.graph, self.current_node, self.target_node, weight=weight)
        self.route_index = 0

    def move(self):
        # Method to move along the route
        while self.route and self.route_index < len(self.route) - 1:
            self.current_node = self.route[self.route_index]
            self.route_index += 1
            self.position = (self.graph.nodes[self.current_node]['x'], self.graph.nodes[self.current_node]['y'])
            return True
        else:
            return False  # Movement is done

    def run(self):
        while self.move() and not end.is_set():
            time.sleep(0.2)  # Wait between nodes


class Incident:
    def __init__(self, id, osmid, incident_type, second_help):
        # Define properties of incident
        self.id = id
        self.location = osmid
        self.incident_type = incident_type
        self.status = "reported"
        self.secondary_help = second_help
        self.missing_resources = 0
        self.lock = threading.Lock()
        print(f"Incident of type {self.incident_type} initiated at {self.location}")


class Citizen(MovingObject):
    def __init__(self, id, graph, emergency_center):
        start_node = random.choice(list(graph.nodes()))
        super().__init__(id, graph, start_node)
        self.num_incidents_reported = 0
        self.emergency_center = emergency_center

    def report_incident(self):
        incident_type = random.choice(["fire", "crime"])
        incident_location = self.current_node
        secondary_help = incident_type if random.random() < 0.1 else None
        print(f"Citizen {self.id} has reported an {incident_type} at {incident_location}")

        # Create a new Incident object with a unique ID, location, type, and whether secondary help is needed
        incident_id = f"{incident_type}_{self.id}_{self.num_incidents_reported}"
        incident_class = Incident(incident_id, incident_location, incident_type, secondary_help)
        # Report the incident to the Emergency Response Center
        self.emergency_center.report_incident(incident_class)
        self.num_incidents_reported += 1

    def run(self):
        while self.num_incidents_reported < 3:
            if random.random() < 0.2:
                self.report_incident()
            time.sleep(10)
        end.set()


class PoliceCar(MovingObject):
    def __init__(self, id, police_incidents, police_incidents_lock, graph):
        start_node = policestation  # Assuming policestation is defined
        super().__init__(id, graph, start_node)
        self.police_incidents = police_incidents
        self.police_incidents_lock = police_incidents_lock
        self.available = True
        self.at_home_location = True

    def attend_incident(self, incident):
        with incident.lock:
            incident.status = "attending"
            incident.resolved = False
        super().run()
        print(f"Police car {self.id} arrived at incident at {incident.location}")
        time.sleep(5)  # Simulate time to resolve incident
        with incident.lock:
            incident.status = "resolved"
            incident.resolved = True
        print(f"Police car {self.id} resolved incident at {incident.location}")
        self.set_route(policestation)
        super().run()
        print(f"Police car {self.id} returned to station")
        self.at_home_location = True
        self.available = True
            


class FireTruck(MovingObject):
    def __init__(self, id, fire_incidents, fire_incidents_lock, graph):
        start_node = firestation  # Assuming firestation is defined
        super().__init__(id, graph, start_node)
        self.fire_incidents = fire_incidents
        self.fire_incidents_lock = fire_incidents_lock
        self.available = True
        self.at_home_location = True

    def attend_incident(self, incident):
        with incident.lock:
            incident.status = "attending"
            incident.resolved = False
        super().run()
        print(f"Firetruck {self.id} arrived at incident at {incident.location}")
        time.sleep(5)
        with incident.lock:
            incident.status = "resolved"
            incident.resolved = True
        print(f"Firetruck {self.id} resolved incident at {incident.location}")
        self.set_route(firestation)
        super().run()
        print(f"Firetruck {self.id} returned to station")
        self.at_home_location = True
        self.available = True


class EmergencyResponseCenter(threading.Thread):
    def __init__(self, firetrucks, police_cars):
        super().__init__()
        self.incident_queue = Queue()
        self.firetrucks = firetrucks
        self.police_cars = police_cars
        self.active_incidents = {}  # Dictionary to track active incidents
        self.lock = threading.RLock()  # Reentrant lock for thread safety
        self.dispatch_event = threading.Event()
        print("Emergency Response Center activated")

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


class City:
    def __init__(self, citizens_number):
        self.citizens_number = citizens_number
        self.citizens = []
        self.firetrucks_onsite = []
        self.police_onsite = []
        self.emergency_response = None
        self.incident_queue = []
        self.incident_queue_lock = threading.Lock()
        self.fire_incidents = list()
        self.fire_incidents_lock = threading.Lock()
        self.police_incidents = list()
        self.police_incidents_lock = threading.Lock() 
        self.graph = ox.graph_from_bbox(north, south, east, west, network_type='drive')
        self.run()

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

    def plot_map(self):
        # Initialize a map plot
        self.fig, self.ax = plt.subplots(figsize=(20, 20), facecolor='black')
        ox.plot_graph(self.graph, ax=self.ax, node_size=0, show=False)

        # Set the limits of the plot to the limits of the graph
        self.ax.set_xlim([west, east])
        self.ax.set_ylim([south, north])

        self.citizen_scatter = self.ax.scatter([], [], c='black', s=20, label='Citizens')
        self.incident_scatter = self.ax.scatter([], [], c='orange', s=75, label='Incidents', marker='s')
        self.police_scatter = self.ax.scatter([], [], c='blue', s=30, label='Police')
        self.firetruck_scatter = self.ax.scatter([], [], c='red', s=30, label='Firetrucks')

        self.anim = FuncAnimation(self.fig, self.refresh_map, interval=100, cache_frame_data=False)
        plt.legend()
        plt.show()

    def start_simulation(self):
        self.deploy_emergency_services()
        self.deploy_citizens()
        self.plot_map()

    def refresh_map(self, frame):
        # We need to define how to get current locations of citizens, incidents, and emergency vehicles
        citizen_nodes = [citizen.current_node for citizen in self.citizens]
        police_nodes = [police.current_node for police in self.police_onsite]
        firetruck_nodes = [firetruck.current_node for firetruck in self.firetrucks_onsite]
        incident_nodes = [incident.location for incident in self.emergency_response.active_incidents.values()]

        # Get coordinates for each group
        citizen_coords = [[self.graph.nodes[node]['x'], self.graph.nodes[node]['y']] for node in citizen_nodes]
        police_coords = [[self.graph.nodes[node]['x'], self.graph.nodes[node]['y']] for node in police_nodes]
        firetruck_coords = [[self.graph.nodes[node]['x'], self.graph.nodes[node]['y']] for node in firetruck_nodes]
        
        # Update scatters with new positions
        self.citizen_scatter.set_offsets(citizen_coords)
        self.police_scatter.set_offsets(police_coords)
        self.firetruck_scatter.set_offsets(firetruck_coords)
        
        # Handle incident_coords separately, checking if the list is empty
        incident_coords = [[self.graph.nodes[node]['x'], self.graph.nodes[node]['y']] for node in incident_nodes] if incident_nodes else np.empty((0, 2))
        self.incident_scatter.set_offsets(incident_coords)

        # We need to return a tuple of "artists" that have been changed
        return self.citizen_scatter, self.incident_scatter, self.police_scatter, self.firetruck_scatter


    def run(self):
        print("Starting simulation")
        self.start_simulation()
        self.anim = FuncAnimation(self.fig, self.refresh_map, interval=200, blit=True)
        plt.legend()
        plt.show()


if __name__ == "__main__":
    num_citizens = 10
    mycity = City(num_citizens)

        
