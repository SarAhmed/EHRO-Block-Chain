import configparser
import json

from Cryptodome.PublicKey import RSA
from block import Block
from Cryptodome.Hash import SHA3_256
from paths import EHRO_PATH, CONFIG_PATH



class Block_Chain:
    def __init__(self):
        self.chain = []
        self.last_index = -1
        #  K : [patient_username,clinic_id], V : last_patient_record_index
        self.patient_map = {}
        # K : hashed_data, V : [patient_username,clinic_id]
        self.hashes_map = {}
        self.init_ehro_keys()

    def init_ehro_keys(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        if config["STATIC"]["EHRO_PUBLIC_KEY"] != "N/A":
            return
        key = RSA.generate(2048)
        private_key = key.export_key().decode('utf-8')
        public_key = key.public_key().export_key().decode('utf-8')
        config.set("STATIC", "EHRO_PUBLIC_KEY", public_key)
        config.set("STATIC", "EHRO_PRIVATE_KEY", private_key)


    def add_block(self,patient_username, patient_clinic_id, hashed_data):
        patient_username = str(patient_username)
        patient_clinic_id = str(patient_clinic_id)
        patient_last_block_index = -1
        # if (patient_username, patient_clinic_id) in self.patient_map :
        #     patient_last_block_index = self.patient_map[(patient_username,patient_clinic_id)]
        if patient_username in self.patient_map :
            if patient_clinic_id in self.patient_map[patient_username]:
                patient_last_block_index = self.patient_map[patient_username][patient_clinic_id]

        new_block = Block(self.last_index + 1, hashed_data)
        new_block.previous_patient_record = patient_last_block_index

        # compute the hash of the previous block
        if self.last_index != -1 :
            hash_last_block = SHA3_256.new()
            byte_obj = bytes(json.dumps(self.chain[self.last_index].toJSON()), 'utf-8')
            hash_last_block.update(byte_obj)
            new_block.hashed_previous_block = hash_last_block.hexdigest()

        self.last_index += 1
        self.chain.append(new_block)
        # self.patient_map[(patient_username,patient_clinic_id)] = self.last_index
        if patient_username not in self.patient_map:
            self.patient_map[patient_username] = {}
        self.patient_map[patient_username][patient_clinic_id] = self.last_index
        self.hashes_map[new_block.hashed_data] = (patient_username,patient_clinic_id)

        json_object = self.toJSON()
        with open(EHRO_PATH, "w") as outfile:
            outfile.write(json_object)


    def get_patient_history(self, patient_username, clinic_id):
        # patient_last_record_index = self.patient_map[(patient_username,clinic_id)]
        patient_last_record_index = self.patient_map[patient_username][ clinic_id]
        records = []
        while patient_last_record_index != -1:
            records.append(self.chain[patient_last_record_index])
            patient_last_record_index = self.chain[patient_last_record_index].previous_patient_record
        return records



    def get_patient_from_hash(self,hashed_data):
        return self.hashes_map[hashed_data] if hashed_data in self.hashes_map  else "THE RECORD DOES NOT EXISTS"

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)






if __name__ == '__main__':
    dict = {}
    dict[1] = 2
    print(dict[1])
