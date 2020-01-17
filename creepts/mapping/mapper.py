import yaml

from datetime import datetime
from creepts.model.tournament import Tournament, TournamentPhase
import creepts.constants as const

class TournamentMappingException(Exception):
    pass

class Mapper:

    def to_tournament(self, dapp):
        #Should be DAppManager at first, when removing the test part of the dapp this
        #first level should disappear and start from the "AnutoDapp" level
        if not dapp.name.startswith("DApp"):
            return None

        #go into AnutoDApp, return None if not possible
        if not (len(dapp.children)>0 and dapp.children[0].name.startswith("AnutoDApp")):
            return None

        anuto_dapp = dapp.children[0]
        id = anuto_dapp.index
        if id == None:
            raise TournamentMappingException("Must have \"index\" field at the AnutoDApp level")

        name = self._get_tournament_name(anuto_dapp)

        if not name:
            raise TournamentMappingException("Couldn't recover name of the tournament with id {}".format(id))

        map = anuto_dapp["level"]

        if map == None:
            raise TournamentMappingException("Couldn't recover the map of the tournament with id {}".format(id))

        tournament = Tournament(id, name, map)

        #Checking if the tournament is done
        if anuto_dapp["current_state"] == "DAppFinished":
            #It is
            tournament.phase = TournamentPhase.END

            #TODO: recover champion score, address and log

            return tournament

        #Checking if tournament is in the round phase and trying to get MatchManager
        elif anuto_dapp["current_state"] == "WaitingMatches":

            #It's in the round phase
            tournament.phase = TournamentPhase.ROUND

            # Get MatchManager if any:
            for child in anuto_dapp.children:
                if child.name == "MatchManager":

                    match_manager = child

                    #Getting tournament info
                    #TODO: remove or discover how to populate playerCount and totalRounds
                    tournament.currentRound = match_manager["current_epoch"]
                    tournament.lastRound = match_manager["last_match_epoch"]
                    tournament.deadline = datetime.utcfromtimestamp(match_manager["last_epoch_start_time"] + match_manager["epoch_duration"]).isoformat()

                    #Trying to recover last opponent info
                    if len(match_manager.children) > 0 and match_manager.children[0].name == "Match":
                        match = match_manager.children[0]

                        #Checking if player is the challenger or the claimer
                        if (match["challenger"] == const.PLAYER_OWN_ADD):
                            tournament.currentOpponent = match["claimer"]
                        elif (match["claimer"] == const.PLAYER_OWN_ADD):
                            tournament.currentOpponent = match["challenger"]

                    return tournament

        #Checking if tournament is in the commit or reveal phases
        elif anuto_dapp["current_state"] == "WaitingCommitAndReveal":

            #Recover commit/reveal manager if any:
            for child in anuto_dapp.children:
                if child.name == "RevealCommit":

                    reveal_commit = child

                    #Checking if it is in the commit phase
                    if reveal_commit["current_state"] == "CommitPhase":
                        tournament.phase = TournamentPhase.COMMIT
                        tournament.deadline = datetime.utcfromtimestamp(reveal_commit["instantiated_at"] + reveal_commit["commit_duration"]).isoformat()

                    else:
                        tournament.phase = TournamentPhase.REVEAL
                        tournament.deadline = datetime.utcfromtimestamp(reveal_commit["instantiated_at"] + reveal_commit["commit_duration"] + reveal_commit["reveal_duration"]).isoformat()

                    #TODO: remove from or discover how to populate playerCount in the tournament class

        return tournament

    def _get_tournament_name(self, dapp):
        name = None
        #At the time this is comming from a static file, but should come from the blockchain in the future
        #Loading yaml with the mapped information
        with open(const.MAPPED_TOURNAMENT_INFO_FILENAME) as tour_info_file:
            tour_info = yaml.full_load(tour_info_file)
            id = dapp.index

            if id in tour_info.keys():
                if "name" in tour_info[id].keys():
                    name = tour_info[id]["name"]

        return name
