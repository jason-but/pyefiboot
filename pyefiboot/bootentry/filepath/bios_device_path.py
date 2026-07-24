"""
This file implements the BIOS Boot Specification Device Path (File Path Node parsing) classes within the pyefiboot library

Each class parses a single node, providing a string representation for display purposes
"""
# Import BaseNodePathParser sub-module classes
from .basenodepathparser import BaseNodePathParser


class BIOS_BootDevice_5_1(BaseNodePathParser):
    """BIOS (BIOS Boot Specification) Device Path Parser"""

    # Lookup table mapping BIOS Device Type to string description
    type_lookup = {0x00: 'Reserved', 0x01: 'Floppy', 0x02: 'HardDisk', 0x03: 'CD-ROM', 0x04: 'PCMCIA', 0x05: 'USB', 0x06: 'Embedded Network', 0x80: 'BEV'}

    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<HH')

        self._log.debug('BIOS Boot Specification Device Path')

        self.__type, self.__flag = self._fields
        self.__description = self._unpacked_data.split(b'\x00', 1)[0].decode('ascii')

    def __str__(self) -> str:
        """:return: String representation of the ATAPI Node"""
        return f'BIOS({BIOS_BootDevice_5_1.type_lookup.get(self.__type, 'Unknown')},{self.__description},{self.__flag:#06x})'


# Class factory registration mapping ACPI Device node subtypes to the class for construction
BIOS_DEVICE_REGISTRY = {
    1: BIOS_BootDevice_5_1,
}
