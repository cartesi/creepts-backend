from datetime import datetime
from creepts.model.tournament import Tournament, TournamentPhase
from creepts.constants import PLAYER_OWN_ADD

class Mapper:

    def to_tournament(self, dapp):
        assert dapp.name.startswith("DApp")
        id = dapp.contract_address
        name = dapp["name"] if "name" in dapp else None
        map = dapp["map"] if "map" in dapp else None

        tournament = Tournament(id, name, map)

        # go into Reveal
        if len(dapp.children) > 0 and dapp.children[0].name.startswith("Reveal"):
            reveal = dapp.children[0]

            # XXX: expecting new reveal variable
            tournament.playerCount = 0

            # tourname state
            state = reveal["current_state"]
            if state == 'CommitPhase':
                tournament.phase = TournamentPhase.COMMIT
            elif state == 'RevealPhase':
                tournament.phase = TournamentPhase.REVEAL
            elif state == 'MatchManagerPhase':
                tournament.phase = TournamentPhase.ROUND
            elif state == 'TournamentOver':
                tournament.phase = TournamentPhase.END

            # deadline
            if state == 'CommitPhase':
                # XXX: there is no commit_start variable
                tournament.deadline = datetime.utcfromtimestamp(
                    reveal["commit_start"] + reveal["commit_duration"])

            # go into MatchManager
            if len(reveal.children) > 0 and reveal.children[0].name == "MatchManager":
                match_manager = reveal.children[0]

                tournament.currentRound = match_manager["current_epoch"]
                tournament.lastRound = match_manager["last_match_epoch"]
                
                if state == 'MatchManagerPhase':
                    tournament.deadline = datetime.utcfromtimestamp(
                        match_manager["last_epoch_start_time"] + match_manager["epoch_duration"])

                if len(match_manager.children) > 0 and match_manager.name == 'Match':
                    match = match_manager[0]
                    challenger = match["challenger"]
                    claimer = match["claimer"]

                    if challenger == PLAYER_OWN_ADD:
                        tournament.currentOpponent = claimer
                    elif claimer == PLAYER_OWN_ADD:
                        tournament.currentOpponent = challenger
                    # XXX: warn if neither challenger nor claimer are my address

        tournament.winner = dapp["winner"] if "winner" in dapp else None

        return tournament
