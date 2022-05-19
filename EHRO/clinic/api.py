# Falcon is the main framework used to implement the generic microservice.
# Falcon docs: https://falcon.readthedocs.io/en/stable/user/index.html
import json

import falcon
import falcon.asgi

from paths import CLINICS_PATH

class CreatePhysician:
    async def on_post(self, req, resp):
        clinic = json.load(open(CLINICS_PATH))
        # Receiving the request body.
        # request = await req.get_media()


        # resp.status = falcon.HTTP_200
        # resp.media = {"msg": "I am alive :)"}

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

