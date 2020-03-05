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

import unittest
import os
import shutil
import filecmp

os.environ['ACCOUNT_ADDRESS'] = "0x760841c050d07d3f74139154284d1cd8b5afa9c6"
os.environ['CONTRACTS_DIR'] = "/"

from creepts.utils import hash_utils
from creepts.constants import PACKED_LOG_EXT

class TestDispatcherContract(unittest.TestCase):

    def test_pack_unpack(self):
        # working file
        filepath = os.path.join(os.path.dirname(__file__), 'mock_logs', 'pack.json')

        # backup file
        cp = os.path.join(os.path.dirname(__file__), 'mock_logs', 'pack_copy.json')

        # copy working file
        shutil.copyfile(filepath, cp)

        # make sure file exists
        self.assertTrue(os.path.exists(filepath))

        # pack file
        packed_filepath = hash_utils.pack_log_file(filepath)

        # new file name is returned
        self.assertEqual(packed_filepath, filepath + '.' + PACKED_LOG_EXT)

        # original file is delete
        self.assertFalse(os.path.exists(filepath))

        # new file exists
        self.assertTrue(os.path.exists(packed_filepath))

        # unpack (reverse operation)
        filepath2 = hash_utils.unpack_log_file(filepath)

        # must work
        self.assertEqual(filepath, filepath2)

        # unpack deletes the packed file
        self.assertFalse(os.path.exists(packed_filepath))

        # compare files
        self.assertTrue(filecmp.cmp(filepath, cp))

        # restore original file
        shutil.copyfile(cp, filepath)

        # delete copy
        os.remove(cp)

        # make sure original file exists
        self.assertTrue(os.path.exists(filepath))


if __name__ == '__main__':
    unittest.main()
