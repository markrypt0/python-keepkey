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

class bleSigntxSegwit(KeepKeyTestBle):
      
  def __init__(self):
    super().__init__()
    
  def test_send_p2sh(self):
    self.setup_mnemonic_allallall()
    self.client.set_tx_api(TxApiTestnet)
    inp1 = proto_types.TxInputType(
      address_n=parse_path("49'/1'/0'/1/0"),
      # 2N1LGaGg836mqSQqiuUBLfcyGBhyZbremDX
      amount=123456789,
      prev_hash=unhexlify('20912f98ea3ed849042efed0fdac8cb4fc301961c5988cba56902d8ffb61c337'),
      prev_index=0,
      script_type=proto_types.SPENDP2SHWITNESS,
    )
    out1 = proto_types.TxOutputType(
      address='mhRx1CeVfaayqRwq5zgRQmD7W5aWBfD5mC',
      amount=12300000,
      script_type=proto_types.PAYTOADDRESS,
    )
    out2 = proto_types.TxOutputType(
      address='2N1LGaGg836mqSQqiuUBLfcyGBhyZbremDX',
      script_type=proto_types.PAYTOADDRESS,
      amount=123456789 - 11000 - 12300000,
    )
    
    proto.TxRequest(request_type=proto_types.TXINPUT, details=proto_types.TxRequestDetailsType(request_index=0)),
    proto.TxRequest(request_type=proto_types.TXOUTPUT, details=proto_types.TxRequestDetailsType(request_index=0)),
    proto.ButtonRequest(code=proto_types.ButtonRequest_ConfirmOutput),
    proto.TxRequest(request_type=proto_types.TXOUTPUT, details=proto_types.TxRequestDetailsType(request_index=1)),
    proto.ButtonRequest(code=proto_types.ButtonRequest_ConfirmOutput),
    proto.ButtonRequest(code=proto_types.ButtonRequest_SignTx),
    proto.TxRequest(request_type=proto_types.TXINPUT, details=proto_types.TxRequestDetailsType(request_index=0)),
    proto.TxRequest(request_type=proto_types.TXOUTPUT, details=proto_types.TxRequestDetailsType(request_index=0)),
    proto.TxRequest(request_type=proto_types.TXOUTPUT, details=proto_types.TxRequestDetailsType(request_index=1)),
    proto.TxRequest(request_type=proto_types.TXINPUT, details=proto_types.TxRequestDetailsType(request_index=0)),
    proto.TxRequest(request_type=proto_types.TXFINISHED),
    (signatures, serialized_tx) = self.client.sign_tx('Testnet', [inp1], [out1, out2])
    
    print("signature: \n", hexlify(serialized_tx))
    print("expected: \n", b'0100000000010137c361fb8f2d9056ba8c98c5611930fcb48cacfdd0fe2e0449d83eea982f91200000000017160014d16b8c0680c61fc6ed2e407455715055e41052f5ffffffff02e0aebb00000000001976a91414fdede0ddc3be652a0ce1afbc1b509a55b6b94888ac3df39f060000000017a91458b53ea7f832e8f096e896b8713a8c6df0e892ca8702483045022100ccd253bfdf8a5593cd7b6701370c531199f0f05a418cd547dfc7da3f21515f0f02203fa08a0753688871c220648f9edadbdb98af42e5d8269364a326572cf703895b012103e7bfe10708f715e8538c92d46ca50db6f657bbc455b7494e6a0303ccdb868b7900000000')

  def test_message_long(self):
    self.setup_mnemonic_nopin_nopassphrase()
    ret = self.client.verify_message(
      'Bitcoin',
      '1JwSSubhmg6iPtRjtyqhUYYH7bZg3Lfy1T',
      unhexlify('1bddc0aed9cf4e10dc9f57770934f4fb72a27c4510a0f4a81e09c163552416f799cd3f211ffeed0f411e9af9b927407d67115fb6d0ab1897137048efe33417fcc1'),
      "VeryLongMessage!" * 64
    )


def main():
  
  # bleSigntxSegwit().test_send_p2sh()
  bleSigntxSegwit().test_message_long()
  return
  
if __name__ == '__main__':
    main()
