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

import logging
from ..utils import blockchain_utils

class BlockchainDecorator:

    def apply(self, dapp, tournament):

        # get number of players from blockchain
        try:
            tournament.playerCount = blockchain_utils.get_number_of_players(dapp)
        except Exception as e:
            # log exception and set value to 0
            logging.error("Failed to recover number of players in tournament %d. Details:", tournament.id)
            logging.exception(e)
            tournament.playerCount = 0

        # get scores from blockchain (opponent and winner)
        self._fetch_scores_from_blockchain(dapp, tournament)

        return
    
    def _fetch_scores_from_blockchain(self, dapp, tournament):
        scores={}
        # getting winner score if available
        if tournament.winner:
            try:
                winner_score = blockchain_utils.get_player_score(dapp, tournament.winner)
                commit_hash = blockchain_utils.get_player_hash(dapp, tournament.winner)
                scores[tournament.winner] = { "score": winner_score, "hash": commit_hash }
            except Exception as e:
                # log exception and keep trying to recover other scores
                logging.error("Failed to recover score or hash from player %s and tournament %d. Details:", tournament.winner, tournament.id)
                logging.exception(e)

        # getting current opponent score if available
        if tournament.currentOpponent:
            try:
                opponent_score = blockchain_utils.get_player_score(dapp, tournament.currentOpponent)
                commit_hash = blockchain_utils.get_player_hash(dapp, tournament.currentOpponent)
                scores[tournament.currentOpponent] = { "score": opponent_score, "hash": commit_hash }
            except Exception as e:
                #Log exception and keep trying to recover other scores
                logging.error("Failed to recover score or hash from player %s and tournament %d. Details:", tournament.currentOpponent, tournament.id)
                logging.exception(e)

        # merge old scores with the new ones
        tournament.scores={**tournament.scores, **scores}
