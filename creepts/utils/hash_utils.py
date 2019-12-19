import subprocess
import logging

from .. import constants as const

LOGGER = logging.getLogger(__name__)

def merkle_root_hash(file_path, page_log2_bytes_size=const.DEFAULT_PAGE_LOG2_BYTES_SIZE, merkle_tree_log2_bytes_size=const.DEFAULT_MERKLE_TREE_LOG2_BYTES_SIZE):

    LOGGER.info("Calculating the merkle tree root hash for file '{}' using log2 bytes size of {} for page and {} for tree".format(file_path, page_log2_bytes_size, merkle_tree_log2_bytes_size))

    cmd_line = [const.HASH_BINARY_CMD, "--input", file_path, "--page-log2-size", page_log2_bytes_size, "--tree-log2-size", merkle_tree_log2_bytes_size]
    LOGGER.debug("Executing {}".format(" ".join(cmd_line)))
    proc = None
    try:
        proc = subprocess.Popen(cmd_line, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, err = proc.communicate()
        LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
    except Exception as e:
        err_msg = "Failed to calculate merkle tree root hash for file '{}'".format(file_path)
        LOGGER.error(err_msg)
        if (proc):
            out, err = proc.communicate()
            LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
            return None

    if (proc.returncode == 0):
        #Return the calculated hash
        return "0x{}".format(out.decode("utf-8"))

    LOGGER.error("Failed to calculate merkle tree root hash for file '{}', processed returned non-zero code".format(file_path))
    return None

def pack_log_file(file_path):

    LOGGER.info("Compacting ant arquiving file '{}'".format(file_path))

    packed_log_filename = "{}.{}".format(file_path, const.PACKED_LOG_EXT)
    cmd_line = [const.PACKLOG_CMD, file_path, packed_log_filename]
    LOGGER.debug("Executing {}".format(" ".join(cmd_line)))
    proc = None
    try:
        proc = subprocess.Popen(cmd_line, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, err = proc.communicate()
        LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
    except Exception as e:
        err_msg = "Failed to compact and archive file '{}'".format(file_path)
        LOGGER.error(err_msg)
        if (proc):
            out, err = proc.communicate()
            LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
            return None

    if (proc.returncode == 0):
        #Return the packed log filename
        return packed_log_filename

    LOGGER.error("Failed to compress and archive file '{}', processed returned non-zero code".format(file_path))
    return None

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
        if (proc):
            out, err = proc.communicate()
            LOGGER.debug("\nStdout:\n{}\nStderr:\n{}".format(out.decode("utf-8"), err.decode("utf-8")))
            return None

    if (proc.returncode == 0):
        #Return true
        return True

    LOGGER.error("Failed to truncate file '{}', processed returned non-zero code".format(file_path))
    return False

