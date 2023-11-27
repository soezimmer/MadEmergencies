# Emergency Response Simulation

## Overview

This project is an emergency response simulation set in a city. The simulation models citizens, emergency vehicles (police cars, fire trucks, and ambulances), and various types of incidents (e.g., fires, medical emergencies, robberies). The scope of the project emphasizes dispatching the appropriate emergency vehicles to incidents based on their priority and resource requirements. Statistical data about incidents is also collected and summarized using a MySQL database.

## Authors
- Luis Javier Gómez García
- Antonia Bleier
- Saleh Haidar
- Ernests Jansons
- Alvaro Morera
- Sören Zimmer

## Features

- **Simulation Environment**: A city with citizens, emergency vehicles, and incidents.
- **Dynamic Incident Generation**: Incidents are randomly generated with specific types, severities, and resource requirements.
- **Priority Queue System**: Incidents are queued based on a calculated priority, which considers severity and resource availability.
- **Dispatch Mechanism**: Emergency vehicles are dispatched from their stations to attend incidents.
- **MySQL Integration**: Incident data is recorded and summarized in a MySQL database for further analysis.
- **Threaded Execution**: Each citizen and vehicle runs on its own thread, allowing for parallel processing.
- **Visualization Interface**: Utilizes `matplotlib` to provide a real-time graphical representation of the simulation, including the movements of citizens and vehicles on a map.

## Installation

Before you begin, make sure you have the following dependencies installed:

- Python 3.x
- matplotlib
- osmnx
- mysql-connector-python

Use the following command to install the required Python libraries:

```
pip install matplotlib osmnx mysql-connector-python
```

## Database Setup

Create a MySQL database and user with the credentials specified in `utils/constants.py`. The `utils/add_sql.py` script sets up the database tables and provides functionality to record incident data.

## Usage

To run the simulation:

1. Navigate to the project directory.
2. Choose the desired parameters in `utils/constants.py`
3. Execute `main.py` by running:

```bash
python main.py
```

The simulation will start, and the visualization window will open.

## Simulation Details

### Components

- **Citizen**: Represents people in the city that may report incidents.
- **EmergencyVehicle**: An abstract base class inherited by vehicle types (police cars, fire trucks, ambulances), moving towards incidents when dispatched.
- **Incident**: A class representing an emergency that has occurred in the city.
- **MovingObject**: A base class for objects that move in the simulation, extended by `Citizen` and `EmergencyVehicle`.

### Services

- **City**: Handles the initial setup of the simulation environment, including citizens, vehicles, and the emergency response center.
- **EmergencyResponseCenter**: Manages incident reporting, queuing via a priority queue, and vehicle dispatching.

### Visualization

The `simulation.py` includes code to visualize the simulation using `matplotlib`. As the simulation runs, you will see citizens, incidents, and emergency vehicles on a map, updated in real-time.
