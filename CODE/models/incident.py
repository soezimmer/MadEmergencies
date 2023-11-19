import threading

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