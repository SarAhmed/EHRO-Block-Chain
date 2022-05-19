# Falcon is the main framework used to implement the generic microservice.
# Falcon docs: https://falcon.readthedocs.io/en/stable/user/index.html
import json

import falcon
import falcon.asgi

from paths import CLINICS_PATH

class CreatePhysician:
    async def on_post(self, req, resp):
        body = await req.get_medi()
        clinic_json = json.load(open(CLINICS_PATH))
        for physician in clinic_json["staff"]:
            if physician["username"] == body["username"]:
                resp.status = falcon.HTTP_400
                resp.media = {"msg": "The chosen username is already in use."}
        clinic_json["staff"].append(body)
        with open("DB/clinic.json", "w") as outfile:
            outfile.write(clinic_json)
        # Send to EHRO the public key and id.
        resp.status = falcon.HTTP_200
        resp.media = {"msg": "The registration was successful."}
class CreatePatient:
    async def on_post(self, req, resp):
        pass


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

