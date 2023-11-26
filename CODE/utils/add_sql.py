from utils.constants import NINCIDENTS_PER_CITIZEN, NCITIZENS, SQL_PASSWORD, SQL_USER
import mysql.connector

# Recall to start SQL
class sql:
    def __init__(self):
        self.all_incidents = {}
        self.cnx = mysql.connector.connect(user=SQL_USER, password=SQL_PASSWORD,
                                      host='127.0.0.1')
        self.cursor = self.cnx.cursor()

        try:
            self.cursor.execute("DROP DATABASE MadEmergencies")
        except mysql.connector.errors.DatabaseError:
            print('Creating database')

        self.cursor.execute("CREATE DATABASE MadEmergencies")
        self.cnx = mysql.connector.connect(user=SQL_USER, password=SQL_PASSWORD,
                                           host='127.0.0.1', database='MadEmergencies')
        self.mycursor = self.cnx.cursor()
        self.mycursor.execute("CREATE TABLE emergencies (id INT AUTO_INCREMENT PRIMARY KEY, time_reported VARCHAR(255), "
                              "incident_type VARCHAR(255), location VARCHAR(255), severity INT, required_police INT, "
                                "required_firetrucks INT, required_ambulances INT)")

    def add_incident(self, time_reported, type, location, severity, required_police, required_firetrucks, required_ambulances):
        unique_id = f"{time_reported}_{type}_{location}"  # Create a unique identifier
        if unique_id not in self.all_incidents:
            self.all_incidents[unique_id] = (time_reported, type, location, severity, required_police, required_firetrucks, required_ambulances)
            return True
        return False

    def add_data(self):
        statement = ("INSERT INTO emergencies (time_reported, incident_type, location, severity, required_police, required_firetrucks, "
                    "required_ambulances) VALUES (%s, %s, %s, %s, %s, %s, %s)")
        self.mycursor.executemany(statement, list(self.all_incidents.values()))
        self.cnx.commit()
        self.all_incidents.clear()  # Clear the dictionary after data is added
        print("Data added to SQL")


    def write_to_file(self):
        all = {}
        query = "SELECT MAX(id) as max_incident_id FROM emergencies"
        self.mycursor.execute(query)
        result = self.mycursor.fetchone()
        all['Number of incidents'] = result[0]

        query = "SELECT incident_type as most_common_incident_type FROM emergencies GROUP BY incident_type ORDER BY COUNT(*) DESC LIMIT 1"
        self.mycursor.execute(query)
        result = self.mycursor.fetchone()
        all['Most common incident'] = result[0]

        query = "SELECT * FROM emergencies WHERE severity = (SELECT MAX(severity) FROM emergencies) LIMIT 1"
        self.mycursor.execute(query)
        result = self.mycursor.fetchone()
        all['Most severe incident (severness)'] = result[2]
        all['Most severe incident (type)'] = result[1]
        all['Most severe incident (police)'] = result[3]
        all['Most severe incident (firetrucks)'] = result[4]
        all['Most severe incident (ambulances)'] = result[5]

        query = (
            "SELECT SUM(required_police) as sum_required_police, SUM(required_firetrucks) as sum_required_firetrucks, "
            "SUM(required_ambulances) as sum_required_ambulances FROM emergencies")

        self.mycursor.execute(query)
        result = self.mycursor.fetchone()
        all['Total police requested'] = result[0]
        all['Total firetrucks requested'] = result[1]
        all['Total ambulances requested'] = result[2]

        with open('output.txt', 'w') as f:
            f.write(f"Number of incidents solved: {all['Number of incidents']}\n")
            f.write(f"The most common incident: {all['Most common incident']}\n")
            f.write(
                f"The most severe incident, a {all['Most severe incident (type)']}, had severity of {all['Most severe incident (severness)']}. ")
            f.write(
                f"It required {all['Most severe incident (ambulances)']} ambulances, {all['Most severe incident (firetrucks)']} firetrucks,")
            f.write(f"and {all['Most severe incident (police)']} police cars.\n")
            f.write(f"Total number of police cars requested: {all['Total police requested']}\n")
            f.write(f"Total number of firetrucks requested: {all['Total firetrucks requested']}\n")
            f.write(f"Total number of ambulances requested: {all['Total ambulances requested']}\n")








