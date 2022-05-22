from physician import Physician
from patient import Patient
from visit import Visit
from Cryptodome.Hash import SHA3_256
from Cryptodome.Random import get_random_bytes
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Signature import pkcs1_15
from Cryptodome.Cipher import AES
import base64
import socket
import requests

import configparser
import json

def prepare_request(obj):
    config = configparser.ConfigParser()
    config.read("config.ini")
    user_private_key = RSA.import_key(config['DYNAMIC']['PHYSICIAN_PRIVATE_KEY'])
    # TODO : change the used PK to the PK of the clinic
    clinic_public_key = RSA.import_key(config['DYNAMIC']['PHYSICIAN_PUBLIC_KEY'])
    obj = bytes(obj, 'utf-8')
    symmetric_key = get_random_bytes(32)

    hash_obj = SHA3_256.new()
    hash_obj.update(obj)

    signed_hashed_data = pkcs1_15.new(user_private_key).sign(hash_obj)

    encryptor = PKCS1_OAEP.new(clinic_public_key)
    encrypted_symmetric_key = encryptor.encrypt(symmetric_key)

    aes_encryptor = AES.new(symmetric_key, AES.MODE_EAX)
    nonce = aes_encryptor.nonce
    encrypted_data= aes_encryptor.encrypt(obj)

    username = config['DYNAMIC']['PHYSICIAN_USERNAME']
    password = config['DYNAMIC']['PHYSICIAN_PASSWORD']
    encrypted_username = encryptor.encrypt(bytes(username,'utf-8'))
    encrypted_password =  encryptor.encrypt(bytes(password,'utf-8'))
    # formuate the object to be sent in the request body
    payload = {
        "encrypted_symmetric_key": encrypted_symmetric_key,
        "signed_data": signed_hashed_data,
        "encrypted_data" : encrypted_data,
        "nonce" : nonce
    }
    request_body = {
        "encrypted_username": encrypted_username,
        "encrypted_password": encrypted_password,
        "payload": payload
    }

    return request_body


def prepare_response(payload):
    config = configparser.ConfigParser()
    config.read("config.ini")
    user_private_key = RSA.import_key(config['DYNAMIC']['PHYSICIAN_PRIVATE_KEY'])
    decryptor = PKCS1_OAEP.new(user_private_key)
    symmetric_key = decryptor.decrypt(payload['encrypted_symmetric_key'])
    cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce=payload['nonce'])
    plaintext = cipher.decrypt(payload['encrypted_data'])
    plaintext_bytes = bytes(plaintext,'utf-8')
    hash_obj = SHA3_256.new()
    hash_obj.update(plaintext_bytes)
    clinic_public_key =  RSA.import_key(config['STATIC']['CLINIC_PUBLIC_KEY'])


    try :
        pkcs1_15.new(clinic_public_key).verify(hash_obj,payload['signed_data'])
        print(plaintext)
    except (ValueError,TypeError) :
        print("SOURCE UNVERIFIABLE")


def create_physician():
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")
    config = configparser.ConfigParser()
    config.read("config.ini")
    static = config['STATIC']
    physician_record = Physician(username, password, static['CLINIC_ID'])
    private_key, public_key = physician_record.generate_rsa_keys()
    # TODO : request to the clinic to update the staff record
    # WE ARE WAITING FOR THE PUBLIC KEY
    physician_dict = physician_record.__dict__
    physician_dict['public_key'] = public_key
    print(physician_dict)
    request_body = json.dumps(physician_dict, indent=4, sort_keys=True,default=str)
    # {
    #     username:'username',
    #     password:'password',
    #     public_key: 'public_key',
    #     last_update_time: 'time'
    #     clinic_id:'clinic_id'
    # }
    # clinic_ip = socket.gethostbyname(config["STATIC"]["CLINIC_ID"])
    print(request_body)
    response = requests.post("http://" + "192.168.33.83" + ":8000/create_physician", json=request_body)

    print(response.text)
    config.set("DYNAMIC", "PHYSICIAN_USERNAME", username)
    config.set("DYNAMIC", "PHYSICIAN_PASSWORD", password)
    config.set("DYNAMIC", "PHYSICIAN_PUBLIC_KEY", public_key)
    config.set("DYNAMIC", "PHYSICIAN_PRIVATE_KEY", private_key)
    with open('config.ini', 'w') as configfile:  # save
        config.write(configfile)

def login():
    # verify the input credentials from the config file
    entered_username = input("Please enter your username: ")
    entered_password = input("Please enter your password: ")
    config = configparser.ConfigParser()
    config.read("config.ini")
    username = config['DYNAMIC']['physician_username']
    password = config['DYNAMIC']['physician_password']
    if username != entered_username or password != entered_password :
        print("The username or password is incorrect ")
        return False
    print("You are successfully logged in")
    return True


def create_patient():
    new_patient_json = get_patient_info()
     # TODO send the new patient to the clinic
    request_body = prepare_request(new_patient_json)
    config = configparser.ConfigParser()
    config.read("config.ini")
    clinic_ip = socket.gethostbyname(config["STATIC"]["CLINIC_ID"])
    response = requests.post("http://" + clinic_ip + ":8000/create_patient", json=request_body)


def update_patient_info():
    current_patient_json = get_patient_info()
    # TODO send the updated patient to the clinic
    request_body = prepare_request(current_patient_json)
    config = configparser.ConfigParser()
    config.read("config.ini")
    clinic_ip = socket.gethostbyname(config["STATIC"]["CLINIC_ID"])
    response = requests.post("http://" + clinic_ip + ":8000/update_patient", json=request_body)


def get_patient_info():
    print("Please enter the following information")
    username = input("Username: ")
    name = input("Name: ")
    age = input("Age: ")
    weight = input("Weight: ")
    blood_pressure = input("Blood pressure: ")
    pulse = input("Pulse: ")
    oxygen_saturation = input("Oxygen saturation: ")
    glucose = input("Glucose: ")
    config = configparser.ConfigParser()
    config.read("config.ini")
    new_patient = Patient(username, name, age, weight, blood_pressure,
                          pulse, oxygen_saturation, glucose, config['STATIC']['CLINIC_ID'])
    return json.dumps(new_patient.__dict__,indent=4, sort_keys=True, default=str)

def add_new_visit():
    new_visit_json = get_visit_info()
    #TODO send the new visit to the clinic
    request_body = prepare_request(new_visit_json)
    config = configparser.ConfigParser()
    config.read("config.ini")
    clinic_ip = socket.gethostbyname(config["STATIC"]["CLINIC_ID"])
    response = requests.post("http://" + clinic_ip + ":8000/create_patient_visit", json=request_body)


def update_visit():
    current_visit_json = get_visit_info()
    #TODO send the updated visit to the clinic
    request_body = prepare_request(current_visit_json)
    config = configparser.ConfigParser()
    config.read("config.ini")
    clinic_ip = socket.gethostbyname(config["STATIC"]["CLINIC_ID"])
    response = requests.post("http://" + clinic_ip + ":8000/update_patient_visit", json=request_body)


def get_visit_info():
    print("Please enter the following information")
    patient_username = input("Patient username: ")
    type = input("Visit type: (regular) or (lab)")
    prescription = input("Prescription: ")
    diagnosis = input("Diagnosis: ")
    reason_for_visit = input("Reason for visit: ")
    pulse= input("Pulse: ")
    temperature = input("Tempreature: ")
    glucose = input("Glucose: ")
    blood_pressure = input("Blood pressure: ")
    new_visit = Visit(patient_username, type, prescription, diagnosis,
                      reason_for_visit, pulse, temperature, glucose,blood_pressure)
    return json.dumps(new_visit.__dict__,indent=4, sort_keys=True, default=str)


def view_patient_history():
    config = configparser.ConfigParser()
    config.read("config.ini")
    # clinic_ip = socket.gethostbyname(config["STATIC"]["CLINIC_ID"])
    # response = requests.get("http://" + clinic_ip + ":8000/view_patient_history")





def gui():
    print("Welcome to the public health care system")
    print("Please select your desired option: ")
    while True:
        option = input("1. Sign up \n2. Login \nSelected option: ")
        if option == "1":
            create_physician()
            break
        elif option == "2":
            if login():
                break
        else:
            print("Please select a valid option.")
    print("You are successfully logged in.")
    print("Please select your desired option: ")
    while True:
        option = input("1. Add new patient\n2. Update patient information \n3. Add visit to an existing patient"
                       "\n4. Update patient visit"
                       "\n5. View existing patient record"
                       "\nSelected option: ")
        if option == "1":
            create_patient()
        elif option == "2":
            add_new_visit()
        elif option == "3":
            view_patient_history()
        else:
            print("Please select a valid option.")


if __name__ == "__main__":
    dic = {'name': 'name'}
    gui()

    # encoded_data, hashed_data = prepare_request(json.dumps(dic))
    # config = configparser.ConfigParser()
    # config.read("config.ini")
    # public_key = RSA.import_key(config['DYNAMIC']['PHYSICIAN_PUBLIC_KEY'])
    # try :
    #     pkcs1_15.new(public_key).verify(hashed_data,encoded_data)
    #     print("OK")
    # except (ValueError,TypeError) :
    #     print("NOT OK")
    #  Decryption Code
    # decryptor = PKCS1_OAEP.new(user_private_key)
    # original_key = decryptor.decrypt(encrypted_symmetric_key)
    # print(original_key == symmetric_key)
    # decrypt the symmetric key
    # cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce=nonce)
    # plaintext = cipher.decrypt(encrypted_data)
    # print(plaintext)
    # prepare_request(json.dumps(dic))
