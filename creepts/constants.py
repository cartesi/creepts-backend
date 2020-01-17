import os
import sys

#PLAYER WALLET RELATED

if 'ACCOUNT_ADDRESS' in os.environ.keys():
    PLAYER_OWN_ADD = os.environ['ACCOUNT_ADDRESS']
else:
    print('Must define player address in an environment variable called ACCOUNT_ADDRESS')
    sys.exit(1)

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
DEFAULT_TRUNCATE_SIZE="1m"
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

#TOURNAMENT RESOURCE RELATED
TOURNAMENTS_RESPONSE_LIMIT = 100
