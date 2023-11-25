import threading
import logging
import time
from abc import ABC, abstractmethod

class Observable(ABC):
    @abstractmethod
    def register_observer(self, observer):
        pass

    @abstractmethod
    def remove_observer(self, observer):
        pass

    @abstractmethod
    def notify_observers(self, incident):
        pass

class Incident(threading.Thread, Observable):
    def __init__(self, id, osmid, incident_type, time, severity, city):
        # Define properties of incident
        super().__init__()
        self.id = id
        self.location = osmid
        self.incident_type = incident_type
        self.report_time = time
        self.severity = severity
        self.status = "reported"
        self.resolved = False
        self.vehicles_dispatched = []
        self.vehicles_needed = []
        self.lock = threading.Lock()
        self.observers = []
        self.city = city

    def __str__(self):
        return f"ID: {self.id}, Location: {self.location}, Type: {self.incident_type}, Status: {self.status}"
    
    def register_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update(self)

    def run(self):
        self.notify_observers()
        while not self.resolved:
            time.sleep(0.5)
            with self.lock:  # Ensure this block is thread-safe
                if self.severity <= 0:
                    self.resolved = True
                    self.status = "resolved"
                    self.notify_observers()  # Notify the observers before exiting
                    break  # Correctly exit the loop if the incident is resolved
                self.severity += 0.1  # Decrease the severity over time