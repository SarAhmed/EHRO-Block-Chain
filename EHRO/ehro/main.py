import json
from Cryptodome.PublicKey import RSA
import configparser

from block_chain import Block_Chain
from block import Block
from paths import EHRO_PATH, CONFIG_PATH, PHYSICICANS_PATH


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

def init_ehro_keys():
    key = RSA.generate(2048)
    private_key = key.export_key().decode('utf-8')
    public_key = key.public_key().export_key().decode('utf-8')
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    config.set("STATIC", "EHRO_PUBLIC_KEY", public_key)
    config.set("STATIC", "EHRO_PRIVATE_KEY", private_key)


# should be wrapped to class EHRO with only block chain attribute in addition to the following api calls
# with the init() for the ehro and block chain and the init() for the PK and PR_K only called once.
# def add_physician():
#     pass
#
# def add_visit(block_chain):
#     pass
#
# def add_patient(block_chain):
#     pass

def run_EHRO():
    init_ehro_keys()
    block_chain = init_block_chain()
    print("WELCOME TO EHR SYSTEM !")
    # TODO : continue the simulation of EHRO



if __name__ == '__main__':
    # bc = Block_Chain()
    # bc.add_block(1,1,"aman")
    # bc.add_block(1,1,"rafat")
    # object = json.loads(bc.toJSON())
    # k = json.loads(bc.get_patient_history(1,1)[0].toJSON())
    # print(type(object))
    # test = json.load(open(EHRO_PATH))
    # print(test['hashes_map']['aman'])
    bc = init_block_chain()
    bc.add_block(1,1,"aman")
    bc.add_block(1,1,"rafat")
    print(bc.patient_map['1']['1'])


