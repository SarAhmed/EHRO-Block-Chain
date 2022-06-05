import json

from Cryptodome.Cipher import PKCS1_OAEP, AES
from Cryptodome.Hash import SHA3_256
from Cryptodome.PublicKey import RSA
import configparser

from Cryptodome.Signature import pkcs1_15
from block_chain import Block_Chain
from server import init_block_chain
from block import Block
from termcolor import colored
import requests
from paths import EHRO_PATH, CONFIG_PATH, PHYSICICANS_PATH


# def init_block_chain():
#     block_chain = json.load(open(EHRO_PATH))
#     if block_chain == {}:
#         return Block_Chain()
#     # construct the old block chain object from the dict old_block_chain
#     chain = []
#     for block in block_chain['chain']:
#         curr_block = Block()
#         curr_block.hashed_data = block['hashed_data']
#         curr_block.hashed_previous_block = block['hashed_previous_block']
#         curr_block.index = block['index']
#         curr_block.previous_block = block['previous_block']
#         curr_block.previous_patient_record = block['previous_patient_record']
#         chain.append(curr_block)
#
#     block_chain_obj = Block_Chain()
#     block_chain_obj.chain = chain
#     block_chain_obj.hashes_map = block_chain['hashes_map']
#     block_chain_obj.last_index = block_chain['last_index']
#     block_chain_obj.patient_map = block_chain['patient_map']
#     return block_chain_obj
from EHRO.ehro.api import get_physician_data, get_physician_PK, str_to_bytes


def init_ehro_keys():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if config["STATIC"]["EHRO_PUBLIC_KEY"] != "N/A":
        return
    key = RSA.generate(2048)
    private_key = key.export_key().decode('utf-8')
    public_key = key.public_key().export_key().decode('utf-8')
    config.set("STATIC", "EHRO_PUBLIC_KEY", public_key)
    config.set("STATIC", "EHRO_PRIVATE_KEY", private_key)


# should be wrapped to class EHRO with only block chain attribute in addition to the following api calls
# with the init() for the ehro and block chain and the init() for the PK and PR_K only called once.
def add_physician():
    pass


def add_visit(block_chain):
    pass


def add_patient(block_chain):
    pass



def prepare_response(signed_data, payload, encrypted_username, encrypted_clinic_id):
    config = configparser.ConfigParser()
    config.read("config.ini")
    ehro_private_key = RSA.import_key(config['STATIC']['EHRO_PRIVATE_KEY'])
    decryptor = PKCS1_OAEP.new(ehro_private_key)
    symmetric_key = decryptor.decrypt(str_to_bytes(payload['encrypted_symmetric_key']))

    clinic_id, username = get_physician_data(encrypted_clinic_id, encrypted_username, ehro_private_key)
    print(clinic_id, username)

    cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce = str_to_bytes(payload['nonce']))
    plaintext = cipher.decrypt(str_to_bytes(payload['encrypted_data']))
    # plaintext_bytes = bytes(plaintext,'utf-8')
    hash_obj = SHA3_256.new()
    hash_obj.update(plaintext)
    physician_public_key =  RSA.import_key(get_physician_PK(clinic_id, username))
    print(physician_public_key)
    try :
        pkcs1_15.new(physician_public_key).verify(hash_obj, str_to_bytes(signed_data))
        # return json.loads(plaintext.decode('utf-8'))
        # print(type(get_patient_username(plaintext)), get_patient_username(plaintext))
        # print(type(clinic_id), clinic_id)
    except (ValueError,TypeError) :
        # print("not ok")
        return False
    # print("all is ok")
    print("Hash is verified")
    return True


def verify_hash(requested_hash):
    params ={"requested_hash": requested_hash}
    response = requests.get("http://127.0.0.1:8000/verify_hash",params=params)
    if response.status_code != 200:
        return False
    #TODO Test the response.json() and check that it returns the body of the response
    body = response.json()
    is_data_verified = prepare_response(requested_hash, body["payload"], body["encrypted_username"], body["encrypted_clinic_id"])
    if is_data_verified:
        print(colored("Hash is verified correctly!","Green"))
    else:
        print(colored("Hash is incorrect!","red"))

def run_EHRO():
    init_ehro_keys()
    block_chain = init_block_chain()
    print("WELCOME TO EHR SYSTEM !")
    # TODO : continue the simulation of EHRO

def gui():
    while True:
        print("To verify, please enter the following information to retrieve hashes")
        clinic_id = input("Clinic Id:")
        patient_username = input("Patient Username:")
        block_chain = init_block_chain()
        records =[]
        try:
            records = block_chain.get_patient_history(patient_username,clinic_id)
        except(ValueError,TypeError,KeyError):
            print(colored("Please enter correct patient username and clinic ID!","red"))
            continue
        print("Choose which record you want to verify:")
        for i in range(0, len(records)):
            print(i+1,": ",records[i])
        choice = 0
        while True:
            choice_str = input("Record number:")
            choice = int(choice_str)-1 if choice_str.isnumeric() else -1
            if choice<0 or choice>=len(records):
                print(colored("Please enter a valid record number","red"))
            else:
                break
        verify_hash(records[choice])





if __name__ == '__main__':
    # bc = Block_Chain()
    # bc.add_block(1,1,"aman")
    # bc.add_block(1,1,"rafat")
    # object = json.loads(bc.toJSON())
    # k = json.loads(bc.get_patient_history(1,1)[0].toJSON())
    # print(type(object))
    # test = json.load(open(EHRO_PATH))
    # print(test['hashes_map']['aman'])
    # bc = init_block_chain()
    # bc.add_block(1,1,"aman")
    # bc.add_block(1,1,"rafat")
    # print(bc.patient_map['1']['1'])
    gui()


