"""
This file implements the Media Device Path (File Path Node parsing) classes within the pyefiboot library

Each class parses a single node, providing a string representation for display purposes
"""
# Import System Libraries
import struct
import logging
import uuid


class MDP_4_1_HD:
    """Media (Hard Disk) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Media (Hard Disk) Device Path')

        self.__part_no, self.__part_start, self.__part_size, part_sig, self.__part_format, self.__sig_type = struct.unpack('<IQQ16sBB', node_data)

        self.__signature = ''

        match self.__part_format:
            case 1:
                self.__part_format = 'MBR'
                self.__signature = hex(struct.unpack('<I', part_sig[:4])[0])
            case 2:
                self.__part_format = 'GPT'
                self.__signature = str(uuid.UUID(bytes_le=part_sig))

    def __str__(self) -> str:
        """:return: String representation of the Hard Disk Node"""
        return f'HD(part={self.__part_no}<{self.__part_start:#x},{self.__part_size:#x}>,{self.__part_format},sig={self.__signature})'


class MDP_4_2_CD:
    """Media (CD) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Media (CD) Device Path')

        self.__number, self.__part_start, self.__part_size, part_sig, self.__part_format, self.__sig_type = struct.unpack('<LQQ', node_data)

        self.__signature = ''

        match self.__part_format:
            case 1:
                self.__part_format = 'MBR'
                self.__signature = hex(struct.unpack('<I', part_sig[:4])[0])
            case 2:
                self.__part_format = 'GPT'
                self.__signature = str(uuid.UUID(bytes_le=part_sig))

    def __str__(self) -> str:
        """:return: String representation of the CD Node"""
        return f'HD(part={self.__part_no}<{self.__part_start:#x},{self.__part_size:#x}>, {self.__part_format}, sig={self.__signature})'


class MDP_4_4_File:
    """Media (File) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Media (File) Device Path')

        self.__file_path = node_data.decode("utf-16le", errors='ignore')

    def __str__(self) -> str:
        """:return: String representation of the File Node"""
        return f'Path({self.__file_path})'

    @property
    def kernel_file(self) -> str:
        return self.__file_path


# Class factory registration mapping Hardware Device node subtypes to the class for construction
MEDIA_DEVICE_REGISTRY = {
    1: {'len': 42, 'class': MDP_4_1_HD},
    2: {'len': 24, 'class': MDP_4_2_CD},
    4: {'len': 0, 'class': MDP_4_4_File},
}
