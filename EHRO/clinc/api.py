# Falcon is the main framework used to implement the generic microservice.
# Falcon docs: https://falcon.readthedocs.io/en/stable/user/index.html
import falcon
import falcon.asgi


class CreatePhysician:
    async def on_get(self, req, resp):
        # Receiving the request body.
        # request = await req.get_media()
        resp.status = falcon.HTTP_200
        resp.media = {"msg": "I am alive :)"}
