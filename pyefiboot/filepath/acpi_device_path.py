"""
This file implements the ACPI Device Path (File Path Node parsing) classes within the pyefiboot library

Each class parses a single node, providing a string representation for display purposes
"""
# Import BaseNodePathParser sub-module classes
from .basenodepathparser import BaseNodePathParser


class ACPI_ACPIDevice_2_1(BaseNodePathParser):
    """ACPI (ACPI) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<II')

        self._log.debug('ACPI (ACPI) Device Path')

        self.__hid, self.__uid = self._fields

    def __str__(self) -> str:
        """:return: String representation of the ATAPI Node"""
        return f'ACPI(PNP{(self.__hid >> 16) & 0xffff:#04x},{self.__uid})'


# Class factory registration mapping ACPI Device node subtypes to the class for construction
ACPI_DEVICE_REGISTRY = {
    1: ACPI_ACPIDevice_2_1,
}
