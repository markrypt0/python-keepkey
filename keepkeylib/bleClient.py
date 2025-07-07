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

class BLECLIENT:
  def __init__(self):
    self.device = None
    self.dataRx = bytearray()
    self.txbuffer = ""
    self.txReady = False
    self.readReady = False
    self.readFinished = True
    self.notifyOn = False
    
    self.msgLen = 0

        
  def _handle_disconnect(self, _: BleakClient):
    # print("Device was disconnected")
    return
      
  def _handle_notify(self, _: BleakGATTCharacteristic, rx_data: bytearray):
    # each message should be a byte stream of the structure "?##"+<2_byte_msg_type>+<4_byte_msg_len>+<msg>
    # print(rx_data)
    if (rx_data[:10] == bytearray(b'readready\x00')):
      self.readReady = True
      print("NOTIFIED: ready to read")
    else:
      print("Error: ", rx_data)
  
  async def scanForDevice(self, name):
    self.device = await BleakScanner.find_device_by_name(name)

    if self.device is None:
        print("No device named %s found." % name)
        sys.exit()
    
  async def bleHandler(self):
    print("handler entry")
    # this does the full write-get_notified-read loop to make comm more efficient
  
    async with BleakClient(self.device, disconnected_callback=self._handle_disconnect) as client:
      nus = client.services.get_service(BLE_SVC_SPP_UUID16)
      # print("Connected...")
      
      self.rx_char = nus.get_characteristic(BLE_SVC_SPP_CHR_UUID16)
      
      if self.txReady:
        await client.start_notify(BLE_SVC_SPP_CHR_UUID16, self._handle_notify)
        # self.rx_char = nus.get_characteristic(BLE_SVC_SPP_CHR_UUID16)
        sctr = 0
        for s in sliced(self.txbuffer, 20):
          # print("slice s ", s)
          # print(sctr)
          sctr+=1
          await client.write_gatt_char(self.rx_char, s, response=True)
        print("sent %d bytes:" % len(self.txbuffer), self.txbuffer)
        self.txbuffer=""
        self.txReady = False
        self.readFinished = False
        
        # wait for notification of read ready to prevent disconnect
        while self.readReady == False:
          await asyncio.sleep(0)

      # now read
      
      # print("ble reading")
      self.readReady = False
      try:
        rxData = await client.read_gatt_char(self.rx_char)
        # print(bytes(rxData).hex(' '))
      except Exception as e:
        print("exception on read ", e)
        print("exiting...")
        sys.exit()
      
      if len(self.dataRx) == 0:
        # first packet, strip magic and get length
        if (rxData[0:3] == bytearray('?##', 'utf-8')):
          self.msgLen = int.from_bytes(rxData[5:9], byteorder='big')      # access unpacked tuple as int
          # print(rxData[5:9])
          # print(" msgLen dataRx")
          # print(self.msgLen, self.dataRx)
          # print(bytes(rxData).hex(' '))
          self.dataRx.extend(rxData)
          
      while len(self.dataRx) < self.msgLen+9:
        # print("datalen msglen", len(self.dataRx), self.msgLen+9)
        # get rest of packets
        rxData = await client.read_gatt_char(self.rx_char)
        self.dataRx.extend(rxData)
        # print(bytes(rxData).hex(' '))

      self.readFinished = True
      # print("ready to read")
      # print(self.dataRx)
      print("ble handler exit")
        
      return
    

  async def bleWriteHandler(self):
    async with BleakClient(self.device, disconnected_callback=self._handle_disconnect) as client:
      nus = client.services.get_service(BLE_SVC_SPP_UUID16)
      # print("Connected...")
      
      self.rx_char = nus.get_characteristic(BLE_SVC_SPP_CHR_UUID16)
      
      if self.txReady:
        await client.start_notify(BLE_SVC_SPP_CHR_UUID16, self._handle_notify)
        # self.rx_char = nus.get_characteristic(BLE_SVC_SPP_CHR_UUID16)
        sctr = 0
        for s in sliced(self.txbuffer, 20):
          # print("slice s ", s)
          # print(sctr)
          sctr+=1
          await client.write_gatt_char(self.rx_char, s, response=True)
        print("sent %d bytes:" % len(self.txbuffer), self.txbuffer)
        self.txbuffer=""
        self.txReady = False
        self.readFinished = False
        
        # wait for notification of read ready to prevent disconnect
        while self.readReady == False:
          await asyncio.sleep(0)

      return
    
    
  async def bleReadHandler(self):
    async with BleakClient(self.device, disconnected_callback=self._handle_disconnect) as client:
      nus = client.services.get_service(BLE_SVC_SPP_UUID16)
      # print("Connected...")
      
      self.rx_char = nus.get_characteristic(BLE_SVC_SPP_CHR_UUID16)
      
      if self.readReady:
        # print("reading")
        self.readReady = False
        try:
          rxData = await client.read_gatt_char(self.rx_char)
          # print(bytes(rxData).hex(' '))

        except Exception as e:
          print("exception on read ", e)
          print("exiting...")
          sys.exit()
        
        if len(self.dataRx) == 0:
          # first packet, strip magic and get length
          if (rxData[0:3] == bytearray('?##', 'utf-8')):
            self.msgLen = int.from_bytes(rxData[5:9], byteorder='big')      # access unpacked tuple as int
            # print(rxData[5:9])
            # print(" msgLen dataRx")
            # print(self.msgLen, self.dataRx)
            # print(bytes(rxData).hex(' '))
            self.dataRx.extend(rxData)
            
        while len(self.dataRx) < self.msgLen+9:
          # get rest of packets
          rxData = await client.read_gatt_char(self.rx_char)
          self.dataRx.extend(rxData)
          # print(bytes(rxData).hex(' '))
 
        self.readFinished = True
        # print("ready to read")
        # print(self.dataRx)
        
      return
