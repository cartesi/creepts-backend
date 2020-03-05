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

from web3 import Web3
from web3.auto import w3
import logging
import json

from .. import constants as const

# keep a cache of web3 contract instance by the contract name
CONTRACT_CACHE={}

def is_address(address):
    return Web3.isAddress(address)

def get_number_of_players(dapp):

    tournament_id = dapp.index
    logging.debug("Getting number of players in tournament %d", tournament_id)

    # get the reveal child contract
    reveal = next((child for child in dapp.children if child.name == 'RevealCommit'), None)

    # check if RevealCommit really exists
    if reveal is None:
        error = "Contract {} has no RevealCommit sub-instance".format(dapp.name)
        logging.error(error)
        raise ValueError(error)

    # get the web3 instance
    reveal_instance = _get_contract_instance(reveal)

    # call the contract function
    number_of_players = reveal_instance.functions.getNumberOfPlayers(reveal.index).call()

    logging.info("Number of players in tournament %d: %d", tournament_id, number_of_players)

    return number_of_players

def player_exists(dapp, address):

    tournament_id = dapp.index
    logging.debug("Checking if player %s is in tournament %d", address, tournament_id)

    # get the reveal child contract
    reveal = next((child for child in dapp.children if child.name == 'RevealCommit'), None)

    # check if RevealCommit really exists
    if reveal is None:
        error = "Contract {} has no RevealCommit sub-instance".format(dapp.name)
        logging.error(error)
        raise ValueError(error)

    # get the web3 instance
    reveal_instance = _get_contract_instance(reveal)

    # call the contract function
    exists = reveal_instance.functions.playerExist(reveal.index, Web3.toChecksumAddress(address)).call()

    logging.info("Player %s exists in tournament %d: %r", address, tournament_id, exists)

    return exists

def get_player_balance(address):

    if not is_address(address):
        error = "Given address is not a valid Ethereum address: {}".format(address)
        logging.error(error)
        raise ValueError(error)

    logging.info("Querying blockchain for eth balance of address %s", address)

    # pylint: disable=no-member
    balance =  w3.eth.getBalance(Web3.toChecksumAddress(address))
    logging.info("Balance for %s : %d", address, balance)
    return balance

def get_player_score(dapp, address):
    if not is_address(address):
        error = "Given address is not a valid Ethereum address: {}".format(address)
        logging.error(error)
        raise ValueError(error)

    tournament_id = dapp.index
    logging.info("Querying blockchain for player %s score in tournament %d", address, tournament_id)

    # get the reveal child contract
    reveal = _get_reveal(dapp)

    # get the web3 instance
    reveal_instance = _get_contract_instance(reveal)
    logging.debug("Got reveal instantiator contract manipulation instance")

    # get score from blockchain
    score = reveal_instance.functions.getScore(reveal.index, Web3.toChecksumAddress(address)).call()
    logging.info("Score for player %s in tournament %d is %d", address, tournament_id, score)

    return score

def get_player_hash(dapp, address):
    if not is_address(address):
        error = "Given address is not a valid Ethereum address: {}".format(address)
        logging.error(error)
        raise ValueError(error)

    tournament_id = dapp.index
    logging.info("Querying blockchain for player %s hash in tournament %d", address, tournament_id)

    # get the reveal child contract
    reveal = _get_reveal(dapp)

    # get the web3 instance
    reveal_instance = _get_contract_instance(reveal)
    logging.debug("Got reveal instantiator contract manipulation instance")

    # get commit hash from blockchain
    commit_hash = reveal_instance.functions.getLogHash(reveal.index, Web3.toChecksumAddress(address)).call()

    # convert to hex string
    commit_hash = Web3.toHex(commit_hash)

    logging.info("Commit hash for player %s in tournament %d is %s", address, tournament_id, commit_hash)

    return commit_hash

def _get_reveal(dapp):
    # get the reveal child contract
    reveal = next((child for child in dapp.children if child.name == 'RevealCommit'), None)

    # check if RevealCommit really exists
    if reveal is None:
        error = "Contract {} has no RevealCommit sub-instance".format(dapp.name)
        logging.error(error)
        raise ValueError(error)

    return reveal

def _get_contract_instance(contract):
    """
    Returns an instance web3 contract manipulator of the given contract object
    and network of the active ethereum node using data available from the
    truffle deployment file
    """
    contract_name = contract.name
    
    # return from contract instances cache, if in there
    if contract_name in CONTRACT_CACHE.keys():
        return CONTRACT_CACHE[contract_name]

    contracts_mapping = const.CONTRACTS_MAPPING

    if (contract_name not in contracts_mapping.keys()):
        raise ValueError("Contract name {} is invalid, valid options are {}".format(contract_name, contracts_mapping.keys()))

    with open(contracts_mapping[contract_name]) as contract_info_file:
        contract_info_data = json.load(contract_info_file)

    # get the ABI from the truffle json file
    contract_abi = contract_info_data['abi']

    # pylint: disable=no-member
    net_id = w3.net.version

    # get the contract address also from the json file
    # XXX: we could use the contract.contract_address that is coming from the dispatcher instead
    contract_address = contract_info_data['networks'][net_id]['address']

    #Get contract manipulation instance and store it in the cache
    CONTRACT_CACHE[contract_name] = w3.eth.contract(address=contract_address, abi=contract_abi)

    return CONTRACT_CACHE[contract_name]
