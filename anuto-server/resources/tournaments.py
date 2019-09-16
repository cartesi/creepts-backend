import falcon

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
            raise falcon.HTTPInternalServerError("Failed retrieving sample response")

