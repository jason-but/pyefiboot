"""
This file implements the Base Class for a File Path Node Parser

Allows registration of description, specification of fields for parsing, and creation of internal variables with decoded values
"""
# Import System Libraries
import struct
import logging


class BaseNodePathParser:
    """
    Base Node Path Device Path Parser

    Sub classes should call the super class constructor with the struct format string to decode the data contained within node_data

    Payload will be unpacked into fields as self._field, any remaining payload will be in self._unpacked_data
    """
    def __init__(self, node_data: bytes, struct_format: str = ''):
        """
        Base class constructor.

            1) Unpacks data in node_data using formatting from struct_format into self._fields
            2) Remaining payload is unpacked into self._unpacked_data

        :param node_data: Python bytes object containing data to be parsed
        :param struct_format: String containing the format of the data contained within node_data to be unpacked using struct.unpack()
        """
        # Create logger for this and subclasses to use
        self._log = logging.getLogger(self.__class__.__name__)

        if len(node_data) < struct.calcsize(struct_format): raise ValueError('Error in EFI Data format, node data is too small')

        # Unpack node_data into a tuple as defined by
        self._fields = struct.unpack(struct_format, node_data[:struct.calcsize(struct_format)])
        self._unpacked_data = node_data[struct.calcsize(struct_format):]
