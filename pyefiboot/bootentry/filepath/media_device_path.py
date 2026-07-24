"""
This file implements the Media Device Path (File Path Node parsing) classes within the pyefiboot library

Each class parses a single node, providing a string representation for display purposes
"""
# Import System Libraries
import struct
import uuid

# Import BaseNodePathParser sub-module classes
from .basenodepathparser import BaseNodePathParser


class MediaHardDiskDevice_4_1(BaseNodePathParser):
    """Media (Hard Disk) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<IQQ16sBB')

        self._log.debug('Media (Hard Disk) Device Path')

        self.__part_no, self.__part_start, self.__part_size, part_sig, self.__part_format, self.__sig_type = self._fields

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


class MediaCDDevice_4_2(BaseNodePathParser):
    """Media (CD) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<LQQ')

        self._log.debug('Media (CD) Device Path')

        self.__number, self.__part_start, self.__part_size, part_sig, self.__part_format, self.__sig_type = self._fields

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


class MediaFileDevice_4_4(BaseNodePathParser):
    """Media (File) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '')
        self._log.debug('Media (File) Device Path')

        self.__file_path = self._unpacked_data.decode("utf-16le", errors='ignore')

    def __str__(self) -> str:
        """:return: String representation of the File Node"""
        return f'Path({self.__file_path})'

    @property
    def kernel_file(self) -> str:
        return self.__file_path


class MediaPIFirmwareFileDevice_4_6(BaseNodePathParser):
    """Media (PIWG Firmware File) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '')
        self._log.debug('Media (PIWG Firmware File) Device Path')

        self.__path = uuid.UUID(bytes_le=self._unpacked_data)

    def __str__(self) -> str:
        """:return: String representation of the File Node"""
        return f'FirmwareFile({self.__path})'


class MediaPIFirmwareVolumeDevice_4_7(BaseNodePathParser):
    """Media (PIWG Firmware Volume) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '')
        self._log.debug('Media (PIWG Firmware Volume) Device Path')

        self.__path = uuid.UUID(bytes_le=self._unpacked_data)

    def __str__(self) -> str:
        """:return: String representation of the File Node"""
        return f'FirmwareVolume({self.__path})'


# Class factory registration mapping Hardware Device node subtypes to the class for construction
MEDIA_DEVICE_REGISTRY = {
    1: MediaHardDiskDevice_4_1,
    2: MediaCDDevice_4_2,
    4: MediaFileDevice_4_4,
    6: MediaPIFirmwareFileDevice_4_6,
    7: MediaPIFirmwareVolumeDevice_4_7
}
