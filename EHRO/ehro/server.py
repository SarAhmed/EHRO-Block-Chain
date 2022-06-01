import socket

import falcon.asgi
# Uvicorn is an ASGI server in which Falcon runs and provides its functionality.
# Falcon needs this because Falcon does not come with its own server but it focuses on handling the APIs.
# Uvicorn docs: https://www.uvicorn.org/
import uvicorn

# The api file used to store all endpoints
from falcon import HTTPError, HTTPInternalServerError
from Cryptodome.PublicKey import RSA
import json
import api
import argparse
import configparser
from block_chain import Block_Chain
from block import Block
from paths import EHRO_PATH, CONFIG_PATH, PHYSICICANS_PATH


async def generic_error_handler(ex, req, resp, params):
    if not isinstance(ex, HTTPError):
        raise ex
    else:
        raise ex


def init_block_chain():
    block_chain = json.load(open(EHRO_PATH))
    if block_chain == {}:
        return Block_Chain()
    # construct the old block chain object from the dict old_block_chain
    chain = []
    for block in block_chain['chain']:
        curr_block = Block()
        curr_block.hashed_data = block['hashed_data']
        curr_block.hashed_previous_block = block['hashed_previous_block']
        curr_block.index = block['index']
        curr_block.previous_block = block['previous_block']
        curr_block.previous_patient_record = block['previous_patient_record']
        chain.append(curr_block)

    block_chain_obj = Block_Chain()
    block_chain_obj.chain = chain
    block_chain_obj.hashes_map = block_chain['hashes_map']
    block_chain_obj.last_index = block_chain['last_index']
    block_chain_obj.patient_map = block_chain['patient_map']
    return block_chain_obj



if __name__ == "__main__":
    block_chain = init_block_chain()
    app = falcon.asgi.App()
    app.add_route('/create_physician', api.CreatePhysician())
    app.add_route('/create_patient', api.CreateRecord(block_chain))
    app.add_route('/create_patient_visit', api.CreateRecord(block_chain))
    app.add_route('/update_patient', api.CreateRecord(block_chain))
    app.add_route('/update_patient_visit', api.CreateRecord(block_chain))
    # app.add_route('/view_patient_history', api.CreateRecord())

    app.add_error_handler(Exception, generic_error_handler)
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    uvicorn.run(app, host=host_ip, port=5000,)

