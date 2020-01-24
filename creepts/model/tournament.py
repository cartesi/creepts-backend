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
