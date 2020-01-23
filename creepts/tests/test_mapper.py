import os

os.environ['ACCOUNT_ADDRESS'] = "0x760841c050d07d3f74139154284d1cd8b5afa9c6"
import unittest
import json
from creepts.dispatcher.contract import Contract
from creepts.mapping.mapper import Mapper
from creepts.model.tournament import TournamentPhase

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'instance_samples/instance_step_7.json')

class TestMapper(unittest.TestCase):

    def test_mapper(self):
        mapper = Mapper()

        with open(TESTDATA_FILENAME) as json_file:
            json_data = json.load(json_file)

        dapp = Contract(json_data)
        tournament = mapper.to_tournament(dapp)

        self.assertEqual(tournament.id, 7)
        self.assertEqual(tournament.phase, TournamentPhase.ROUND)
        self.assertEqual(tournament.currentRound, 0)
        self.assertEqual(tournament.lastRound, 0)
        self.assertEqual(tournament.deadline, '2020-01-21T22:56:09+00:00')
        self.assertEqual(tournament.map, 'original')
        self.assertEqual(tournament.name, 'saturday one')
        self.assertEqual(tournament.currentOpponent, None)
        self.assertEqual(tournament.winner, None)

if __name__ == '__main__':
    unittest.main()
