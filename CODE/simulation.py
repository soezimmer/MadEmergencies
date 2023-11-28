import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from services.city import City
import osmnx as ox
from utils.constants import NORTH, SOUTH, EAST, WEST
import numpy as np
import time
import logging


class Simulation:
    """
    A class representing a simulation of emergency incidents in a city.

    Attributes:
    - city: The city object representing the simulated city.
    - graph: The graph object representing the city's road network.
    - fig: The figure object for plotting the simulation map.
    - ax: The axes object for plotting the simulation map.
    - citizen_scatter: The scatter plot object for citizens.
    - incident_scatter: The scatter plot object for incidents.
    - police_scatter: The scatter plot object for police.
    - firetruck_scatter: The scatter plot object for firetrucks.
    - ambulance_scatter: The scatter plot object for ambulances.
    - end: A boolean indicating whether the simulation has ended.

    Methods:
    - plot_map: Plots the map for the simulation.
    - start_simulation: Starts the simulation by deploying emergency services and citizens, and plotting the map.
    - refresh_map: Refreshes the map by updating the positions of citizens, emergency services, and incidents.
    - update_texts: Updates the text information for active incidents and incident queue.
    - run: Runs the simulation by starting the emergency services, plotting the map, and animating the map updates.
    """
    def __init__(self, city):
        self.city = city
        self.graph = city.graph 
        self.fig, self.ax = None, None
        self.citizen_scatter = None
        self.incident_scatter = None
        self.police_scatter = None
        self.firetruck_scatter = None
        self.ambulance_scatter = None
        self.end = False

    def plot_map(self):
        """
        Plots the map for the simulation.
        """
        self.fig = plt.figure(figsize=(20, 22), facecolor='black')
        gs = self.fig.add_gridspec(2, 2, height_ratios=[5, 1])  # Adjust for two rows and two columns

        # Map subplot
        self.ax = self.fig.add_subplot(gs[0, :]) 
        ox.plot_graph(self.graph, ax=self.ax, node_size=0, show=False)
        self.ax.set_xlim([WEST, EAST])
        self.ax.set_ylim([SOUTH, NORTH])
        self.fig.subplots_adjust(top=0.95)

        self.citizen_scatter = self.ax.scatter([], [], c='black', s=20, label='Citizens')
        self.incident_scatter = self.ax.scatter([], [], c='orange', s=60, label='Incidents', marker='s')
        self.police_scatter = self.ax.scatter([], [], c='blue', s=30, label='Police')
        self.firetruck_scatter = self.ax.scatter([], [], c='red', s=30, label='Firetrucks')
        self.ambulance_scatter = self.ax.scatter([], [], c='green', s=30, label='Ambulances')
        self.ax_active_incidents = self.fig.add_subplot(gs[1, 0])
        self.ax_active_incidents.axis('off')
        self.active_incidents_text = self.ax_active_incidents.text(0, 1, '', ha='left', va='top', color='white')

        self.ax_queue = self.fig.add_subplot(gs[1, 1])
        self.ax_queue.axis('off')
        self.queue_text = self.ax_queue.text(0, 1, '', ha='left', va='top', color='white')

        # Titles for the text areas
        self.ax_active_incidents.set_title("Active Incidents", color='white')
        self.ax_queue.set_title("Incident Queue", color='white')


        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()
        

        self.anim = FuncAnimation(self.fig, self.refresh_map, interval=100, cache_frame_data=False)
        plt.legend()
        plt.show()

    def start_simulation(self):
        """
        Starts the simulation by deploying emergency services and citizens, and plotting the map.
        """
        self.deploy_emergency_services()
        self.deploy_citizens()
        self.plot_map()

    def refresh_map(self, frame):
        """
        Refreshes the map by updating the positions of citizens, emergency services, and incidents.

        Parameters:
        - frame: The frame number of the animation.

        Returns:
        A tuple of "artists" that have been changed.
        """
        citizen_nodes = [citizen.current_node for citizen in self.city.citizens]
        police_nodes = [police.current_node for police in self.city.police_onsite]
        firetruck_nodes = [firetruck.current_node for firetruck in self.city.firetrucks_onsite]
        incident_nodes = [incident.location for incident in self.city.emergency_response.active_incidents.values()]
        ambulance_nodes = [ambulance.current_node for ambulance in self.city.ambulances_onsite]

        # Get coordinates for each group
        citizen_coords = [[self.graph.nodes[node]['x'], self.graph.nodes[node]['y']] for node in citizen_nodes] if citizen_nodes else np.empty((0, 2))
        police_coords = [[self.graph.nodes[node]['x'], self.graph.nodes[node]['y']] for node in police_nodes] if police_nodes else np.empty((0, 2))
        firetruck_coords = [[self.graph.nodes[node]['x'], self.graph.nodes[node]['y']] for node in firetruck_nodes] if firetruck_nodes else np.empty((0, 2))
        ambulance_coords = [[self.graph.nodes[node]['x'], self.graph.nodes[node]['y']] for node in ambulance_nodes] if ambulance_nodes else np.empty((0, 2))
        incident_coords = [[self.graph.nodes[node]['x'], self.graph.nodes[node]['y']] for node in incident_nodes] if incident_nodes else np.empty((0, 2))

        # Update scatters with new positions
        self.citizen_scatter.set_offsets(citizen_coords)
        self.police_scatter.set_offsets(police_coords)
        self.firetruck_scatter.set_offsets(firetruck_coords)
        self.ambulance_scatter.set_offsets(ambulance_coords)
        self.incident_scatter.set_offsets(incident_coords)
        self.update_texts()
        self.ax.legend()

        # We need to return a tuple of "artists" that have been changed
        return self.citizen_scatter, self.incident_scatter, self.police_scatter, self.firetruck_scatter, self.ambulance_scatter, self.active_incidents_text, self.queue_text


    def update_texts(self):
        """
        Updates the text information for active incidents and incident queue.
        """
        # Update text for active incidents
        active_incidents = self.city.emergency_response.active_incidents
        active_incidents_info = "\n".join([f"Incident {id} - {incident.incident_type} - Severity {round(incident.severity,2)}"
                                          for id, incident in active_incidents.items()])
        self.active_incidents_text.set_text(active_incidents_info)

        # Update text for incident queue
        incident_queue_info = "\n".join([f"Incident {incident_id} - Priority {round(priority,2)}"
                                        for priority, incident_id in self.city.emergency_response.incident_queue.queue])
        self.queue_text.set_text(incident_queue_info)

    def run(self):
        """
        Runs the simulation by starting the emergency services, plotting the map, and animating the map updates.
        """
        self.city.start_services()
        self.plot_map()
        self.anim = FuncAnimation(self.fig, self.refresh_map, interval=50, blit=True)
        plt.legend()
        plt.show()