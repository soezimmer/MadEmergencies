NORTH, SOUTH, EAST, WEST = 40.501416, 40.459202, -3.606143, -3.711698
FIRE_STATION = 55243514
AMBULANCE_STATION = 26207177
POLICE_STATION = 2421410285
FIRE_TRUCKS = 8
AMBULANCES = 12
POLICE_CARS = 10
NCITIZENS = 20
NINCIDENTS_PER_CITIZEN = 5
CITIZEN_WAIT_TIME = (5, 15)
CITIZEN_REPORT_PROBABILITY = 0.1

INCIDENTS = {
            'petty_theft': {
                'required_police_cars': 1,
                'required_firetrucks': 0,
                'required_ambulances': 0,
                'severity': 5,
                'probability': 0.15
            },
            'traffic_accident_minor': {
                'required_police_cars': 1,
                'required_firetrucks': 0,
                'required_ambulances': 1,
                'severity': 15,
                'probability': 0.13
            },
            'medical_emergency': {
                'required_police_cars': 0,
                'required_firetrucks': 0,
                'required_ambulances': 1,
                'severity': 10,
                'probability': 0.12
            },
            'bar_fight': {
                'required_police_cars': 2,
                'required_firetrucks': 0,
                'required_ambulances': 1,
                'severity': 20,
                'probability': 0.10
            },
            'house_fire_small': {
                'required_police_cars': 1,
                'required_firetrucks': 2,
                'required_ambulances': 1,
                'severity': 30,
                'probability': 0.08
            },
            'vandalism': {
                'required_police_cars': 1,
                'required_firetrucks': 0,
                'required_ambulances': 0,
                'severity': 8,
                'probability': 0.07
            },
            'traffic_accident_major': {
                'required_police_cars': 2,
                'required_firetrucks': 1,
                'required_ambulances': 2,
                'severity': 35,
                'probability': 0.06
            },
            'store_robbery': {
                'required_police_cars': 3,
                'required_firetrucks': 0,
                'required_ambulances': 1,
                'severity': 40,
                'probability': 0.05
            },
            'industrial_fire': {
                'required_police_cars': 2,
                'required_firetrucks': 3,
                'required_ambulances': 2,
                'severity': 60,
                'probability': 0.04
            },
            'earthquake_minor': {
                'required_police_cars': 3,
                'required_firetrucks': 3,
                'required_ambulances': 2,
                'severity': 70,
                'probability': 0.01
            },
            'terrorist_threat': {
                'required_police_cars': 4,
                'required_firetrucks': 1,
                'required_ambulances': 3,
                'severity': 80,
                'probability': 0.025
            },
            'chemical_spill': {
                'required_police_cars': 2,
                'required_firetrucks': 4,
                'required_ambulances': 2,
                'severity': 65,
                'probability': 0.022
            },
            'wildfire': {
                'required_police_cars': 2,
                'required_firetrucks': 4,
                'required_ambulances': 3,
                'severity': 85,
                'probability': 0.028
            },
            'flood': {
                'required_police_cars': 3,
                'required_firetrucks': 3,
                'required_ambulances': 3,
                'severity': 75,
                'probability': 0.015
            },
            'earthquake_major': {
                'required_police_cars': 5,
                'required_firetrucks': 5,
                'required_ambulances': 4,
                'severity': 100,
                'probability': 0.010
            },
            'power_outage': {
                'required_police_cars': 1,
                'required_firetrucks': 0,
                'required_ambulances': 0,
                'severity': 20,
                'probability': 0.03
            },
            'gas_leak': {
                'required_police_cars': 2,
                'required_firetrucks': 1,
                'required_ambulances': 1,
                'severity': 25,
                'probability': 0.025
            },
            'public_disturbance': {
                'required_police_cars': 2,
                'required_firetrucks': 0,
                'required_ambulances': 0,
                'severity': 15,
                'probability': 0.02
            },
            'animal_rescue': {
                'required_police_cars': 1,
                'required_firetrucks': 1,
                'required_ambulances': 0,
                'severity': 10,
                'probability': 0.015
            }
        }