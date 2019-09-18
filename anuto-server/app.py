import falcon
from resources.tournaments import Tournaments

api = falcon.API()
api.add_route('/tournaments', Tournaments())
api.add_route('/tournaments/{tour_id}', Tournaments(), suffix='single')
