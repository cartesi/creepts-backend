from web3 import Web3
from web3.auto import w3
import logging
import json

from .. import constants as const

LOGGER=logging
CONTRACT_CACHE={}

def is_address(address):
    return Web3.isAddress(address)

def player_exists(tour_id, address):

    LOGGER.debug("Checking if player %s is in tournament %d", address, tour_id)

    rev_inst = _get_contract_instance(const.REVEAL_INSTANTIATOR_CONTRACT)
    exists = rev_inst.functions.playerExist(tour_id, Web3.toChecksumAddress(address)).call()

    LOGGER.info("Player %s exists in tournament %d: %r", address, tour_id, exists)

    return exists

def get_player_balance(address):

    if not is_address(address):
        error = "Given address is not a valid Ethereum address: {}".format(address)
        LOGGER.error(error)
        raise ValueError(error)

    LOGGER.info("Querying blockchain for eth balance of address %s", address)
    balance =  w3.eth.getBalance(Web3.toChecksumAddress(address))
    LOGGER.info("Balance for %s : %d", address, balance)
    return balance

def get_player_score(tour_id, address):
    if not is_address(address):
        error = "Given address is not a valid Ethereum address: {}".format(address)
        LOGGER.error(error)
        raise ValueError(error)

    LOGGER.info("Querying blockchain for player %s score in tournament %d", address, tour_id)

    #Get reveal instantiator contract instance
    rev_inst = _get_contract_instance(const.REVEAL_INSTANTIATOR_CONTRACT)
    LOGGER.debug("Got reveal instantiator contract manipulation instance")

    #Recover score from blockchain
    score = rev_inst.functions.getScore(tour_id, Web3.toChecksumAddress(address)).call()
    LOGGER.info("Score for player %s in tournament %d is %d", address, tour_id, score)

    return score

def _get_contract_instance(contract_name):
    """
    Returns an instance web3 contract manipulator of the given contract name
    and network of the active ethereum node using data available from the
    truffle deployment file
    """
    #Return from contract instances cache, if in there
    if contract_name in CONTRACT_CACHE.keys():
        return CONTRACT_CACHE[contract_name]

    contracts_mapping = const.CONTRACTS_MAPPING

    if (contract_name not in contracts_mapping.keys()):
        raise ValueError("Contract name {} is invalid, valid options are {}".format(contract_name, contracts_mapping.keys()))

    with open(contracts_mapping[contract_name]) as contract_info_file:
        contract_info_data = json.load(contract_info_file)

    contract_abi = contract_info_data['abi']
    net_id = w3.net.version
    contract_addr = contract_info_data['networks'][net_id]['address']

    #Get contract manipulation instance and store it in the cache
    CONTRACT_CACHE[contract_name] = w3.eth.contract(address=contract_addr, abi=contract_abi)

    return CONTRACT_CACHE[contract_name]
