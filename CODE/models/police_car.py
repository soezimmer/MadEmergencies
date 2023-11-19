class PoliceCar(MovingObject):
    def __init__(self, id, police_incidents, police_incidents_lock, graph):
        start_node = policestation  # Assuming policestation is defined
        super().__init__(id, graph, start_node)
        self.police_incidents = police_incidents
        self.police_incidents_lock = police_incidents_lock
        self.available = True
        self.at_home_location = True

    def attend_incident(self, incident):
        with incident.lock:
            incident.status = "attending"
            incident.resolved = False
            super().run()
            print(f"Police car {self.id} arrived at incident at {incident.location}")
            time.sleep(5)  # Simulate time to resolve incident
            incident.status = "resolved"
            incident.resolved = True
            print(f"Police car {self.id} resolved incident at {incident.location}")
            self.set_route(policestation)
            super().run()
            print(f"Police car {self.id} returned to station")
            self.at_home_location = True
            self.available = True