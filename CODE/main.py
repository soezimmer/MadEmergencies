from services.city import City
from simulation import Simulation
import logging
from utils.constants import NCITIZENS

def main():
    logging.info("Starting simulation")
    my_city = City(NCITIZENS)  # Create an instance of the City class
    simulation = Simulation(my_city)  # Create an instance of the Simulation class with the city instance
    simulation.run()  # Run the simulation
    my_city.emergency_response.join()  # Wait for the emergency response center to finish
    logging.info("Simulation finished")

if __name__ == '__main__':
    normal_format = "\033[97m%(asctime)s:%(msecs)05d:  %(message)s\033[0m"
    debug_format = "\033[91m%(asctime)s:%(msecs)05d:  %(message)s\033[0m"
    logging.basicConfig(format=normal_format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.basicConfig(format=debug_format, level=logging.ERROR, datefmt="%H:%M:%S", filename="debug.log")
    main() 