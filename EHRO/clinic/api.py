# Falcon is the main framework used to implement the generic microservice.
# Falcon docs: https://falcon.readthedocs.io/en/stable/user/index.html
import configparser
import json

import falcon
import falcon.asgi
import requests

import util
from paths import CLINICS_PATH


class CreatePhysician:
    def __init__(self, public_key):
        self.clinic_public_key = public_key

    async def on_post(self, req, resp):
        body = await req.get_media()
        body = json.loads(body)
        clinic_json = json.load(open(CLINICS_PATH))
        for physician in clinic_json["staff"]:
            if physician["username"] == body["username"]:
                resp.status = falcon.HTTP_400
                resp.media = {"msg": "The chosen username is already in use."}
                return
        clinic_json["staff"].append(body)
        with open("DB/clinic.json", "w") as outfile:
            outfile.write(json.dumps(clinic_json, indent=4))

        config = configparser.ConfigParser()
        config.read("config.ini")
        request_body = json.dumps({"payload": {
            "physician": body["username"],
            "clinic_id": config["STATIC"]["clinic_id"],
            "physician_public_key": body["public_key"]
        }
        }, indent=4, sort_keys=True, default=str)
        response = requests.post("http://172.17.64.1:5000" + "/create_physician", json=request_body)
        response_json = json.loads(response.text)

        util.write_ehro_key_in_config(response_json["payload"]["ehro_public_key"])

        resp.status = falcon.HTTP_200
        resp.media = {"msg": "The registration was successful.",
                      "payload": {"clinic_public_key": self.clinic_public_key}}


# payload = {
#        "encrypted_symmetric_key": encrypted_symmetric_key, //encrypted using public key of clinic
#        "signed_data": signed_hashed_data, // signed using private key of phyisician
#        "encrypted_data" : encrypted_data, // encrypted data using the symmetric key
#        "nonce" : nonce // nonce used in the AES encryption --> look at the physician.py main
#    }
#    request_body = {
#        "encrypted_username": encrypted_username, // encrypted using the clinic public key
#        "encrypted_password": encrypted_password,
#        "payload": payload
#    }
class CreatePatient:
    async def on_post(self, req, resp):
        body = await req.get_media()
        body = json.loads(body)
        physician_username = util.decrypt_using_clinic_private_key(body["encrypted_username"]).decode('utf-8')
        physician_password = util.decrypt_using_clinic_private_key(body["encrypted_password"]).decode('utf-8')
        if not util.validate_credentials(physician_username, physician_password):
            resp.status = falcon.HTTP_400
            resp.media = {"msg": "Physician credentials are invalid."}
            return

        payload = body["payload"]
        symmetric_key = util.decrypt_using_clinic_private_key(payload["encrypted_symmetric_key"])

        data = util.decrypt_using_AES_key(payload["encrypted_data"], symmetric_key, payload["nonce"]).decode("utf-8")
        if not util.validate_patient_not_exists(data):
            resp.status = falcon.HTTP_400
            resp.media = {"msg": "A patient with the provided username already exists. Please choose another username."}
            return

        encrypted_symmetric_key_ehro = util.encrypt_using_ehro_public_key(symmetric_key)
        request_body_to_ehro = json.dumps({
            "encrypted_username": util.bytes_to_str(util.encrypt_using_ehro_public_key(bytes(physician_username, "utf-8"))),
            "encrypted_clinic_id": util.bytes_to_str(util.encrypt_using_ehro_public_key(bytes(util.get_clinic_id(), "utf-8"))),
            "payload": {
                "encrypted_symmetric_key": util.bytes_to_str(encrypted_symmetric_key_ehro),
                "signed_data": payload["signed_data"],
                "encrypted_data": payload["encrypted_data"],
                "nonce": payload["nonce"]
            }
        }, indent=4, sort_keys=True, default=str)

        response = requests.post("http://172.17.64.1:5000" + "/create_patient", json=request_body_to_ehro)
        if not response:
            resp.status = falcon.HTTP_400
            resp.media = {"msg": "The data is corrupted."}
            return

        util.add_to_database("patients", data)
        util.add_req_to_database(request_body_to_ehro,  payload["signed_data"])
        resp.status = falcon.HTTP_200
        resp.media = {"msg": "Patient added successfully."}


class UpdatePatient:
    async def on_post(self, req, resp):
        pass


class CreatePatientVisit:
    async def on_post(self, req, resp):
        pass


class UpdatePatientVisit:
    async def on_post(self, req, resp):
        pass


class ViewPatientHistory:
    async def on_get(self, req, resp):
        pass
