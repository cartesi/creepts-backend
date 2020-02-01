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

from enum import Enum
from datetime import datetime
import json

class TournamentPhase(Enum):
    COMMIT = "commit"
    REVEAL = "reveal"
    ROUND = "round"
    END = "end"

class Tournament:

    def __init__(self, id, name, map):
        self.id = id
        self.name = name
        self.map = map
        self.playerCount = 0
        self.phase = None
        self.currentRound = 0
        self.totalRounds = 0
        self.lastRound = 0
        self.winner = None
        self.deadline = None
        self.currentOpponent = None
        self.scores = {}

class TournamentJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Tournament):
            return obj.__dict__

        if isinstance(obj, TournamentPhase):
            return obj.value

        if isinstance(obj, datetime):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
