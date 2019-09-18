import falcon
import json
import traceback

class Tournaments:
    def on_get(self, req, resp):
        """
        Handles the get method for Tournaments resource

        Parameters
        ----------
        req : falcon.Request
            Contains the request, including query string parameters:
            - limit: int
                Maximum number of tournaments to return (default applies if not specified)
            - offset: int
                Pagination offset, 10 returns 10th element up to (10+limit)th element
            - phase: str -> Enum:"commit" "reveal" "round" "end"
                Filter tournaments by phase
            - me: bool
                Filter tournaments which I am participating
            - sort_by: str -> Enum:"playerCount" "deadline"
                Sort criteria of returned tournaments
            - order_by: str ->  Enum:"asc" "desc"
                Ascendent or descendent order of returned tournaments. Default is asc

        resp: falcon.Response
            This object is used to issue the response to this call it,
            if no error occurs, it should return a structure describing the
            tournaments similar to the one available in:
            <project_root>/reference/anuto/examples/tournaments.json

        Returns
        -------
        NoneType
            This method has no return
        """

        #Returning mocked response
        try:
            with open("../reference/anuto/examples/tournaments.json", 'r') as sample_tour_file:
                resp.body = sample_tour_file.read()
                resp.status = falcon.HTTP_200
        except:
            raise falcon.HTTPInternalServerError(description="Failed retrieving sample response")


    def on_get_single(self, req, resp, tour_id):
        """
        Handles the get method for a single Tournament

        Parameters
        ----------
        req : falcon.Request
            Contains the request

        resp: falcon.Response
            This object is used to issue the response to this call it,
            if no error occurs, it should return a structure describing the
            tournament similar to the one available in:
            <project_root>/reference/anuto/examples/tournament.json

        tour_id : str
            The id of the desired tournament

        Returns
        -------
        NoneType
            This method has no return
        """

        #Returning mocked response
        try:
            with open("../reference/anuto/examples/tournaments.json", 'r') as sample_tour_file:
                tournaments_json = sample_tour_file.read()
                tournaments_struct = json.loads(tournaments_json)

                if ("results" not in tournaments_struct.keys()):
                    raise falcon.HTTPInternalServerError(description="Malformed mocked tournaments file, no results entry")

                #Retrieving the desired tournament, or 404 if not found
                for tour in tournaments_struct["results"]:
                    if ("id" not in tour.keys()):
                        raise falcon.HTTPInternalServerError(description="Malformed mocked tournaments file, no id entry in tournament: \n{}".format(json.dumps(tour)))
                    if (tour["id"].strip() == tour_id.strip()):
                        resp.body = json.dumps(tour)
                        resp.status = falcon.HTTP_200
                        return

        except Exception as e:
            print("An exception happened:")
            print(e)
            print("Traceback:")
            print(traceback.format_exc())
            raise falcon.HTTPInternalServerError(description="Failed retrieving sample response")

        #No matches, return 404
        raise falcon.HTTPNotFound(description="No tournament with the provided id")

