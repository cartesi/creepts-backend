import falcon
import json
import traceback
import sys
import requests
import logging
import logging.config
import argparse

from creepts import constants as const
from creepts.utils import game_log_utils, hash_utils
from creepts.db import db_utilities

#Configuring the logging for the application
logging.config.fileConfig('logging.conf')

LOGGER = logging.getLogger(__name__)

description = "Issues a commit in the dispatcher to the given tournament using the given address and log"

parser = argparse.ArgumentParser(description=description)
parser.add_argument(
    '--log-filename', '-l',
    dest='log_filename',
    required=True,
    help='Game log filename to commit (required)'
)
parser.add_argument(
    '--tournament_id', '-t',
    dest='tour_id',
    required=True,
    help='The tournament id to commit to (required)'
)

#Getting arguments
args = parser.parse_args()

log_filename = args.log_filename
tour_id = args.tour_id

LOGGER.info("Provided tour_id {} and game log filename {}".format(tour_id, log_filename))

#Compress and archive the log
packed_log_filename = hash_utils.pack_log_file(log_filename)

if not packed_log_filename:
    raise RuntimeError("Error compressing and archiving game log file")

#Truncate file to the expected final size
success = hash_utils.truncate_file(packed_log_filename)

if not success:
    raise RuntimeError("Error truncating compressed and archived game log file to correct size")

#Calculate the merkle tree root hash of it
calculated_hash = hash_utils.merkle_root_hash(packed_log_filename)

if not calculated_hash:
    raise RuntimeError("Error calculating the merkle root hash of the compressed, archieved and truncated game log file")

#Format the post payload
payload = {
    "action": "commit",
    "params": {
        "hash": calculated_hash
    }
}
data = {
    "Post": {
    "index": int(tour_id),
    "payload": json.dumps(payload)
    }
}

#Commit the game log
dispatcher_resp = requests.post(const.COMMIT_LOG_URL, json=data)

if (dispatcher_resp.status_code != 200):
    print("Failed to commit gamelog for tournament id {} and game log file name {}. Response content was {}".format(tour_id, packed_log_filename, dispatcher_resp.text))
    sys.exit(1)

print("Dispatcher returned 200")
