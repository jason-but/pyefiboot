"""
This file implements the Hardware Device Path (File Path Node parsing) classes within the pyefiboot library

Each class parses a single node, providing a string representation for display purposes
"""
# Import System Libraries
import struct
import logging
import uuid


class HDP_1_1_PCI:
    """Hardware (PCI) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Hardware (PCI) Device Path')

        self.__function, self.__device = struct.unpack('<BB', node_data)

    def __str__(self) -> str:
        """:return: String representation of the PCI Node"""
        return f'PCI({self.__device:#04x},{self.__function:#04x})'


class HDP_1_2_PCCARD:
    """Hardware (PCCard) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Hardware (PCCARD) Device Path')

        self.__target_id, self.__number = struct.unpack('<HH', node_data)

    def __str__(self) -> str:
        """:return: String representation of the PCCard Node"""
        return f'SCSI(target={self.__target_id},{self.__number})'


class HDP_1_3_MemoryMapped:
    """Hardware (Memory Mapped) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Hardware (Memory Mapped) Device Path')

        self.__type, self.__mem_start, self.__mem_end = struct.unpack('<LQQ', node_data)

    def __str__(self) -> str:
        """:return: String representation of the Memory Mapped Node"""
        return f'MemMapped({self.__mem_start:#08x}:{self.__mem_end:#08x},{self.__type})'


class HDP_1_4_Vendor:
    """Hardware (Vendor) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Hardware (Vendor) Device Path')

        self.__vendor_guid = str(uuid.UUID(bytes_le=node_data[:16]))
        self.__vendor_data = node_data[16:].decode('utf-16le', errors='ignore').strip('\x00')

    def __str__(self) -> str:
        """:return: String representation of the Vendor Node"""
        return f'Vendor(uid={self.__vendor_guid},desc={self.__vendor_data})'


class HDP_1_5_Controller:
    """Hardware (Controller) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Hardware (Controller) Device Path')

        self.__num = struct.unpack('<L', node_data)

    def __str__(self) -> str:
        """:return: String representation of the Controller Node"""
        return f'Controller(id={self.__num})'


class HDP_1_6_BMC:
    """Hardware (BMC) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Hardware (BMC) Device Path')

        self.__type, self.__address = struct.unpack('<BQ', node_data)

    def __str__(self) -> str:
        """:return: String representation of the BMC Node"""
        return f'BMC(type={self.__type},add={self.__address:#08x})'


# Class factory registration mapping Hardware Device node subtypes to the class for construction
HARDWARE_DEVICE_REGISTRY = {
    1: {'len': 6, 'class': HDP_1_1_PCI},
    2: {'len': 5, 'class': HDP_1_2_PCCARD},
    3: {'len': 24, 'class': HDP_1_3_MemoryMapped},
    4: {'len': 0, 'class': HDP_1_4_Vendor},
    5: {'len': 8, 'class': HDP_1_5_Controller},
    6: {'len': 13, 'class': HDP_1_6_BMC},
}
