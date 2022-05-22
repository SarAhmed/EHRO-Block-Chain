import json


class Block:
    def __init__(self,index = -1, hashed_data = None, previous_patient_record_index = -1, hashed_previous_block = None):
        # self.patient_username = patient_username
        # self.clinic_id = clinic_id
        self.index = index
        self.hashed_data = hashed_data
        self.previous_block = index - 1
        # the very first initial record in case of new added patient to the block chain will be -1
        self.previous_patient_record = previous_patient_record_index
        # hash of the whole previous block
        self.hashed_previous_block = hashed_previous_block


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
