from cryptography.hazmat.primitives.asymmetric import rsa
import json
import string
import random
import os.path
from os import path


class Physician:
    def __init__(self, clinic_id):
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 16))
        self.clinic_id = clinic_id
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()
        self.private_key = self.private_key
        _path = "../Collections/clinics/clinic" + str(self.clinic_id) + ".json"
        if not path.exists(_path):
            print("ERROR : the clinic does not exist")
            return
        # clinic_object = None
        with open(_path) as openfile:
            clinic_object = json.loads(openfile.read())
            clinic_object["staff"].append(self.__dict__)
            print(clinic_object)
            # openfile.write(json.dumps(clinic_object))


if __name__ == '__main__':
    p = Physician('ZBDF1BC8ZGAGRSVE')
    # print(p.id)
    # print(p.private_key, p.public_key)

