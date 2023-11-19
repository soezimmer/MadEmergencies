import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from services.city import City  
import osmnx as ox
from utils.constants import NORTH, SOUTH, EAST, WEST


class Simulation:
    def __init__(self, city):
        self.city = city
        self.fig, self.ax = None, None
        self.citizen_scatter = None
        self.incident_scatter = None
        self.police_scatter = None
        self.firetruck_scatter = None


    def plot_map(self):
        # Initialize a map plot
        self.fig, self.ax = plt.subplots(figsize=(20, 20), facecolor='black')
        ox.plot_graph(self.graph, ax=self.ax, node_size=0, show=False)

        # Set the limits of the plot to the limits of the graph
        self.ax.set_xlim([WEST, EAST])
        self.ax.set_ylim([SOUTH, NORTH])

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
        self.city.start_services()
        self.plot_map()
        self.anim = FuncAnimation(self.fig, self.refresh_map, interval=200, blit=True)
        plt.legend()
        plt.show()