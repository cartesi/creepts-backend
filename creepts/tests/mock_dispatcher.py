import falcon
import logging
import sys
import json

#Response files name template
TESTDATA_FILENAME_BASE='instance_samples/instance_step_{}_pretty.json'
#Min and max index of reponse files
TESTDATA_SIZE=15

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOGGER.addHandler(handler)

class InstanceResource(object):
    def on_get(self, req, resp):
        #Making sure a json was sent in the request payload
        if not req.content_type:
            raise falcon.HTTPBadRequest(description="Provide a valid JSON as payload for this method")
        if 'application/json' not in req.content_type:
            raise falcon.HTTPUnsupportedMediaType(description="The payload must be sent in json format")

        #Getting the request payload json
        req_json = req.media

        instance_index = None

        #Checking if it has the information requesting an instance inside the payload
        if req_json:
            keys_method = getattr(req_json, "keys", None)
            if callable(keys_method):
                if "Instance" in req_json.keys():
                    #There is, getting it
                    instance_index = int(req_json["Instance"])

        #Return the index desired if any
        if (instance_index != None):
            if instance_index < TESTDATA_SIZE:
                with open(TESTDATA_FILENAME_BASE.format(instance_index)) as json_file:
                    #Return the desired instance
                    resp.body = json_file.read()
                    resp.status = falcon.HTTP_200
                    return
            else:
                #No instance for the provided index
                raise falcon.HTTPNotFound(description="There are no instances with the provided index: {}".format(instance_index))

        #No instance index provided, return the index list
        resp.body = json.dumps([i for i in range(0, TESTDATA_SIZE)])
        resp.status = falcon.HTTP_200
        return

    def on_post(self, req, resp):
        LOGGER.debug("Request received:")
        LOGGER.debug(req.media)

        resp.status = falcon.HTTP_200

app = falcon.API()

app.add_route('/', InstanceResource())
