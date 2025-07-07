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
import importlib
import logging
import sys
import time
import atexit

from .transport import Transport, ConnectionError

from .bleClient import BLECLIENT


class FakeRead(object):
    # Let's pretend we have a file-like interface
    def __init__(self, func):
        self.func = func

    def read(self, size):
        return self.func(size)

class BleTransport(Transport):

  def __init__(self, device, *args, **kwargs):
    self.loop = asyncio.get_event_loop()
    self.bc = BLECLIENT()
    super(BleTransport, self).__init__(device, *args, **kwargs)
   
  def _open(self, name="kkcomm-server"):
    self.loop.run_until_complete(self.bc.scanForDevice(name))
    return
    
  def _close(self):
    return
    
  def ready_to_read(self):
    return self.bc.readFinished
 
  def _write(self, msg, protobuf_msg):
    self.bc.txbuffer = bytearray()
    msg = bytearray(msg)

    # add reportID
    self.bc.txbuffer = ([63, ] + list(msg[:len(msg)]))
    msgLen = len(self.bc.txbuffer)
    indx = 64
    while msgLen > 64:
      self.bc.txbuffer.insert(indx, 63)
      msgLen = len(self.bc.txbuffer[indx:])
      indx += 64
      
    # print(".............writing in transport_ble")
    # print(self.bc.txbuffer)

    self.bc.txReady = True
    try:
      # self.loop.run_until_complete(self.bc.bleWriteHandler())
      self.loop.run_until_complete(self.bc.bleHandler())
    except Exception as e:
      print("exception ", e)
      print("exiting...")
      sys.exit()
    return
  
  
  def _read(self):
    # try:
    #   while (self.bc.readFinished == False):
    #     print("......... notified: ready to read")
    #     # self.loop.run_until_complete(self.bc.bleReadHandler())
    #     continue
    # except Exception as e:
    #   print("read exception ", e)
    #   print("exiting...")
    #   sys.exit()
    
    data = self.bc.dataRx
    # "?##"+<2_byte_msg_type>+<4_byte_msg_len>+<msg>

    msgLen = int.from_bytes(data[5:9], byteorder='big')
    
    # reset the read buffer vars
    self.bc.dataRx = bytearray()
    self.bc.rxDone = False
    self.bc.readReady = False
  
    return (int.from_bytes(data[3:5], byteorder='big'), bytes(data[9:(9+msgLen)]))
