import os

os.environ['ACCOUNT_ADDRESS'] = "0x760841c050d07d3f74139154284d1cd8b5afa9c6"
#Dummy value
os.environ['CONTRACTS_DIR'] = "/"
import unittest
import json
from creepts.dispatcher.contract import Contract
from creepts.mapping.mapper import Mapper
from creepts.model.tournament import TournamentPhase

class TestMapper(unittest.TestCase):

    def test_mapper_round(self):
        mapper = Mapper()

        filename = os.path.join(os.path.dirname(__file__), 'instance_samples/instance_step_7.json')
        with open(filename) as json_file:
            json_data = json.load(json_file)

        dapp = Contract(json_data)
        tournament = mapper.to_tournament(dapp)

        self.assertEqual(tournament.id, 7)
        self.assertEqual(tournament.phase, TournamentPhase.ROUND)
        self.assertEqual(tournament.currentRound, 0)
        self.assertEqual(tournament.lastRound, 0)
        self.assertEqual(tournament.deadline.isoformat(), '2020-01-21T22:56:09+00:00')
        self.assertEqual(tournament.map, 'original')
        self.assertEqual(tournament.name, 'saturday one')
        self.assertEqual(tournament.currentOpponent, None)
        self.assertEqual(tournament.winner, None)

    def test_mapper_end(self):
        mapper = Mapper()

        filename = os.path.join(os.path.dirname(__file__), 'instance_samples/instance_step_8.json')
        with open(filename) as json_file:
            json_data = json.load(json_file)

        dapp = Contract(json_data)
        tournament = mapper.to_tournament(dapp)

        self.assertEqual(tournament.id, 8)
        self.assertEqual(tournament.phase, TournamentPhase.END)
        self.assertEqual(tournament.currentRound, 0)
        self.assertEqual(tournament.lastRound, 0)
        self.assertEqual(tournament.deadline, None)
        self.assertEqual(tournament.map, 'original')
        self.assertEqual(tournament.name, 'the perfect one')
        self.assertEqual(tournament.currentOpponent, None)
        self.assertEqual(tournament.winner, '0x3a0afba9a89cf64dd22a570d833f5da04f3020b6')

if __name__ == '__main__':
    unittest.main()
