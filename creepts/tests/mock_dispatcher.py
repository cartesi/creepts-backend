"""
Copyright 2020 Cartesi Pte. Ltd.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import falcon
import logging
import sys
import json

#Response files name template
TESTDATA_FILENAME_BASE='instance_samples/instance_step_{}.json'
#Min and max index of response files
TESTDATA_SIZE=9

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
            LOGGER.debug("Not a JSON")
            raise falcon.HTTPBadRequest(description="Provide a valid JSON as payload for this method")
        if 'application/json' not in req.content_type:
            LOGGER.debug("'application/json' header not set")
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
                    LOGGER.debug("Instance index {} was requested".format(instance_index))

        #Return the index desired if any
        if (instance_index != None):
            if instance_index < TESTDATA_SIZE:
                with open(TESTDATA_FILENAME_BASE.format(instance_index)) as json_file:
                    #Return the desired instance
                    resp.body = json_file.read()
                    resp.status = falcon.HTTP_200
                    LOGGER.debug("Returning json for instance {}".format(instance_index))
                    return
            else:
                #No instance for the provided index
                LOGGER.debug("No instances with provided index {}".format(instance_index))
                raise falcon.HTTPNotFound(description="There are no instances with the provided index: {}".format(instance_index))

        #No instance index provided, return the index list
        LOGGER.debug("Returning instances list")
        resp.body = json.dumps([i for i in range(0, TESTDATA_SIZE)])
        resp.status = falcon.HTTP_200
        return

    def on_post(self, req, resp):
        LOGGER.debug("Request received:")
        LOGGER.debug(req.media)

        resp.status = falcon.HTTP_200

app = falcon.API()

app.add_route('/', InstanceResource())
