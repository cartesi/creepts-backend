import falcon

TESTDATA_FILENAME='instance.json'

class InstanceResource(object):
    def on_get(self, req, resp):
        with open(TESTDATA_FILENAME) as json_file:
            resp.body = json_file.read()

        resp.status = falcon.HTTP_200 

app = falcon.API()

app.add_route('/', InstanceResource())
