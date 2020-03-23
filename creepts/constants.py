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
import sys
from cobra_hdwallet import HDWallet
from web3 import Web3
import logging

hdWallet = HDWallet()

#PLAYER WALLET RELATED

if 'MNEMONIC' in os.environ.keys():
    # create wallet object from MNEMONIC
    # user can define an ACCOUNT_INDEX, defaults to 0
    wallet = hdWallet.create_hdwallet(os.environ.get("MNEMONIC"),
        '', # no passphrase
        int(os.getenv("ACCOUNT_INDEX", default="0")))

    PLAYER_OWN_ADD = Web3.toChecksumAddress(wallet['address'])

elif 'ACCOUNT_ADDRESS' in os.environ.keys():
    PLAYER_OWN_ADD = Web3.toChecksumAddress(os.environ['ACCOUNT_ADDRESS'])

else:
    print('Must define MNEMONIC or ACCOUNT_ADDRESS for the player address')
    #sys.exit(1)

# TODO: logging does not work here
# logging.info('Using account ' + PLAYER_OWN_ADD)
#print('Using account ' + PLAYER_OWN_ADD)

#TEST RELATED
READ_ONLY = bool(os.getenv('READ_ONLY'))
MOCKED_SERVER = bool(os.getenv('MOCKED_SERVER'))

#DB RELATED

if MOCKED_SERVER:
    DB_NAME = os.getenv("DB_NAME", default="creepts/tests/creepts_test.db")
else:
    DB_NAME = os.getenv("DB_NAME", default="creepts/db/creepts.db")

USER_LOG_TABLE = "user_logs"
CREATE_USER_LOG_TABLE = "CREATE TABLE {} (user_id TEXT NOT NULL, tournament_id TEXT NOT NULL, score INTEGER NOT NULL, waves INTEGER NOT NULL, log BLOB NOT NULL);".format(USER_LOG_TABLE)
INSERT_SINGLE_LOG_TABLE = "INSERT INTO {} ('user_id', 'tournament_id', 'score', 'waves', 'log') VALUES (?, ?, ?, ?, ?);".format(USER_LOG_TABLE)
SELECT_LOG_TABLE_FROM_USER_AND_TOURNAMENT = "SELECT * FROM {} WHERE user_id=? and tournament_id=?".format(USER_LOG_TABLE)
BASE_SELECT_LOG_TABLE_FROM_TOURNAMENTS = "SELECT * FROM {} WHERE tournament_id in ".format(USER_LOG_TABLE) #The list is not supported by sqlite argument formatting so it is substituted in the program itself
UPDATE_LOG_TABLE_FOR_USER_AND_TOURNAMENT = "UPDATE {} SET score=?, waves=?, log=? WHERE user_id=? and tournament_id=?".format(USER_LOG_TABLE)

#GAMEPLAY LOG FILES RELATED

LOGGER_URL = os.getenv("LOGGER_URL", default="logger:50051")
LOGGER_DATA_DIR = os.getenv("LOGGER_DATA_DIR", default="/opt/cartesi/srv/logger-server")
LOG_FILES_OUTPUT_DIR = os.getenv("LOG_FILES_OUTPUT_DIR", default="creepts/logs-to-share/")
DEFAULT_PAGE_LOG2_BYTES_SIZE = 10
DEFAULT_MERKLE_TREE_LOG2_BYTES_SIZE = 20

#MERKLE TREE ROOT HASH CALCULATOR BINARY
HASH_BINARY_CMD = os.getenv("HASH_BINARY_CMD", default="cartesi-machine-hash")

#PACK LOG RELATED
PACKED_LOG_EXT = "br.cpio"
PACKLOG_CMD = os.getenv("PACKLOG_CMD", default="./packlog")
UNPACKLOG_CMD = os.getenv("UNPACKLOG_CMD", default="./unpacklog")

#TRUNCATE RELATED
DEFAULT_TRUNCATE_SIZE="1M"
TRUNCATE_BIN="truncate"

#DISPATCHER RELATED
DISPATCHER_URL = os.getenv("DISPATCHER_URL", default="http://dispatcher:3001")
COMMIT_LOG_URL = DISPATCHER_URL

#LOGGING RELATED
LOGGING_CONFIG_FILENAME = "creepts/logging.conf"

#TOURNAMENT STATIC INFORMATION RELATED
MAPPED_TOURNAMENT_INFO_FILENAME = "creepts/tournament_info.yaml"

#MAPS STATIC INFORMATION RELATED
MAPPED_MAP_INFO_FILENAME = "creepts/map_info.yaml"

#TOURNAMENT RESOURCE RELATED
TOURNAMENTS_RESPONSE_LIMIT = 100

#BLOCKCHAIN RELATED
CONTRACTS_DIR = os.getenv('CONTRACTS_DIR', default=".")
CONTRACTS_MAPPING = {
    "RevealCommit": "node_modules/@cartesi/tournament/build/contracts/RevealInstantiator.json"
}

#Formatting contracts mapping to contain the full path of the contract specification files
for k in CONTRACTS_MAPPING.keys():
    CONTRACTS_MAPPING[k] = "{}/{}".format(CONTRACTS_DIR, CONTRACTS_MAPPING[k])
