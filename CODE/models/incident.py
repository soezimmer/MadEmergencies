import threading

class Incident:
    def __init__(self, id, osmid, incident_type, time, hardness):
        # Define properties of incident
        self.id = id
        self.location = osmid
        self.incident_type = incident_type
        self.report_time = time
        self.hardness = hardness
        self.status = "reported"
        self.resolved = False
        self.vehicles_dispatched = []
        self.vehicles_needed = []
        self.lock = threading.Lock()
        print(f"Incident of type {self.incident_type} initiated at {self.location}")

    def __str__(self):
        return f"ID: {self.id}, Location: {self.location}, Type: {self.incident_type}, Status: {self.status}"