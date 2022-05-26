import string
import random
from datetime import datetime
import time
import json


class Patient:
    def __init__(self, username,name, age, weight, blood_pressure, pulse, oxygen_saturation, glucose, clinic_id):
        # self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        self.username = username
        self.name = name
        self.age = age
        self.weight = weight
        self.blood_pressure = blood_pressure
        self.pulse = pulse
        self.oxygen_saturation = oxygen_saturation
        self.glucose = glucose
        self.clinic_id = clinic_id
        self.last_update_time = time.time()
        # time = datetime.now()
        # self.last_update_time = {'year': time.year, 'month':time.month, 'day':time.day,
        #                          'hour':time.hour,'minutes':time.minute,'seconds':time.second}
        # _path = paths.CLINICS_PATH + str(clinic_id) + ".json"
        # clinic_file = open(_path, "r")
        # clinic_object = json.loads(clinic_file.read())
        # clinic_object["patients"].append(self.__dict__)
        # clinic_file = open(_path, "w")
        # json.dump(clinic_object, clinic_file)
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
