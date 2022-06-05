from datetime import datetime
import random
import string
import json


class Visit:
    def __init__(self, username, type, prescription, diagnosis, reason_for_visit, pulse, temperature, glucose,
                 blood_pressure,id = None):
        if id == None:
            self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        else:
            self.id = id
        self.username = username
        self.type = type
        self.prescription = prescription
        self.diagnosis = diagnosis
        self.reason_for_visit = reason_for_visit
        self.pulse = pulse
        self.temperature = temperature
        self.glucose = glucose
        self.blood_pressure = blood_pressure
        self.last_update_time = datetime.now()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
