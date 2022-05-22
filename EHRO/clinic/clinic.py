from Cryptodome.Cipher import AES
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
import json
import string
import random
import configparser
import os.path
from os import path

from paths import CLINICS_PATH


class Clinic:
    def __init__(self):
        if path.exists(CLINICS_PATH):
            clinic_json = json.load(open(CLINICS_PATH))
            self.id = clinic_json["id"]
            self.private_key = clinic_json["private_key"]
            self.public_key = clinic_json["public_key"]
            self.staff = clinic_json["staff"]
            self.patients = clinic_json["patients"]
            self.visits = clinic_json["visits"]
        else:
            config = configparser.ConfigParser()
            config.read("config.ini")
            self.id = config["STATIC"]["clinic_id"]
            key = RSA.generate(2048)
            self.private_key = key.export_key().decode('utf-8')
            self.public_key = key.public_key().export_key().decode('utf-8')
            config.set("DYNAMIC", "clinic_public_key", self.public_key)
            config.set("DYNAMIC", "clinic_private_key", self.private_key)
            self.staff = []
            self.patients = []
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

            json_object = json.dumps(self.__dict__, indent=4)
            with open("DB/clinic.json", "w") as outfile:
                outfile.write(json_object)
        # Check database existence and intialize parameters.


if __name__ == '__main__':
    c = Clinic()
    print(json.dumps(c.__dict__))
    clinic = json.load(open(CLINICS_PATH))
    # print(path.exists(CLINICS_PATH))
