from physician import Physician
import configparser


def create_physician():
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")
    config = configparser.ConfigParser()
    config.read("config.ini")
    static = config['STATIC']
    physician_record = Physician(username, password, static['CLINIC_ID'])
    config.set("DYNAMIC", "PHYSICIAN_USERNAME", username)
    config.set("DYNAMIC", "PHYSICIAN_PASSWORD", password)
    config.set("DYNAMIC", "PHYSICIAN_PUBLIC_KEY", physician_record.public_key)
    config.set("DYNAMIC", "PHYSICIAN_PRIVATE_KEY", physician_record.private_key)
    with open('config.ini', 'w') as configfile:  # save
        config.write(configfile)
    # TODO : request to the clinic to update the staff record

def login():
    # verify the input credentials from the config file
    entered_username = input("Please enter your username: ")
    entered_password = input("Please enter your password: ")
    config = configparser.ConfigParser()
    config.read("config.ini")
    username = config['DYNAMIC']['physician_username']
    password = config['DYNAMIC']['physician_password']
    if username != entered_username or password != entered_password :
        print("The username or password is incorrect ")
        return False
    print("You are successfully logged in")
    return True


def create_patient():
    pass


def add_new_visit():
    pass


def view_patient_history():
    pass


def gui():
    print("Welcome to the public health care system")
    print("Please select your desired option: ")
    while True:
        option = input("1. Sign up \n2. Login \nSelected option: ")
        if option == "1":
            create_physician()
            break
        elif option == "2":
            if login():
                break
        else:
            print("Please select a valid option.")
    print("You are successfully logged in.")
    print("Please select your desired option: ")
    while True:
        option = input("1. Add new patient \n2. Add visit to an existing patient\n3. View existing patient record "
                       "\nSelected option: ")
        if option == "1":
            create_patient()
        elif option == "2":
            add_new_visit()
        elif option == "3":
            view_patient_history()
        else:
            print("Please select a valid option.")


if __name__ == "__main__":
    gui()
