import base64
import configparser
import json

import falcon
import falcon.asgi
from Cryptodome.Cipher import PKCS1_OAEP, AES
from Cryptodome.Hash import SHA3_256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pkcs1_15
from paths import PHYSICICANS_PATH


def bytes_to_str(bytes):
    return base64.b64encode(bytes).decode('utf-8')


def str_to_bytes(input_str):
    return base64.b64decode(bytes(input_str,'utf-8'))


def get_physician_PK(clinic_id, username):
    physician_json = json.load(open(PHYSICICANS_PATH))
    return physician_json[clinic_id][username]



def get_physician_data(encrypted_clinic_id, encrypted_username,ehro_private_key ):
    # cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce=str_to_bytes(nonce))
    # username = cipher.decrypt(str_to_bytes(encrypted_username))
    # clinic_id = cipher.decrypt(str_to_bytes(encrypted_clinic_id))
    # private_key = RSA.import_key(ehro_private_key)
    config = configparser.ConfigParser()
    config.read("config.ini")
    private_key = RSA.import_key(config['STATIC']['EHRO_PRIVATE_KEY'])
    decryptor = PKCS1_OAEP.new(private_key)
    username = decryptor.decrypt(str_to_bytes(encrypted_username))
    clinic_id = decryptor.decrypt(str_to_bytes(encrypted_clinic_id))
    return clinic_id.decode("utf-8"), username.decode("utf-8")



def get_patient_username(plaintext):
    plaintext_str = plaintext.decode('utf-8')
    plaintext_json = json.loads(plaintext_str)
    return plaintext_json["username"]


def prepare_response(block_chain, payload, encrypted_username, encrypted_clinic_id):
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
        pkcs1_15.new(physician_public_key).verify(hash_obj, str_to_bytes(payload['signed_data']))
        # return json.loads(plaintext.decode('utf-8'))
        # print(type(get_patient_username(plaintext)), get_patient_username(plaintext))
        # print(type(clinic_id), clinic_id)
    except (ValueError,TypeError) :
        # print("not ok")
        return False
    block_chain.add_block(get_patient_username(plaintext), clinic_id, payload['signed_data'])
    # print("all is ok")
    return True


class CreatePhysician:

    async def on_post(self, req, resp):
        body = await req.get_media()
        body = json.loads(body)
        physician_json = json.load(open(PHYSICICANS_PATH))
        clinic_id = body["payload"]["clinic_id"]
        physician_username = body["payload"]["physician"]
        physician_public_key = body["payload"]["physician_public_key"]
        # {
        #     physician:"username",
        #     clinic_id:"id",
        #     physician_public_key:"key"
        # }
        if clinic_id not in physician_json:
            physician_json[clinic_id] = {}
        physician_json[clinic_id][physician_username] = physician_public_key
        with open(PHYSICICANS_PATH, "w") as outfile:
            outfile.write(json.dumps(physician_json, indent=4))

        resp.status = falcon.HTTP_200
        config = configparser.ConfigParser()
        config.read("config.ini")

        resp.media = {"msg": "The registration was successful.",
                      "payload": {"ehro_public_key": config["STATIC"]["ehro_public_key"]}}


class CreateRecord:
    def __init__(self,block_chain):
        self.block_chain = block_chain

    async def on_post(self, req, resp):
        body = await req.get_media()
        body = json.loads(body)
        # payload = {
        #     "encrypted_symmetric_key": bytes_to_str(encrypted_symmetric_key),
        #     "signed_data": bytes_to_str(signed_hashed_data),
        #     "encrypted_data": bytes_to_str(encrypted_data),
        #     "nonce": bytes_to_str(nonce)
        # }
        #
        payload = body["payload"]
        # {
        #     physician:"username",
        #     clinic_id:"id",
        #     physician_public_key:"key"
        # }
        response = prepare_response(self.block_chain, payload, body["encrypted_username"], body["encrypted_clinic_id"])
        if response :
            resp.status = falcon.HTTP_200
            resp.media = {"msg": "Record added successfully !."}
        else :
            resp.status = falcon.HTTP_400
            resp.media = {"msg": "The verification failed."}
