# Waveshare PN532 NFC Hat control library.
# Author: Yehui from Waveshare
#
# The MIT License (MIT)
#
# Copyright (c) 2015-2018 Adafruit Industries
# Copyright (c) 2019 Waveshare
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
This module will let you communicate with a PN532 RFID/NFC chip
using UART (ttyS0) on the Raspberry Pi.
"""

import RPi.GPIO as GPIO
from pn532 import *
import ndef


# Run application
def writeNFC(receipt_id):
    
    pn532 = PN532_UART(debug=True) 

    ic, ver, rev, support = pn532.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

    print("Receipt ID = ", receipt_id)
    message = ndef.TextRecord(receipt_id, encoding='UTF-8')
    
    ndef_message = [message]
    
    ndef_bytes = ndef.message_encoder(ndef_message)
    
    print("Receipt ID in NDEF = ",ndef_bytes)


    print('Waiting for RFID/NFC card to write to!')
    while True:
        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=0.5)
        print('.', end="")
        if uid is not None:
            break
    print('Found card with UID:', [hex(i) for i in uid])
    
    # Write block #6
    block_number = 1
    data = ndef_bytes
    
    try:
        pn532.ntag2xx_write_block(block_number, data)
        if pn532.ntag2xx_read_block(block_number) == data:
            print('write block %d successfully' % block_number)
    except nfc.PN532Error as e:
        print(e.errmsg)
        
    
