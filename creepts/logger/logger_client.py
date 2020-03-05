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
import grpc
from web3 import Web3

from . import cartesi_base_pb2
from . import logger_high_pb2
from . import logger_high_pb2_grpc

from ..constants import LOGGER_URL, LOGGER_DATA_DIR, LOG_FILES_OUTPUT_DIR, PACKED_LOG_EXT, DEFAULT_PAGE_LOG2_BYTES_SIZE, DEFAULT_MERKLE_TREE_LOG2_BYTES_SIZE

class LoggerClient:

    def download(self, commit_hash):
        # use the hash as base name of file
        filename = '{}.json'.format(commit_hash)

        # build the path where the file will be in the backend filesystem
        mypath = os.path.join(LOG_FILES_OUTPUT_DIR, filename)

        # build the path the logger will store the file (may be different, because it's a different container/filesystem)
        logger_path = os.path.join(LOGGER_DATA_DIR, '{}.{}'.format(filename, PACKED_LOG_EXT))

        # create channel, maybe need to do this only once?
        channel = grpc.insecure_channel(LOGGER_URL)

        # create the stub (only once?)
        stub = logger_high_pb2_grpc.LoggerManagerHighStub(channel)

        # request file
        request = logger_high_pb2.DownloadFileRequest(
            path=logger_path,
            root=cartesi_base_pb2.Hash(content=Web3.toBytes(hexstr=commit_hash)),
            page_log2_size=DEFAULT_PAGE_LOG2_BYTES_SIZE,
            tree_log2_size=DEFAULT_MERKLE_TREE_LOG2_BYTES_SIZE
        )

        response = stub.DownloadFile(request)

        # path
        # progress
        # status: 0 -> finished successfully
        #         1 -> working on it, not ready yet
        #         2 -> invalid argument
        #         3 -> service not available, shutting down
        # description

        if response.status == 0:
            return { 'status': 0, 'path': mypath }
        elif response.status == 1:
            # still working on it
            return { 'status': 1, 'progress': response.progress }
        elif response.status == 2:
            raise ValueError(response.description)
        elif response.status == 3:
            raise RuntimeError(response.description)
