"""
This file implements the OptionalData class within the pyefiboot library

OptionalData is an internal base class to decode the Optional Data within a UEFI BootEntry variable
"""
# Import System Libraries
import logging


class OptionalData:
    """
    OptionalData class - Decodes optional data within a UEFI BootEntry variable and provides access to internal data for display
    """
    def __init__(self, raw_data: bytes):
        """
        Parse the raw bytes object within a BootEntry variable as provided to the constructor and store within internal variables

        :param raw_data: Python bytes object containing data to be parsed
        """
        self.__log = logging.getLogger(self.__class__.__name__)

        self.__data: str | bytes = ''
        self.__raw_data: bytes = raw_data
        self.__log.debug(f'Initialising from raw data: {raw_data!r}')

        try:
            self.__log.info('Attempting to decode using UTF-16')
            self.__data = raw_data.decode('utf-16le')
            if self.__data.isprintable():
                self.__log.debug(f'Decoding string: {self.__data}')
                return
        except UnicodeDecodeError:
            pass

        try:
            self.__log.info('Attempting to decode using UTF-8')
            self.__data = raw_data.decode('utf-8')
            if self.__data.isprintable():
                self.__log.debug(f'Decoding string: {self.__data}')
                return
        except UnicodeDecodeError:
            pass

        hex_rep = ':'.join(f'{b:02x}' for b in raw_data)
        ascii_rep = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in raw_data)
        self.__data = f'Hex({hex_rep}) ASCII({ascii_rep})'
        self.__log.info(f'Not decodable - binary byte sequence ({self.__data})')

    def __str__(self):
        """:return: Return string representation of optional data for display"""
        return self.__data

    @property
    def raw_data(self) -> bytes:
        """:return: Return original bytes data containing optional data"""
        return self.__raw_data
