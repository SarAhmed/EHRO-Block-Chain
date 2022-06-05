# This file will be used to test the implementation during implementation phase.
# The requests library is used to issue requests. It is mainly used to test our implementation.
# Requests docs: https://docs.python-requests.org/en/master/
import requests
import socket
import time


# The function contains the logic used to test the implementation of the resource route.
def test_resource():
    time.sleep(3)
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    body = {
    "clinic_id": "\"XXXXXXXX\"",
    "last_update_time": "2022-05-19 21:29:44.170761",
    "password": "1",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwTB567W8L1bhQl49izRJ\nSeq/8mC+FblERBsZdyVUBICAq0eVxHkpqYHhFActBXaPDau4gcSqzaTdQq9KTYL4\nb9UbTVpP9KXnNO0UKya6v2Aqzp6gyTc8NDyDZ0HhzSbsdJjewycFx747FG3Nv/qZ\n/Yw1j/GxukSubciHrn68lSOtabMrJO8raJQ1Zndo3cmuz8TrwMPlA7zsCqtIh9hT\nPOR6sLvG8b0C1+k9yjiVdwfPjMNlD0i2AvQ8RI7m/4yax5Yza4W2lycuyd2NUjLh\nVaS/TDYuBNmlDFJvSq0VGxadW5hPYbbYCHuXNNyCxQSTtScTVkr1px8+LCW0RFQ/\nCwIDAQAB\n-----END PUBLIC KEY-----",
    "username": "1"
}
    resp = requests.post("http://192.168.246.83:8000/create_physician",
                       json=body)
    print(resp.text)

if __name__ == "__main__":
    test_resource()