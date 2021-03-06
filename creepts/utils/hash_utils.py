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

import subprocess
import logging
import os

from .. import constants as const

LOGGER = logging

def merkle_root_hash(file_path, page_log2_bytes_size=const.DEFAULT_PAGE_LOG2_BYTES_SIZE, merkle_tree_log2_bytes_size=const.DEFAULT_MERKLE_TREE_LOG2_BYTES_SIZE):

    LOGGER.info("Calculating the merkle tree root hash for file '{}' using log2 bytes size of {} for page and {} for tree".format(file_path, page_log2_bytes_size, merkle_tree_log2_bytes_size))

    cmd_line = [const.HASH_BINARY_CMD, "--input={}".format(file_path), "--page-log2-size={}".format(page_log2_bytes_size), "--tree-log2-size={}".format(merkle_tree_log2_bytes_size)]
    LOGGER.debug("Executing {}".format(" ".join(cmd_line)))
    proc = None
    try:
        proc = subprocess.Popen(" ".join(cmd_line), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, err = proc.communicate()
        LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
    except Exception as e:
        LOGGER.exception(e)
        err_msg = "Failed to calculate merkle tree root hash for file '{}'".format(file_path)
        LOGGER.error(err_msg)
        if (proc):
            out, err = proc.communicate()
            LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
        return None

    if (proc.returncode == 0):
        #Return the calculated hash
        return "0x{}".format(out.decode("utf-8").rstrip('\n'))

    LOGGER.error("Failed to calculate merkle tree root hash for file '{}', processed returned non-zero code".format(file_path))
    return None

def pack_log_file(file_path):

    logging.info("Compacting and arquiving file '{}'".format(file_path))

    packed_log_filename = "{}.{}".format(file_path, const.PACKED_LOG_EXT)
    cmd_line = [const.PACKLOG_CMD, file_path, packed_log_filename]
    logging.debug("Executing {}".format(" ".join(cmd_line)))

    result = subprocess.run(cmd_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        #Remove original file and return the packed log filename
        os.remove(file_path)
        return packed_log_filename
    else:
        logging.error('Error executing command: {}'.format(result.returncode))
        logging.error(result.stderr.decode('utf-8'))
        return None

    #proc = None
    #try:
    #    proc = subprocess.Popen(cmd_line, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    #    out, err = proc.communicate()
    #    LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
    #except Exception as e:
    #    err_msg = "Failed to compact and archive file '{}'".format(file_path)
    #    LOGGER.error(err_msg)
    #    LOGGER.exception(e)
    #    if (proc):
    #        out, err = proc.communicate()
    #        LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
    #    return None

    #if (proc.returncode == 0):
    #    #Remove original file and return the packed log filename
    #    os.remove(file_path)
    #    return packed_log_filename

    LOGGER.error("Failed to compress and archive file '{}', processed returned non-zero code".format(file_path))
    return None

def unpack_log_file(file_path):

    logging.info("Unarchiving and unpacking file '{}'".format(file_path))

    packed_log_filename = "{}.{}".format(file_path, const.PACKED_LOG_EXT)
    cmd_line = [const.UNPACKLOG_CMD, packed_log_filename, file_path]
    LOGGER.debug("Executing {}".format(" ".join(cmd_line)))

    result = subprocess.run(cmd_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        os.remove(packed_log_filename)
        return file_path
    else:
        logging.error('Error executing command: {}'.format(result.returncode))
        logging.error(result.stderr.decode('utf-8'))
        return None

#    proc = None
#    try:
#        proc = subprocess.Popen(cmd_line, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
#        out, err = proc.communicate()
#        LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
#    except Exception as e:
#        err_msg = "Failed to unarchive and uncompress file '{}'".format(packed_log_filename)
#        LOGGER.error(err_msg)
#        LOGGER.exception(e)
#        if (proc):
#            out, err = proc.communicate()
#            LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
#        return None
    
#    if (proc.returncode == 0):
#        #Remove original file and return the unpacked log filename
#        os.remove(packed_log_filename)
#        return file_path

#    LOGGER.error("Failed to unarchive and decompress file '{}', processed returned non-zero code".format(packed_log_filename))
#    return None

def truncate_file(file_path, size=const.DEFAULT_TRUNCATE_SIZE):

    LOGGER.info("Truncating file '{}'".format(file_path))

    cmd_line = [const.TRUNCATE_BIN, "-s", size, file_path]
    LOGGER.debug("Executing {}".format(" ".join(cmd_line)))
    proc = None
    try:
        proc = subprocess.Popen(cmd_line, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
    except Exception as e:
        err_msg = "Failed to truncate file '{}'".format(file_path)
        LOGGER.error(err_msg)
        LOGGER.exception(e)
        if (proc):
            out, err = proc.communicate()
            LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
        return None

    if (proc.returncode == 0):
        #Return true
        return True

    LOGGER.error("Failed to truncate file '{}', processed returned non-zero code".format(file_path))
    return False

