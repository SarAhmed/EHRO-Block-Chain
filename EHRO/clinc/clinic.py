from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import json
import string
import random


class Clinic:
    def __init__(self):
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        self.symmetric_key = str(get_random_bytes(32))
        self.staff = []
        self.patients = []
        json_object = json.dumps(self.__dict__, indent=4)
        with open("../Collections/clinics/clinic" + str(self.id) + ".json", "w") as outfile:
            outfile.write(json_object)


if __name__ == '__main__':
    c = Clinic()
    print(json.dumps(c.__dict__))

