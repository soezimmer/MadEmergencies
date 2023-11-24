from services.city import City
from simulation import Simulation
import logging

def main():
    num_citizens = 10  # Define the number of citizens for the simulation
    my_city = City(num_citizens)  # Create an instance of the City class
    my_city.start_services() 
    simulation = Simulation(my_city)  # Create an instance of the Simulation class with the city instance
    simulation.run()  # Run the simulation

if __name__ == '__main__':
    normal_format = "\033[97m%(asctime)s:%(msecs)05d:  %(message)s\033[0m"
    debug_format = "\033[91m%(asctime)s:%(msecs)05d:  %(message)s\033[0m"
    logging.basicConfig(format=normal_format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.basicConfig(format=debug_format, level=logging.ERROR, datefmt="%H:%M:%S")
    #logging.error("Error message")
    main() 