import base64
import configparser
import json

from Cryptodome.Cipher import AES
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes

from paths import CLINICS_PATH

CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini")


def validate_credentials(username, password):
    clinic_json = json.load(open(CLINICS_PATH))
    for physician in clinic_json["staff"]:
        if physician["username"] == username and physician["password"] == password:
            return True
    return False


def validate_patient_not_exists(data):
    data_json = json.loads(data)
    username = data_json["username"]
    clinic_json = json.load(open(CLINICS_PATH))
    for p in clinic_json["patients"]:
        if p["username"] == username:
            return False
    return True


def decrypt_using_clinic_private_key(encrypted_data):
    encrypted_data = str_to_bytes(encrypted_data)
    private_key = RSA.import_key(CONFIG['DYNAMIC']['clinic_private_key'])
    decryptor = PKCS1_OAEP.new(private_key)
    return decryptor.decrypt(encrypted_data)


def encrypt_using_ehro_public_key(data):
    ehro_public_key = RSA.import_key(CONFIG['STATIC']['ehro_public_key'])
    encryptor = PKCS1_OAEP.new(ehro_public_key)
    return encryptor.encrypt(data)


def decrypt_using_AES_key(encrypted_data, symmetric_key, nonce):
    nonce = str_to_bytes(nonce)
    encrypted_data = str_to_bytes(encrypted_data)
    decryptor = AES.new(symmetric_key, AES.MODE_EAX, nonce=nonce)
    return decryptor.decrypt(encrypted_data)


def encrypt_using_AES(data):
    symmetric_key = get_random_bytes(32)
    encryptor = AES.new(symmetric_key, AES.MODE_EAX)
    nonce = encryptor.nonce
    encrypted_data = encryptor.encrypt(data)
    return {
        "symmetric_key": symmetric_key,
        "nonce": nonce,
        "encrypted_data": encrypted_data
    }


def bytes_to_str(bytes):
    return base64.b64encode(bytes).decode('utf-8')


def str_to_bytes(input_str):
    return base64.b64decode(bytes(input_str, 'utf-8'))


def add_to_database(key, data):
    clinic_json = json.load(open(CLINICS_PATH))
    clinic_json[key].append(json.loads(data))
    with open("DB/clinic.json", "w") as outfile:
        outfile.write(json.dumps(clinic_json, indent=4))


def add_signed_to_database(key, data, sign):
    clinic_json = json.load(open(CLINICS_PATH))
    data_json = json.loads(data)
    data_json["sign"] = sign
    clinic_json[key].append(data_json)
    with open("DB/clinic.json", "w") as outfile:
        outfile.write(json.dumps(clinic_json, indent=4))