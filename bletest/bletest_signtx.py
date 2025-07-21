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
    

  def test_one_two_fee(self):
    self.setup_mnemonic_nopin_nopassphrase()
    # tx: d5f65ee80147b4bcc70b75e4bbf2d7382021b871bd8867ef8fa525ef50864882
    # input 0: 0.0039 BT
    inp1 = proto_types.TxInputType(address_n=[0],  # 14LmW5k4ssUrtbAB4255zdqv3b4w1TuX9e
                         # amount=390000,
                         prev_hash=unhexlify('d5f65ee80147b4bcc70b75e4bbf2d7382021b871bd8867ef8fa525ef50864882'),
                         prev_index=0,
                         )
                         
    out1 = proto_types.TxOutputType(address='1MJ2tj2ThBE62zXbBYA5ZaN3fdve5CPAz1',
                          amount=390000 - 80000 - 10000,
                          script_type=proto_types.PAYTOADDRESS,
                          )
                      
    out2 = proto_types.TxOutputType(address_n=[1],
                          amount=80000,
                          script_type=proto_types.PAYTOADDRESS,
                          )
                          
    proto.TxRequest(request_type=proto_types.TXINPUT, details=proto_types.TxRequestDetailsType(request_index=0))
    proto.TxRequest(request_type=proto_types.TXMETA, details=proto_types.TxRequestDetailsType(tx_hash=unhexlify("d5f65ee80147b4bcc70b75e4bbf2d7382021b871bd8867ef8fa525ef50864882")))
    proto.TxRequest(request_type=proto_types.TXINPUT, details=proto_types.TxRequestDetailsType(request_index=0, tx_hash=unhexlify("d5f65ee80147b4bcc70b75e4bbf2d7382021b871bd8867ef8fa525ef50864882")))
    proto.TxRequest(request_type=proto_types.TXINPUT, details=proto_types.TxRequestDetailsType(request_index=1, tx_hash=unhexlify("d5f65ee80147b4bcc70b75e4bbf2d7382021b871bd8867ef8fa525ef50864882")))
    proto.TxRequest(request_type=proto_types.TXOUTPUT, details=proto_types.TxRequestDetailsType(request_index=0, tx_hash=unhexlify("d5f65ee80147b4bcc70b75e4bbf2d7382021b871bd8867ef8fa525ef50864882")))
    proto.TxRequest(request_type=proto_types.TXOUTPUT, details=proto_types.TxRequestDetailsType(request_index=0))
    proto.ButtonRequest(code=proto_types.ButtonRequest_ConfirmOutput)
    proto.TxRequest(request_type=proto_types.TXOUTPUT, details=proto_types.TxRequestDetailsType(request_index=1))
    proto.ButtonRequest(code=proto_types.ButtonRequest_ConfirmOutput)
    proto.ButtonRequest(code=proto_types.ButtonRequest_SignTx)
    proto.TxRequest(request_type=proto_types.TXINPUT, details=proto_types.TxRequestDetailsType(request_index=0))
    proto.TxRequest(request_type=proto_types.TXOUTPUT, details=proto_types.TxRequestDetailsType(request_index=0))
    proto.TxRequest(request_type=proto_types.TXOUTPUT, details=proto_types.TxRequestDetailsType(request_index=1))
    proto.TxRequest(request_type=proto_types.TXOUTPUT, details=proto_types.TxRequestDetailsType(request_index=0))
    proto.TxRequest(request_type=proto_types.TXOUTPUT, details=proto_types.TxRequestDetailsType(request_index=1))
    proto.TxRequest(request_type=proto_types.TXFINISHED)
    
    (signatures, serialized_tx) = self.client.sign_tx('Bitcoin', [inp1, ], [out1, out2])
                                                          
    print("signature: \n", hexlify(serialized_tx))
    print("expected: \n", b'010000000182488650ef25a58fef6788bd71b8212038d7f2bbe4750bc7bcb44701e85ef6d5000000006b483045022100c1400d8485d3bdcae7413e123148f35ece84806fc387ab88c66b469df89aef1702201d481d04216b319dc549ffe2333143629ba18828a4e2d1783ab719a6aa263eb70121023230848585885f63803a0a8aecdd6538792d5c539215c91698e315bf0253b43dffffffff02e0930400000000001976a914de9b2a8da088824e8fe51debea566617d851537888ac80380100000000001976a9140223b1a09138753c9cb0baf95a0a62c82711567a88ac00000000')
    

def main():
  
  bleSigntxSegwit().test_one_two_fee()
  return
  
if __name__ == '__main__':
    main()
