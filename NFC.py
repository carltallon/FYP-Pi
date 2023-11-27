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

# Run application
if __name__ == '__main__':
    pn532 = PN532_UART(debug=True) 

    ic, ver, rev, support = pn532.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

    def create_text_ndef_record(text_content):
        #Create an NDEF Text record
        # Define the payload for an NDEF Text record (assuming UTF-8 encoding)
        language_code = 'en'  # Language code (e.g., 'en' for English)
        text_payload = bytes([len(language_code)]) + language_code.encode('utf-8') + text_content.encode('utf-8')

        # Determine the payload length
        payload_len = len(text_payload)

        # Define the NDEF message
        # The structure follows the NDEF standard: [MB(1) | ME(1) | CF(1) | SR(1) | IL(1) | TNF(3) | TYPE LENGTH(1) | PAYLOAD LENGTH(1+) | TYPE(1+) | PAYLOAD(0+)]
        ndef_message = bytes([
            0b11010000,  # MB: Message Begin and ME: Message End flags for the first and only record
            0x01,        # Type length (1 byte)
            payload_len + 1,  # Payload length (1 byte for language code + text content length)
            0x54         # TNF (Type Name Format): 0x54 for well-known type 'T' (Text)
        ]) + b'T' + text_payload  # 'T' denotes a Text record

        return ndef_message

    text_content = "TEST 1"
    data_to_write = create_text_ndef_record(text_content)
    # Perform NFC tasks (specific actions depend on your application)
    # Example:

    #pn532.write_to_tag(data_to_write)  # Write data to an NFC tag