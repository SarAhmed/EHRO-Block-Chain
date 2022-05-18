import string
import random


class Patient:
    def __init__(self, name, age, weight, blood_pressure, pulse, oxygen_saturation, glucose, clinic_id):
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        self.name = name
        self.age = age
        self.weight = weight
        self.blood_pressure = blood_pressure
        self.pulse = pulse
        self.oxygen_saturation = oxygen_saturation
        self.glucose = glucose
        self.visits = []
        self.clinic_id = clinic_id
        # _path = paths.CLINICS_PATH + str(clinic_id) + ".json"
        # clinic_file = open(_path, "r")
        # clinic_object = json.loads(clinic_file.read())
        # clinic_object["patients"].append(self.__dict__)
        # clinic_file = open(_path, "w")
        # json.dump(clinic_object, clinic_file)
