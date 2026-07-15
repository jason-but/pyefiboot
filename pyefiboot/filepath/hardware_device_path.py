"""
This file implements the Hardware Device Path (File Path Node parsing) classes within the pyefiboot library

Each class parses a single node, providing a string representation for display purposes
"""
# Import System Libraries
import struct
import uuid

# Import BaseNodePathParser sub-module classes
from .basenodepathparser import BaseNodePathParser


class HardwarePCIDevice_1_1(BaseNodePathParser):
    """Hardware (PCI) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<BB')

        self._log.debug('Hardware (PCI) Device Path')

        self.__function, self.__device = self._fields

    def __str__(self) -> str:
        """:return: String representation of the PCI Node"""
        return f'PCI({self.__device:#04x},{self.__function:#04x})'


class HardwarePCCardDevice_1_2(BaseNodePathParser):
    """Hardware (PCCard) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<HH')

        self._log.debug('Hardware (PCCARD) Device Path')

        self.__target_id, self.__number = self._fields

    def __str__(self) -> str:
        """:return: String representation of the PCCard Node"""
        return f'SCSI(target={self.__target_id},{self.__number})'


class HardwareMemoryMappedDevice_1_3(BaseNodePathParser):
    """Hardware (Memory Mapped) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<LQQ')

        self._log.debug('Hardware (Memory Mapped) Device Path')

        self.__type, self.__mem_start, self.__mem_end = self._fields

    def __str__(self) -> str:
        """:return: String representation of the Memory Mapped Node"""
        return f'MemMapped({self.__mem_start:#08x}:{self.__mem_end:#08x},{self.__type})'


class HardwareVendorDevice_1_4(BaseNodePathParser):
    """Hardware (Vendor) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<16s')

        self._log.debug('Hardware (Vendor) Device Path')

        self.__vendor_guid = str(uuid.UUID(bytes_le=self._fields[0]))
        self.__vendor_data = self._unpacked_data.decode('utf-16le', errors='ignore').strip('\x00')

    def __str__(self) -> str:
        """:return: String representation of the Vendor Node"""
        return f'Vendor(uid={self.__vendor_guid},desc={self.__vendor_data})'


class HardwareControllerDevice_1_5(BaseNodePathParser):
    """Hardware (Controller) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<L')

        self._log.debug('Hardware (Controller) Device Path')

        self.__num, = self._fields

    def __str__(self) -> str:
        """:return: String representation of the Controller Node"""
        return f'Controller(id={self.__num})'


class HardwareBMCDevice_1_6(BaseNodePathParser):
    """Hardware (BMC) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<BQ')

        self._log.debug('Hardware (BMC) Device Path')

        self.__type, self.__address = self._fields

    def __str__(self) -> str:
        """:return: String representation of the BMC Node"""
        return f'BMC(type={self.__type},add={self.__address:#08x})'


# Class factory registration mapping Hardware Device node subtypes to the class for construction
HARDWARE_DEVICE_REGISTRY = {
    1: HardwarePCIDevice_1_1,
    2: HardwarePCCardDevice_1_2,
    3: HardwareMemoryMappedDevice_1_3,
    4: HardwareVendorDevice_1_4,
    5: HardwareControllerDevice_1_5,
    6: HardwareBMCDevice_1_6,
}
