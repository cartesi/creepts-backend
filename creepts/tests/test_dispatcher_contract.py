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

import os
import unittest
import json
from creepts.dispatcher.contract import Contract

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'instance.json')

class TestDispatcherContract(unittest.TestCase):

    def test_instance(self):
        with open(TESTDATA_FILENAME) as json_file:
            json_data = json.load(json_file)

        dapp = Contract(json_data)
        self.assertEqual(dapp.name, "DAppMock")
        self.assertEqual(dapp.contract_address, "0x59D956d5eEB2F7d93453CE028D1d4A0Bee46543A")
        self.assertEqual(dapp.user_address, "0xB9fBeC4553483B58A11084234587f38377Dd7b95")
        self.assertEqual(dapp["reveal_index"], 0)
        self.assertEqual(dapp["current_state"], "DAppRunning")

        reveal = dapp.children[0]
        self.assertEqual(reveal.name, "RevealMock")
        self.assertEqual(reveal.contract_address, "0x926Fc8818E8666880394665AC5D6D251A7f1A02C")
        self.assertEqual(reveal.user_address, "0xB9fBeC4553483B58A11084234587f38377Dd7b95")
        self.assertEqual(reveal["commit_duration"], 200)
        self.assertEqual(reveal["reveal_duration"], 200)
        self.assertEqual(reveal["match_manager_epoch_duration"], 100)
        self.assertEqual(reveal["match_manager_match_duration"], 50)
        self.assertEqual(reveal["final_time"], 13000)
        self.assertEqual(reveal["initial_hash"], "0x3078633765320000000000000000000000000000000000000000000000000000")
        self.assertEqual(reveal["machine_address"], "0x0000000000000000000000000000000000000000")
        self.assertEqual(reveal["current_state"], "MatchManagerPhase")

        match_manager = reveal.children[0]
        self.assertEqual(match_manager.name, "MatchManager")
        self.assertEqual(match_manager.contract_address, "0x53D1D41e3952347156c49fACC6Ef7AB1872ac1a3")
        self.assertEqual(match_manager.user_address, "0xB9fBeC4553483B58A11084234587f38377Dd7b95")
        self.assertEqual(match_manager["epoch_duration"], 100)
        self.assertEqual(match_manager["round_duration"], 50)
        self.assertEqual(match_manager["current_epoch"], 1)
        self.assertEqual(match_manager["final_time"], 13000)
        self.assertEqual(match_manager["last_epoch_start_time"], 1571955037)
        self.assertEqual(match_manager["number_of_matches_on_last_epoch"], 2)
        self.assertEqual(match_manager["unmatched_player"], "0x0000000000000000000000000000000000000000")
        self.assertEqual(match_manager["last_match_index"], 2)
        self.assertEqual(match_manager["initial_hash"], "0x3078633765320000000000000000000000000000000000000000000000000000")
        self.assertEqual(match_manager["machine"], "0x0000000000000000000000000000000000000000")
        self.assertEqual(match_manager["reveal_address"], "0x926Fc8818E8666880394665AC5D6D251A7f1A02C")
        self.assertEqual(match_manager["reveal_instance"], 0)
        self.assertEqual(match_manager["last_match_epoch"], 1)
        self.assertEqual(match_manager["registered"], False)
        self.assertEqual(match_manager["current_state"], "WaitingMatches")

        match = match_manager.children[0]
        self.assertEqual(match.name, "Match")
        self.assertEqual(match.contract_address, "0x0937625B39EC841740558cddBb2B0A9C169B721A")
        self.assertEqual(match.user_address, "0xB9fBeC4553483B58A11084234587f38377Dd7b95")
        self.assertEqual(match["challenger"], "0xB9fBeC4553483B58A11084234587f38377Dd7b95")
        self.assertEqual(match["claimer"], "0xB24d40F656F8cCC41C76fcBd36057Cd61426E758")
        self.assertEqual(match["machine"], "0x0000000000000000000000000000000000000000")
        self.assertEqual(match["epoch_number"], 1)
        self.assertEqual(match["round_duration"], 50)
        self.assertEqual(match["time_of_last_move"], 1571955040)
        self.assertEqual(match["initial_hash"], "0x3078633765320000000000000000000000000000000000000000000000000000")
        self.assertEqual(match["claimed_final_hash"], "0x0100000000000000000000000000000000000000000000000000000000000000")
        self.assertEqual(match["final_time"], 13000)
        self.assertEqual(match["current_state"], "ClaimerWon")


if __name__ == '__main__':
    unittest.main()
