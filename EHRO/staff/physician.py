import json
import random
import string
from os import path

from Cryptodome.PublicKey import RSA

from patient import Patient
from visit import Visit


class Physician:
    def __init__(self, username, password, clinic_id):
        self.username = username
        self.password = password
        # self.username = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        key = RSA.generate(2048)
        self.private_key = key.export_key().decode('utf-8')
        self.public_key = key.public_key().export_key().decode('utf-8')
        self.clinic_id = clinic_id
        # _path = paths.CLINICS_PATH + str(clinic_id) + ".json"
        # if not path.exists(_path):
        #     print("ERROR : the clinic does not exist")
        #     return
        # clinic_file = open(_path, "r")
        # clinic_object = json.loads(clinic_file.read())
        # clinic_object["staff"].append(self.__dict__)
        # clinic_file = open(_path, "w")
        # json.dump(clinic_object, clinic_file)

    def create_patient_visit(self):
        patient_id = input("Patient ID: ")
        type = input("Type of visit (If it is a regular visit enter 1, if it is a lab test enter 2): ")
        reason_for_visit = input("Reason for the visit: ")
        pulse = input("Pulse: ")
        temperature = input("Temperature: ")
        glucose = input("Glucose: ")
        blood_pressure = input("Blood pressure: ")
        diagnosis = input("Diagnosis: ")
        prescription = input("Prescription: ")

        visit = Visit(patient_id, type, prescription, diagnosis, reason_for_visit, pulse, temperature, glucose,
                      blood_pressure)

        # 1. generate AES key on the fly
        # 2. hash the visit then encrypt the hash using the staff private key
        # 3. (digital envelope) encrypt the AES key using the public key of the clinic
        # 4. encrypt the data using the AES key generated
        # 5. send the visit to the clinic

    def create_patient(self):
        name = input("Name: ")
        age = input("Age: ")
        weight = input("Weight: ")
        blood_pressure = input("Blood pressure: ")
        pulse = input("Pulse: ")
        oxygen_saturation = input("Oxygen saturation: ")
        glucose = input("Glucose: ")
        clinic_id = self.clinic_id

        patient = Patient(name, age, weight, blood_pressure, pulse, oxygen_saturation, glucose, clinic_id)


if __name__ == '__main__':
    p = Physician('QK7DG7X1VIKUOBOW')
    print(type(p.private_key))
    # print(p.private_key, p.public_key)
