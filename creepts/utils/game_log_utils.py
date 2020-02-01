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

import json

MOCKED_LOGS = {
    '1': {
        '0x036f5cf5ca56c6b5650c9de2a41d94a3fe1e2077':'original_log.json',
        '0xba4ff7070fb59d83aab639c8833bb7c39e4c1e40':'original_log2.json'
    },
    '2': {
        '0x036f5cf5ca56c6b5650c9de2a41d94a3fe1e2077':'original_log3.json',
        '0xe7b54494ef9c1d25448a6fc8e58e47713817755b':'original_log4.json'
    },
    '3': {
        '0x036f5cf5ca56c6b5650c9de2a41d94a3fe1e2077':'waiting_line_log.json'
    },
    '4': {
        '0x036f5cf5ca56c6b5650c9de2a41d94a3fe1e2077':'original_log5.json'
    },
    '5': {
        '0x036f5cf5ca56c6b5650c9de2a41d94a3fe1e2077':'original_log3.json'
    },
    '7': {
        '0x036f5cf5ca56c6b5650c9de2a41d94a3fe1e2077':'turn_a_round_log.json'
    },
    '8': {
        '0x036f5cf5ca56c6b5650c9de2a41d94a3fe1e2077':'we_are_in_a_hurry_log.json'
    }
}

MOCKED_LOGS_DIR='creepts/tests/mock_logs/'

def get_game_log(tour_id, player_id):
    if (tour_id in MOCKED_LOGS.keys()):
        if (player_id in MOCKED_LOGS[tour_id].keys()):
            log_filename = MOCKED_LOGS_DIR + MOCKED_LOGS[tour_id][player_id]
            with open(log_filename) as logfile:
                str_log = logfile.read()
                return json.loads(str_log)

    return None
