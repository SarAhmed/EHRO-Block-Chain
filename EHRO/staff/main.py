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

    # formuate the object to be sent in the request body
    payload = {
        "encrypted_symmetric_key": encrypted_symmetric_key,
        "signed_data": signed_hashed_data,
        "encrypted_data" : encrypted_data,
        "nonce" : nonce
    }
    request_body = {
        "username": config['DYNAMIC']['PHYSICIAN_USERNAME'],
        "password": config['DYNAMIC']['PHYSICIAN_PASSWORD'],
        "payload": payload
    }

    return request_body


def create_physician():
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")
    config = configparser.ConfigParser()
    config.read("config.ini")
    static = config['STATIC']
    physician_record = Physician(username, password, static['CLINIC_ID'])
    # TODO : request to the clinic to update the staff record

    config.set("DYNAMIC", "PHYSICIAN_USERNAME", username)
    config.set("DYNAMIC", "PHYSICIAN_PASSWORD", password)
    config.set("DYNAMIC", "PHYSICIAN_PUBLIC_KEY", physician_record.public_key)
    config.set("DYNAMIC", "PHYSICIAN_PRIVATE_KEY", physician_record.private_key)
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


def update_patient_info():
    current_patient_json = get_patient_info()
    # TODO send the updated patient to the clinic

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
    return json.dumps(new_patient.__dict__)

def add_new_visit():
    new_visit_json = get_visit_info()
    #TODO send the new visit to the clinic


def update_visit():
    current_visit_json = get_visit_info()
    #TODO send the updated visit to the clinic

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
    return json.dumps(new_visit.__dict__)


def view_patient_history():
    pass


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
    # gui()

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
    prepare_request(json.dumps(dic))
