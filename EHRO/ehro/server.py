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

async def generic_error_handler(ex, req, resp, params):
    if not isinstance(ex, HTTPError):
        raise ex
    else:
        raise ex


if __name__ == "__main__":
    app = falcon.asgi.App()
    app.add_route('/create_physician', api.CreatePhysician())
    # app.add_route('/create_patient', api.CreatePatient())
    # app.add_route('/update_patient', api.UpdatePatient())
    # app.add_route('/create_patient_visit', api.CreatePatientVisit())
    # app.add_route('/update_patient_visit', api.UpdatePatientVisit())
    # app.add_route('/view_patient_history', api.ViewPatientHistory())
    app.add_error_handler(Exception, generic_error_handler)
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    uvicorn.run(app, host=host_ip, port=5000,)

