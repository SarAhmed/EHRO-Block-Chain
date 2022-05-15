from datetime import datetime


class Visit:
    def __init__(self, patient_id, type, prescription, diagnosis, reason_for_visit, pulse, temperature, glucose, blood_pressure):
        self.patient_id = patient_id
        self.type = type
        self.prescription = prescription
        self.diagnosis = diagnosis
        self.reason_for_visit = reason_for_visit
        self.pulse = pulse
        self.temperature = temperature
        self.glucose = glucose
        self.blood_pressure = blood_pressure
        self.visit_date = datetime.now()
