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
    resp = requests.get("http://" + host_ip + ":8000/health")
    print(resp.text)

if __name__ == "__main__":
    test_resource()