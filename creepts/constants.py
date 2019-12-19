import os

#PLAYER WALLET RELATED

PLAYER_OWN_ADD = "0x036f5cf5ca56c6b5650c9de2a41d94a3fe1e2077"
#Overwrite own player address if environment variable set
if 'CARTESI_PLAYER_ADD' in os.environ.keys():
    PLAYER_OWN_ADD = os.environ['CARTESI_PLAYER_ADD']

#DB RELATED

DB_NAME = "creepts/db/anuto.db"
USER_LOG_TABLE = "user_logs"
CREATE_USER_LOG_TABLE = "CREATE TABLE {} (user_id INTEGER NOT NULL, tournament_id TEXT NOT NULL, score INTEGER NOT NULL, waves INTEGER NOT NULL, log BLOB NOT NULL);".format(USER_LOG_TABLE)
INSERT_SINGLE_LOG_TABLE = "INSERT INTO {} ('user_id', 'tournament_id', 'score', 'waves', 'log') VALUES (?, ?, ?, ?, ?);".format(USER_LOG_TABLE)
SELECT_LOG_TABLE_BY_USER_AND_TOURNAMENT = "SELECT * FROM {} WHERE user_id=? and tournament_id=?".format(USER_LOG_TABLE)
UPDATE_LOG_TABLE_FOR_USER_AND_TOURNAMENT = "UPDATE {} SET score=?, waves=?, log=? WHERE user_id=? and tournament_id=?".format(USER_LOG_TABLE)

#GAMEPLAY LOG FILES RELATED

LOG_FILES_OUTPUT_DIR = "/home/carlo/crashlabs/anuto-server/creepts/tests/logs-to-share/"
DEFAULT_PAGE_LOG2_BYTES_SIZE = 10
DEFAULT_MERKLE_TREE_LOG2_BYTES_SIZE = 20

#MERKLE TREE ROOT HASH CALCULATOR BINARY
HASH_ENV = "LD_LIBRARY_PATH=/home/carlo/crashlabs/machine-emulator/build/Linux_x86_64/lib"
HASH_BINARY_PATH = "/home/carlo/crashlabs/machine-emulator/src/hash"
HASH_BINARY_CMD = "{} {}".format(HASH_ENV, HASH_BINARY_PATH)

#PACK LOG RELATED
PACKED_LOG_EXT = "br.tar"
PACKLOG_CMD = "/home/carlo/crashlabs/anuto-dapp/machine/packlog"

#TRUNCATE RELATED
DEFAULT_TRUNCATE_SIZE="1m"
TRUNCATE_BIN="truncate"

#DISPATCHER RELATED
DISPATCHER_URL = "http://dispatcher:3001"
COMMIT_LOG_URL = DISPATCHER_URL

#LOGGING RELATED
LOGGING_CONFIG_FILENAME = "creepts/logging.conf"

#TOURNAMENT STATIC INFORMATION RELATED
MAPPED_TOURNAMENT_INFO_FILENAME = "creepts/tournament_info.yaml"
