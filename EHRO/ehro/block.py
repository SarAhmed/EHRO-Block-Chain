class Block:
    def __init__(self,hashed_data, previous_block = None, previous_patient_record = None):
        # self.patient_username = patient_username
        # self.clinic_id = clinic_id
        self.hashed_data = hashed_data
        self.previous_block = previous_block
        self.previous_patient_record = previous_patient_record

