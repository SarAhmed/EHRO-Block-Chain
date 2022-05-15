from Cryptodome.PublicKey import RSA
import json
import string
import random
import paths
from os import path


class Physician:
    def __init__(self, clinic_id):
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 16))
        key = RSA.generate(2048)
        self.private_key = key.export_key().decode('utf-8')
        self.public_key = key.public_key().export_key().decode('utf-8')
        _path = paths.CLINICS_PATH + str(clinic_id) + ".json"
        if not path.exists(_path):
            print("ERROR : the clinic does not exist")
            return
        clinic_file = open(_path, "r")
        clinic_object = json.loads(clinic_file.read())
        clinic_object["staff"].append(self.__dict__)
        clinic_file = open(_path, "w")
        json.dump(clinic_object, clinic_file)


if __name__ == '__main__':
    p = Physician('QK7DG7X1VIKUOBOW')
    print(type(p.private_key))
    # print(p.private_key, p.public_key)

