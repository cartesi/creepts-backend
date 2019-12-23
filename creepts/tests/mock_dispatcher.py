import falcon
import logging
import sys

TESTDATA_FILENAME='instance.json'

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOGGER.addHandler(handler)

class InstanceResource(object):
    def on_get(self, req, resp):
        with open(TESTDATA_FILENAME) as json_file:
            resp.body = json_file.read()

        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        LOGGER.debug("Request received:")
        LOGGER.debug(req.media)

        resp.status = falcon.HTTP_200

app = falcon.API()

app.add_route('/', InstanceResource())
