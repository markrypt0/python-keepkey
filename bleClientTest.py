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

import asyncio
import sys
from itertools import count, takewhile
from typing import Iterator
import struct

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

from keepkeylib.bleClient import BLECLIENT

# 16 Bit SPP Service UUID 
BLE_SVC_SPP_UUID16 = "ABF0"

# 16 Bit SPP Service Characteristic UUID 
# BLE_SVC_SPP_CHR_UUID16 = "ABF1"
BLE_SVC_SPP_CHR_UUID16 = '0000abf1-0000-1000-8000-00805f9b34fb'

# TIP: you can get this function and more from the ``more-itertools`` package.
def sliced(data: bytes, n: int) -> Iterator[bytes]:
    """
    Slices *data* into chunks of size *n*. The last slice may be smaller than
    *n*.
    """
    return takewhile(len, (data[i : i + n] for i in count(0, n)))
    
class BleTransport():

  def __init__(self):
    self.bc = BLECLIENT()
    self.loop = asyncio.get_event_loop()
   
  def open(self, name):
    self.loop.run_until_complete(self.bc.scanForDevice(name))
    return
    
  def close(self):
    return
    
  def ready_to_read(self):
    return self.bc.readFinished
    
  def write(self, data):

    # # send message as bytes beginning with magic chars, then packed struct of data len, data
    # fstr = "<L"+str(len(data))+"s"
    # self.bc.txbuffer = bytearray('##', 'utf-8') + struct.pack(fstr, len(data), data)
    self.bc.txbuffer = data
    self.bc.txReady = True
    try:
      self.loop.run_until_complete(self.bc.bleHandler())    # completes with notify
    except Exception as e:
      print("exception ", e)
      print("exiting...")
      sys.exit()
    return

  def read(self):
    data = self.bc.dataRx
    # "?##"+<2_byte_msg_type>+<4_byte_msg_len>+<msg>

    msgLen = int.from_bytes(data[5:9], byteorder='big')
    
    # reset the read buffer vars
    self.bc.dataRx = bytearray()
    self.bc.rxDone = False
    self.bc.readReady = False
  
    return (int.from_bytes(data[3:5], byteorder='big'), bytes(data[9:(9+msgLen)]))

def main():
  bufferSize = 12*1024 - 9
  msgBuf = bytearray(bufferSize)
  try:
    bt = BleTransport()

    bt.open("kkcomm-server")

    # Implement a write/read loop for BLE
    # data = b'1234567890'
    
    
    # f = open("./helloworld.py", "rb")
    # mbuf = f.read()
    # # numBytes = f.readinto(msgBuf)

    # header = bytearray(b'?##\0\0') + len(mbuf).to_bytes(4, byteorder='big')
    # print(header)
    # print(header+mbuf)
    # bt.write(header+mbuf)

    bt.write(b'?##\x00\x00\x00\x00\x00\x00')
    
    # f = open("./helloworld.py", "rb")
    # bt.write(f.read())
    
    # data = b'1234567890abcdefghijklmnopqrstuvwxyz'
    # bt.write(data)

    while bt.ready_to_read() == False:
      continue
    resp = bt.read()
    print("read len", len(resp), "\n", resp)

  except KeyboardInterrupt:
    del bt
    print('done')


if __name__ == '__main__':
    main()
