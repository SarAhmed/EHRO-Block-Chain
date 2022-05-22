# Falcon is the main framework used to implement the generic microservice.
# Falcon docs: https://falcon.readthedocs.io/en/stable/user/index.html
import json

import falcon
import falcon.asgi

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
        # TODO: Send to EHRO the public key and id.
        # config.set("STATIC", "ehro_public_key", ehro public key)
        # config.set("STATIC", "ehro_id", ehro id)
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
        body = json.loads(await req.get_media())
        physician_username = util.decrypt_using_clinic_private_key(body["encrypted_username"])
        physician_password = util.decrypt_using_clinic_private_key(body["encrypted_password"])
        if not util.validate_credentials(physician_username, physician_password):
            resp.status = falcon.HTTP_400
            resp.media = {"msg": "Physician credentials are invalid."}
            return

        payload = body["payload"]
        symmetric_key = util.decrypt_using_clinic_private_key(payload["encrypted_symmetric_key"])
        encrypted_symmetric_key_ehro = util.encrypt_using_ehro_public_key(symmetric_key)
        request_body_to_ehro = {
            "encrypted_username": util.encrypt_using_ehro_public_key(physician_username),
            "payload": {
                "encrypted_symmetric_key": encrypted_symmetric_key_ehro,
                "signed_data": payload["signed_data"],
                "encrypted_data": payload["encrypted_data"],
                "nonce": payload["nonce"]
            }
        }
        # TODO: Send to EHRO the request
        response = True  # TODO: response of the request sent to the EHRO
        if not response:
            resp.status = falcon.HTTP_400
            resp.media = {"msg": "The data is corrupted."}
            return

        data = util.decrypt_using_AES_key(payload["encrypted_data"], symmetric_key, payload["nonce"])
        util.add_to_database("patients", data)

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
