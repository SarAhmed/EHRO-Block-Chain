import configparser
import json

import falcon
import falcon.asgi
from paths import PHYSICICANS_PATH

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


def CreatePatient:
    pass