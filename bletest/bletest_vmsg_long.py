# Copyright (C) 2025 markrypto
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the License along with this library.
# If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.

import blecommon

from binascii import hexlify, unhexlify
import unittest

from keepkeylib import ckd_public as bip32
from blecommon import KeepKeyTestBle

from keepkeylib import messages_pb2 as proto
from keepkeylib import types_pb2 as proto_types
from keepkeylib.client import CallException
from keepkeylib.tools import parse_path
from keepkeylib.tx_api import TxApiTestnet

# from test_vuln20007 import Vuln20007TrapPrevent

class bleVMsg(KeepKeyTestBle):
      
  def __init__(self):
    super().__init__()
    
  def test_message_long(self):
    self.setup_mnemonic_nopin_nopassphrase()
    ret = self.client.verify_message(
      'Bitcoin',
      '1JwSSubhmg6iPtRjtyqhUYYH7bZg3Lfy1T',
      unhexlify('1bddc0aed9cf4e10dc9f57770934f4fb72a27c4510a0f4a81e09c163552416f799cd3f211ffeed0f411e9af9b927407d67115fb6d0ab1897137048efe33417fcc1'),
      "VeryLongMessage!" * 64
    )


def main():
  
  bleVMsg().test_message_long()
  return
  
if __name__ == '__main__':
    main()
