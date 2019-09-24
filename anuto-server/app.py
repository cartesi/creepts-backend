import falcon
from falcors import CORS
from resources.tournaments import Tournaments

cors = CORS(allow_all_origins=True)

api = falcon.API(middleware=[cors.middleware])
api.add_route('/tournaments', Tournaments())
api.add_route('/tournaments/{tour_id}', Tournaments(), suffix='single')
