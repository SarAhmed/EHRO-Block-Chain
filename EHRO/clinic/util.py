import base64
import configparser
import json

from Cryptodome.Cipher import AES
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Hash import SHA3_256
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from Cryptodome.Signature import pkcs1_15

from paths import CLINICS_PATH


def write_ehro_key_in_config(ehro_public_key):
    # CONFIG.set("STATIC", "ehro_public_key", ehro_public_key)
    #
    # with open('config.ini', 'w') as configfile:  # save
    #     CONFIG.write(configfile)

    config = configparser.ConfigParser()
    config.read("config.ini")
    config.set("STATIC", "ehro_public_key", ehro_public_key)
    with open('config.ini', 'w') as configfile:  # save
        config.write(configfile)


def get_clinic_id():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config['STATIC']['clinic_id']


def validate_credentials(username, password):
    clinic_json = json.load(open(CLINICS_PATH))
    for physician in clinic_json["staff"]:
        if physician["username"] == username and physician["password"] == password:
            return True
    return False


def validate_patient_not_exists(data):
    return get_patient_idx(data) == -1


def get_patient_idx(data):
    data_json = json.loads(data)
    username = data_json["username"]
    clinic_json = json.load(open(CLINICS_PATH))
    idx = 0
    for p in clinic_json["patients"]:
        if p["username"] == username:
            return idx
        idx = idx + 1
    return -1


def decrypt_using_clinic_private_key(encrypted_data):
    config = configparser.ConfigParser()
    config.read("config.ini")
    encrypted_data = str_to_bytes(encrypted_data)
    private_key = RSA.import_key(config['DYNAMIC']['clinic_private_key'])
    decryptor = PKCS1_OAEP.new(private_key)
    return decryptor.decrypt(encrypted_data)


def encrypt_using_ehro_public_key(data):
    config = configparser.ConfigParser()
    config.read("config.ini")
    ehro_public_key = RSA.import_key(config['STATIC']['ehro_public_key'])
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


def add_req_to_database(req, sign):
    clinic_json = json.load(open(CLINICS_PATH))
    clinic_json["requests"][sign] = json.loads(req)
    with open("DB/clinic.json", "w") as outfile:
        outfile.write(json.dumps(clinic_json, indent=4))


def remove_from_database(entry_type, data):
    clinic_json = json.load(open(CLINICS_PATH))
    if entry_type == "patients":
        clinic_json["patients"].pop(get_patient_idx(data))

    if entry_type == "visits":
        clinic_json["visits"].pop(get_visit_idx(data))

    with open("DB/clinic.json", "w") as outfile:
        outfile.write(json.dumps(clinic_json, indent=4))


def validate_visit_not_exists(data):
    return get_visit_idx(data) == -1


def get_visit_idx(data):
    data_json = json.loads(data)
    visit_id = data_json["id"]
    clinic_json = json.load(open(CLINICS_PATH))
    idx = 0
    for p in clinic_json["visits"]:
        if p["id"] == visit_id:
            return idx
        idx = idx + 1
    return -1


def get_patient_history(data):
    data_json = json.loads(data)
    username = data_json["username"]
    clinic_json = json.load(open(CLINICS_PATH))

    profile = None
    for p in clinic_json["patients"]:
        if p["username"] == username:
            profile = p
            break

    visits = []
    for v in clinic_json["visits"]:
        if v["username"] == username:
            visits.append(v)

    return json.dumps({"profile": profile, "visits": visits}, default=lambda o: o.__dict__, sort_keys=True, indent=4)



def get_staff_public_key(username):
    clinic_json = json.load(open(CLINICS_PATH))
    for p in clinic_json["staff"]:
        if p["username"] == username:
            return p["public_key"]

def prepare_request(obj, username):
    config = configparser.ConfigParser()
    config.read("config.ini")
    clinic_private_key = RSA.import_key(config['DYNAMIC']['clinic_private_key'])
    physician_public_key = RSA.import_key(get_staff_public_key(username))
    obj = bytes(obj, 'utf-8')
    symmetric_key = get_random_bytes(32)

    hash_obj = SHA3_256.new()
    hash_obj.update(obj)

    signed_hashed_data = pkcs1_15.new(clinic_private_key).sign(hash_obj)

    encryptor = PKCS1_OAEP.new(physician_public_key)
    encrypted_symmetric_key = encryptor.encrypt(symmetric_key)
    aes_encryptor = AES.new(symmetric_key, AES.MODE_EAX)
    nonce = aes_encryptor.nonce
    encrypted_data = aes_encryptor.encrypt(obj)
    payload = {
        "encrypted_symmetric_key": bytes_to_str(encrypted_symmetric_key),
        "signed_data": bytes_to_str(signed_hashed_data),
        "encrypted_data": bytes_to_str(encrypted_data),
        "nonce": bytes_to_str(nonce)
    }
    request_body = {
        "payload": payload
    }
    return json.dumps(request_body)


def get_packet(hash):
    clinic_json = json.load(open(CLINICS_PATH))
    if hash in clinic_json["requests"]:
        return clinic_json["requests"][hash]


