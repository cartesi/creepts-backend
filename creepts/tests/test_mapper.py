import os
import unittest
import json
from datetime import datetime
from creepts.dispatcher.contract import Contract
from creepts.mapping.mapper import Mapper
from creepts.model.tournament import TournamentPhase

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'instance_samples/instance_step_11_pretty.json')

class TestMapper(unittest.TestCase):

    def test_mapper(self):
        mapper = Mapper()

        with open(TESTDATA_FILENAME) as json_file:
            json_data = json.load(json_file)

        dapp = Contract(json_data)
        tournament = mapper.to_tournament(dapp)

        self.assertEqual(tournament.id, 11)
        self.assertEqual(tournament.phase, TournamentPhase.ROUND)
        self.assertEqual(tournament.currentRound, 1)
        self.assertEqual(tournament.lastRound, 0)
        self.assertEqual(tournament.deadline, datetime(2019, 12, 26, 21, 49, 37))
        # self.assertEqual(tournament.currentOpponent, None)
        self.assertEqual(tournament.winner, None)

if __name__ == '__main__':
    unittest.main()
