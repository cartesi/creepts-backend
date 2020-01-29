import os
import sys
from cobra_hdwallet import HDWallet
from web3.auto import w3
import logging

hdWallet = HDWallet()

#PLAYER WALLET RELATED

if 'MNEMONIC' in os.environ.keys():
    # create wallet object from MNEMONIC
    # user can define an ACCOUNT_INDEX, defaults to 0
    wallet = hdWallet.create_hdwallet(os.environ.get("MNEMONIC"),
        '', # no passphrase
        int(os.getenv("ACCOUNT_INDEX", default="0")))

    PLAYER_OWN_ADD = w3.toChecksumAddress(wallet['address'])

elif 'ACCOUNT_ADDRESS' in os.environ.keys():
    PLAYER_OWN_ADD = os.environ['ACCOUNT_ADDRESS']

else:
    print('Must define MNEMONIC or ACCOUNT_ADDRESS for the player address')
    sys.exit(1)

# TODO: logging does not work here
# logging.info('Using account ' + PLAYER_OWN_ADD)
print('Using account ' + PLAYER_OWN_ADD)

#TEST RELATED

MOCKED_SERVER = False
#Overwrite if environment variable set
if 'MOCKED_SERVER' in os.environ.keys():
    MOCKED_SERVER = True

#DB RELATED

if MOCKED_SERVER:
    DB_NAME = "creepts/tests/creepts_test.db"
else:
    DB_NAME = "creepts/db/creepts.db"

USER_LOG_TABLE = "user_logs"
CREATE_USER_LOG_TABLE = "CREATE TABLE {} (user_id TEXT NOT NULL, tournament_id TEXT NOT NULL, score INTEGER NOT NULL, waves INTEGER NOT NULL, log BLOB NOT NULL);".format(USER_LOG_TABLE)
INSERT_SINGLE_LOG_TABLE = "INSERT INTO {} ('user_id', 'tournament_id', 'score', 'waves', 'log') VALUES (?, ?, ?, ?, ?);".format(USER_LOG_TABLE)
SELECT_LOG_TABLE_FROM_USER_AND_TOURNAMENT = "SELECT * FROM {} WHERE user_id=? and tournament_id=?".format(USER_LOG_TABLE)
BASE_SELECT_LOG_TABLE_FROM_TOURNAMENTS = "SELECT * FROM {} WHERE tournament_id in ".format(USER_LOG_TABLE) #The list is not supported by sqlite argument formatting so it is substituted in the program itself
UPDATE_LOG_TABLE_FOR_USER_AND_TOURNAMENT = "UPDATE {} SET score=?, waves=?, log=? WHERE user_id=? and tournament_id=?".format(USER_LOG_TABLE)

#GAMEPLAY LOG FILES RELATED

LOG_FILES_OUTPUT_DIR = "creepts/logs-to-share/"
if 'LOG_FILES_OUTPUT_DIR' in os.environ.keys():
    LOG_FILES_OUTPUT_DIR = os.environ['LOG_FILES_OUTPUT_DIR']
DEFAULT_PAGE_LOG2_BYTES_SIZE = 10
DEFAULT_MERKLE_TREE_LOG2_BYTES_SIZE = 20

#MERKLE TREE ROOT HASH CALCULATOR BINARY
HASH_BINARY_CMD = "cartesi-machine-hash"
if 'HASH_BINARY_CMD' in os.environ.keys():
    HASH_BINARY_CMD = os.environ['HASH_BINARY_CMD']

#PACK LOG RELATED
PACKED_LOG_EXT = "br.cpio"
PACKLOG_CMD = "packlog"
if 'PACKLOG_CMD' in os.environ.keys():
    PACKLOG_CMD = os.environ['PACKLOG_CMD']

#TRUNCATE RELATED
DEFAULT_TRUNCATE_SIZE="1M"
TRUNCATE_BIN="truncate"

#DISPATCHER RELATED
DISPATCHER_URL = "http://dispatcher:3001"
if 'DISPATCHER_URL' in os.environ.keys():
    DISPATCHER_URL = os.environ['DISPATCHER_URL']
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
if 'CONTRACTS_DIR' in os.environ.keys():
    CONTRACTS_DIR = os.environ['CONTRACTS_DIR']
else:
    print("Must define CONTRACTS_DIR env variable with the path of the contracts specifications directory")
    sys.exit(1)

REVEAL_INSTANTIATOR_CONTRACT = "reveal_instantiator"

CONTRACTS_MAPPING = {
        REVEAL_INSTANTIATOR_CONTRACT: "node_modules/@cartesi/tournament/build/contracts/RevealInstantiator.json"
}

#Formatting contracts mapping to contain the full path of the contract specification files
for k in CONTRACTS_MAPPING.keys():
    CONTRACTS_MAPPING[k] = "{}/{}".format(CONTRACTS_DIR, CONTRACTS_MAPPING[k])
