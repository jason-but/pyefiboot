"""
This file implements the ACPI Device Path (File Path Node parsing) classes within the pyefiboot library

Each class parses a single node, providing a string representation for display purposes
"""
# Import System Libraries
import struct
import logging


class ADP_2_1_ACPI:
    """ACPI (ACPI) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('ACPI (ACPI) Device Path')

        self.__hid, self.__uid = struct.unpack('<II', node_data)

    def __str__(self) -> str:
        """:return: String representation of the ATAPI Node"""
        return f'ACPI(PNP{(self.__hid >> 16) & 0xffff:#04x},{self.__uid})'


# Class factory registration mapping ACPI Device node subtypes to the class for construction
ACPI_DEVICE_REGISTRY = {
    1: {'len': 12, 'class': ADP_2_1_ACPI},
}