# Falcon is the main framework used to implement the generic microservice.
# Falcon docs: https://falcon.readthedocs.io/en/stable/user/index.html
# The socket library is used to get the hostname to run uvicorn on the public IP not local IP
# socket docs: https://docs.python.org/3/library/socket.html
import socket

import falcon.asgi
# Uvicorn is an ASGI server in which Falcon runs and provides its functionality.
# Falcon needs this because Falcon does not come with its own server but it focuses on handling the APIs.
# Uvicorn docs: https://www.uvicorn.org/
import uvicorn

# The api file used to store all endpoints
from falcon import HTTPError, HTTPInternalServerError

import api
import argparse
import configparser


class Server:
    def __init__(self):
        pass
        # self.resource = resource.Resource()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--clinic_id', required=True)
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read("config.ini")
    config["STATIC"]["clinic_id"] = args.clinic_id
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

async def generic_error_handler(ex, req, resp, params):
    if not isinstance(ex, HTTPError):
        raise ex
    else:
        raise ex


if __name__ == "__main__":
    parse_arguments()
    app = falcon.asgi.App()
    server = Server()
    app.add_route('/create_physician', api.CreatePhysician())
    app.add_route('/create_patient', api.CreatePatient())
    app.add_route('/update_patient', api.UpdatePatient())
    app.add_route('/create_patient_visit', api.CreatePatientVisit())
    app.add_route('/update_patient_visit', api.UpdatePatientVisit())
    app.add_route('/view_patient_history', api.ViewPatientHistory())
    app.add_error_handler(Exception, generic_error_handler)
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    uvicorn.run(app, host=host_ip, port=8000,)
