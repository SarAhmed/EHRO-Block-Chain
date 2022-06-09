import ast

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
import argparse
from termcolor import colored
import configparser
import json
from paths import CLINIC_IP
from paths import EHRO_IP


def toJSON(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def bytes_to_str(bytes):
    return base64.b64encode(bytes).decode('utf-8')


def str_to_bytes(input_str):
    return base64.b64decode(bytes(input_str,'utf-8'))


def prepare_request(obj):
    config = configparser.ConfigParser()
    config.read("config.ini")
    user_private_key = RSA.import_key(config['DYNAMIC']['PHYSICIAN_PRIVATE_KEY'])
    # TODO : change the used PK to the PK of the clinic
    clinic_public_key = RSA.import_key(config['STATIC']['CLINIC_PUBLIC_KEY'])
    obj = bytes(obj, 'utf-8')
    symmetric_key = get_random_bytes(32)

    hash_obj = SHA3_256.new()
    hash_obj.update(obj)

    signed_hashed_data = pkcs1_15.new(user_private_key).sign(hash_obj)

    encryptor = PKCS1_OAEP.new(clinic_public_key)
    encrypted_symmetric_key = encryptor.encrypt(symmetric_key)
    # print(type(encrypted_symmetric_key))
    aes_encryptor = AES.new(symmetric_key, AES.MODE_EAX)
    nonce = aes_encryptor.nonce
    encrypted_data= aes_encryptor.encrypt(obj)

    username = config['DYNAMIC']['PHYSICIAN_USERNAME']
    password = config['DYNAMIC']['PHYSICIAN_PASSWORD']
    encrypted_username = encryptor.encrypt(bytes(username,'utf-8'))
    encrypted_password =  encryptor.encrypt(bytes(password,'utf-8'))
    # formuate the object to be sent in the request body
    # decoded_symmetric_key = base64.b64encode(encrypted_symmetric_key).decode('utf-8')
    # decoded_signed_hashed_data = base64.b64encode(signed_hashed_data).decode('utf-8')
    # decoded_encrypted_data = base64.b64encode(encrypted_data).decode('utf-8')
    # decoded_nonce = base64.b64encode(nonce).decode('utf-8')
    # decoded_encrypted_username = base64.b64encode(encrypted_username).decode('utf-8')
    # decoded_encrypted_password = base64.b64encode(encrypted_password).decode('utf-8')
    payload = {
        "encrypted_symmetric_key": bytes_to_str(encrypted_symmetric_key),
        "signed_data": bytes_to_str(signed_hashed_data),
        "encrypted_data" : bytes_to_str(encrypted_data),
        "nonce" : bytes_to_str(nonce)
    }
    request_body = {
        "encrypted_username": bytes_to_str(encrypted_username),
        "encrypted_password": bytes_to_str(encrypted_password),
        "payload": payload
    }
    # request_body_string = json.dumps(request_body, indent=4, sort_keys=True,default=str)
    # request_body_string  = request_body
    return json.dumps(request_body)
    # return json.dumps(request_body,indent=4, sort_keys=True,default=str)

def prepare_response(payload):
    config = configparser.ConfigParser()
    config.read("config.ini")
    user_private_key = RSA.import_key(config['DYNAMIC']['PHYSICIAN_PRIVATE_KEY'])
    decryptor = PKCS1_OAEP.new(user_private_key)
    symmetric_key = decryptor.decrypt(str_to_bytes(payload['encrypted_symmetric_key']))
    cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce=str_to_bytes(payload['nonce']))
    plaintext = cipher.decrypt(str_to_bytes(payload['encrypted_data']))
    # plaintext_bytes = bytes(plaintext,'utf-8')
    hash_obj = SHA3_256.new()
    hash_obj.update(plaintext)
    clinic_public_key =  RSA.import_key(config['STATIC']['CLINIC_PUBLIC_KEY'])
    try :
        pkcs1_15.new(clinic_public_key).verify(hash_obj,str_to_bytes(payload['signed_data']))
        return json.loads(plaintext.decode('utf-8'))
    except (ValueError,TypeError) :
        return {"error": "SOURCE UNVERIFIABLE"}
        print(colored("SOURCE UNVERIFIABLE","red"))


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
    # print(physician_dict)
    request_body = json.dumps(physician_dict, indent=4, sort_keys=True,default=str)
    # {
    #     username:'username',
    #     password:'password',
    #     public_key: 'public_key',
    #     last_update_time: 'time'
    #     clinic_id:'clinic_id'
    # }
    # clinic_ip = socket.gethostbyname(config["STATIC"]["CLINIC_ID"])
    # print(request_body)
    response = requests.post(CLINIC_IP + "/create_physician", json=request_body)
    response_json = json.loads(response.text)
    if response.status_code != 200 :
        print(colored(response_json['msg'],"red"))
        return False
    # print(response_json)
    clinic_public_key = response_json['payload']['clinic_public_key']
    config.set("DYNAMIC", "PHYSICIAN_USERNAME", username)
    config.set("DYNAMIC", "PHYSICIAN_PASSWORD", password)
    config.set("DYNAMIC", "PHYSICIAN_PUBLIC_KEY", public_key)
    config.set("DYNAMIC", "PHYSICIAN_PRIVATE_KEY", private_key)
    config.set("STATIC", "CLINIC_PUBLIC_KEY", clinic_public_key)
    with open('config.ini', 'w') as configfile:  # save
        config.write(configfile)
    return True


def login():
    # verify the input credentials from the config file
    entered_username = input("Please enter your username: ")
    entered_password = input("Please enter your password: ")
    config = configparser.ConfigParser()
    config.read("config.ini")
    username = config['DYNAMIC']['physician_username']
    password = config['DYNAMIC']['physician_password']
    if username != entered_username or password != entered_password :
        print(colored("The username or password is incorrect ","red"))
        return False
    return True


def create_patient():
    new_patient_json = get_patient_info()
    request_body = prepare_request(new_patient_json)
    # print(type(request_body))
    # print(json.loads(request_body))
    config = configparser.ConfigParser()
    config.read("config.ini")
    # clinic_ip = socket.gethostbyname(config["STATIC"]["CLINIC_ID"])
    response = requests.post(CLINIC_IP + "/create_patient", json=request_body)
    response_json = json.loads(response.text)
    if response.status_code == 200:
        print(colored(response_json['msg'], 'green'))
    else:
        print(colored(response_json['msg'], 'red'))



def update_patient_info():
    current_patient_json = get_patient_info()
    request_body = prepare_request(current_patient_json)
    config = configparser.ConfigParser()
    config.read("config.ini")
    #clinic_ip = socket.gethostbyname(config["STATIC"]["CLINIC_ID"])
    response = requests.post(CLINIC_IP + "/update_patient", json=request_body)
    response_json = json.loads(response.text)
    if response.status_code == 200:
        print(colored(response_json['msg'],'green'))
    else:
        print(colored(response_json['msg'],'red'))



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
    # return json.dumps(new_patient.__dict__,indent=4, sort_keys=True, default=str)
    return new_patient.toJSON()

def add_new_visit():
    new_visit_json = get_visit_info()
    request_body = prepare_request(new_visit_json)
    config = configparser.ConfigParser()
    config.read("config.ini")
    # clinic_ip = socket.gethostbyname(config["STATIC"]["CLINIC_ID"])
    response = requests.post(CLINIC_IP + "/create_patient_visit", json=request_body)
    response_json = json.loads(response.text)
    if response.status_code == 200:
        print(colored(response_json['msg'], 'green'))
    else:
        print(colored(response_json['msg'], 'red'))


def update_visit():
    current_visit_json = get_visit_info(True)
    request_body = prepare_request(current_visit_json)
    config = configparser.ConfigParser()
    config.read("config.ini")
    # clinic_ip = socket.gethostbyname(config["STATIC"]["CLINIC_ID"])
    response = requests.post(CLINIC_IP + "/update_patient_visit", json=request_body)
    response_json = json.loads(response.text)
    if response.status_code == 200:
        print(colored(response_json['msg'], 'green'))
    else:
        print(colored(response_json['msg'], 'red'))

def get_visit_info(is_update = False):
    print("Please enter the following information")
    visit_id = None
    if is_update:
        visit_id = input("Visit ID: ")
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
                      reason_for_visit, pulse, temperature, glucose,blood_pressure, visit_id)
    return json.dumps(new_visit.__dict__,indent=4, sort_keys=True, default=str)


def view_patient_history():
    username = input("Username: ")
    config = configparser.ConfigParser()
    config.read("config.ini")
    # clinic_ip = socket.gethostbyname(config["STATIC"]["CLINIC_ID"])
    request_body = prepare_request(toJSON({"username":username}))
    response = requests.post(CLINIC_IP + "/view_patient_history",json=request_body)
    # print(response.json()["payload"])
    # resp= response.text.replace('/"')
    # print(response.text)
    # response_json = ast.literal_eval(response.text)
    # print(type(response_json))
    # response_json = json.loads(response.text)
    response_json = response.json()
    response_json = json.loads(response_json)
    # print(type(response_json))
    if response.status_code != 200:
        print(colored(response_json['msg'], "red"))
        return False
    data = prepare_response(response_json["payload"])
    if not "error" in data:
        print(toJSON(data))






def gui():
    print("Welcome to the public health care system")
    print("Please select your desired option: ")
    while True:
        option = input("1. Sign up \n2. Login \nSelected option: ")
        if option == "1":
            if create_physician() :
                break
        elif option == "2":
            if login():
                break
        else:
            print(colored("Please select a valid option.","red"))
    print(colored("You are successfully logged in.","green"))
    print("Please select your desired option: ")
    while True:
        option = input("1. Add new patient\n2. Update patient information \n3. Add visit to an existing patient"
                       "\n4. Update patient visit"
                       "\n5. View existing patient record"
                       "\nSelected option: ")
        if option == "1":
            create_patient()
        elif option == "2":
            update_patient_info()
        elif option == "3":
            add_new_visit()
        elif option == "4":
            update_visit()
        elif option == "5":
            view_patient_history()
        else:
            print("Please select a valid option.")

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--clinic_id', required=True)
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read("config.ini")
    config["STATIC"]["clinic_id"] = args.clinic_id
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    parse_arguments()
    gui()
    # dic = {'name': 'name'}
    # patient  = json.loads(prepare_request(get_patient_info()))
    # # print(type(patient))
    # config = configparser.ConfigParser()
    # config.read("../clinic/config.ini")
    # clinic_private_key = RSA.import_key(config['DYNAMIC']['CLINIC_PRIVATE_KEY'])
    # request_body = patient
    #
    # encrypted_symmetric_key = request_body['payload']['encrypted_symmetric_key']
    # # print(type(encrypted_symmetric_key))
    # decryptor = PKCS1_OAEP.new(clinic_private_key)
    # # encrypted_symmetric_key_bytes = bytes(encrypted_symmetric_key,'utf-8')
    # print(encrypted_symmetric_key)
    # print(type(encrypted_symmetric_key))
    # symmetric_key = decryptor.decrypt(base64.b64decode(bytes(encrypted_symmetric_key,'utf-8')))
    # print(symmetric_key)
    # cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce= str_to_bytes(request_body['payload']['nonce']))
    # plaintext = cipher.decrypt(str_to_bytes(request_body['payload']['encrypted_data']))
    # print(type(plaintext))
    # plaintext_bytes = plaintext
    # hash_obj = SHA3_256.new()
    # hash_obj.update(plaintext_bytes)
    # config = configparser.ConfigParser()
    # config.read("config.ini")
    # clinic_public_key = RSA.import_key(config['DYNAMIC']['physician_public_key'])
    #
    # try:
    #     pkcs1_15.new(clinic_public_key).verify(hash_obj, str_to_bytes(request_body['payload']['signed_data']))
    #     print(json.loads(plaintext.decode('utf-8')))
    # except (ValueError, TypeError):
    #     print("SOURCE UNVERIFIABLE")
    #
    # gui()
    #
    # encoded_data, hashed_data = prepare_request(json.dumps(dic))
    # config = configparser.ConfigParser()
    # config.read("config.ini")
    # public_key = RSA.import_key(config['DYNAMIC']['PHYSICIAN_PUBLIC_KEY'])
    # try :
    #     pkcs1_15.new(public_key).verify(hashed_data,encoded_data)
    #     print("OK")
    # except (ValueError,TypeError) :
    #     print("NOT OK")
    # # Decryption Code
    # decryptor = PKCS1_OAEP.new(user_private_key)
    # original_key = decryptor.decrypt(encrypted_symmetric_key)
    # print(original_key == symmetric_key)
    # #decrypt the symmetric key
    # cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce=nonce)
    # plaintext = cipher.decrypt(encrypted_data)
    # print(plaintext)
    # prepare_request(json.dumps(dic))
