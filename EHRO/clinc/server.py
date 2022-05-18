# Falcon is the main framework used to implement the generic microservice.
# Falcon docs: https://falcon.readthedocs.io/en/stable/user/index.html
import falcon.asgi
# Uvicorn is an ASGI server in which Falcon runs and provides its functionality.
# Falcon needs this because Falcon does not come with its own server but it focuses on handling the APIs.
# Uvicorn docs: https://www.uvicorn.org/
import uvicorn
# The socket library is used to get the hostname to run uvicorn on the public IP not local IP
# socket docs: https://docs.python.org/3/library/socket.html
import socket
# The api file used to store all endpoints
import api


class Server:
    def __init__(self):
        pass
        # self.resource = resource.Resource()


if __name__ == "__main__":
    app = falcon.asgi.App()
    server = Server()
    # resource = service.resource
    # log = resource.log
    # app.add_route('/log', log)
    app.add_route('/health', api.CreatePhysician())
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    uvicorn.run(app, host=host_ip, port=8000)
