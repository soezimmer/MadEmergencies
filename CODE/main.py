from services.city import City
from simulation import Simulation

def main():
    num_citizens = 10  # Define the number of citizens for the simulation
    my_city = City(num_citizens)  # Create an instance of the City class
    my_city.start_services() 
    simulation = Simulation(my_city)  # Create an instance of the Simulation class with the city instance
    simulation.run()  # Run the simulation

if __name__ == '__main__':
    main()