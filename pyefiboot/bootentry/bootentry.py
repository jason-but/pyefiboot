
import struct
import pathlib

# from pyefiboot import BootManager
from pyefiboot.efivar import EFIVarBase
from pyefiboot.bootentry.filepath import FilePath
from pyefiboot.bootentry.optionaldata import OptionalData


class BootEntry(EFIVarBase):
    """
    BootEntry class - Stores the EFI Boot Order Variable

    Can be created via directly loading an existing EFI Boot Entry variable, or via calling the static create_new() method which will create a new variable
    using efibootmgr and then create an instance of BootEntry mapped to the newly created variable

    This class allows extraction of current BootEntry data for display to screen or processing
    """
    def __init__(self, efivar_name: str | None = None, efivar_fullpath: pathlib.Path | None = None) -> None:
        """
        Inherit from the base class to read the BootEntry variable

        The base class will load the variable raw data into self._raw_data and the actual variable name in self.efivar_name

        The contents of the bytes array self._raw_data are decoded into internal variables

        **WARNING: ONLY one of global_namespace or efivar_fullpath must be provided**

        :param efivar_name: EFI variable name to read
        :param efivar_fullpath: Fully qualified path of the EFI Variable file
        """
        super().__init__(efivar_name, efivar_fullpath)

        self.__hex_index: str = self.efivar_name[4:]
        self.__index: int = int(self.__hex_index, base=16)
        self._log.debug(f'Boot Entry Index: {self.__hex_index} ({self.__index})')

        self.__attributes: int = 0
        self.__path_list_length: int = 0
        self.__is_active: bool = False
        self.__is_force_reconnecting: bool = False
        self.__is_hidden: bool = False
        self.__label: str = ''
        self.__path_list: FilePath | None = None
        self.__optional_data: OptionalData | None = None

        self._parse_raw_data()

    def _parse_raw_data(self) -> None:
        # Layout of data within BootEntry
        # +------------+---------------+------------------------------------+---------------------+---------------+
        # |   32-bits  |    16-bits    |           unknown length           | File Path Len bytes | rest of data  |
        # | Attributes | File Path Len | UTF-16 Null Terminated Entry Label | File Path List      | Optional Data |
        # +------------+---------------+------------------------------------+---------------------+---------------+

        # Extract attributes and File Path List Length
        self.__attributes, path_list_length = struct.unpack("<IH", self._raw_data[:6])
        self.__is_active = (self.__attributes & 0x01) != 0
        self.__is_force_reconnect = (self.__attributes & 0x02) != 0
        self.__is_hidden = (self.__attributes & 0x08) != 0
        self._log.debug(f'Boot Entry Attributes: active={self.__is_active}, force_reconnect={self.__is_force_reconnect}, hidden={self.__is_hidden}')

        # Next block is a null terminated UTF-16 string with Boot Entry Label, find the index of the null terminated-string
        label_index = 6

        # Find index of UTF-16 Null Terminator in Label
        for null_index in range(label_index, len(self._raw_data) - 1, 2):
            if self._raw_data[null_index:null_index + 2] == b'\x00\x00': break
        else:
            raise ValueError("No UTF-16 null terminator found")

        # File Path list for Boot Entry starts 2 bytes after the null index
        path_list_index = null_index + 2

        # Optional Data for Boot Entry is immediately after the path list
        optional_data_index = path_list_index + path_list_length

        # Extract Boot Entry Label - self._raw_data[label_index:null_index] maps to UTF-16 string excluding NULL terminator
        self.__label = self._raw_data[label_index:null_index].decode('utf-16le', errors='ignore')
        self._log.debug(f'Boot Entry Label: {self.__label}')

        # Decode File Path List
        self.__path_list: FilePath = FilePath(self._raw_data[path_list_index:optional_data_index])
        self._log.debug(f'File Path Data: {self.__path_list}')

        # Decode Optional Data
        self.__optional_data = OptionalData(self._raw_data[optional_data_index:])
        self._log.debug(f'Optional Data: {self.__optional_data}')

    def refresh(self) -> None:
        """Re-read the current EFI variable from NVRAM (base class function) and reset internal state by decoding stored value"""
        super().refresh()
        self._parse_raw_data()
        self._log.info(f'Boot Entry details reloaded')

    def __str__(self) -> str:
        """:return: Default string representation of the Boot Entry"""
        return f'Boot{self.__index:04X}{'*' if self.__is_active else ''} {self.__label}'

    def verbose_str(self) -> str:
        """:return: Default string representation of the Boot Entry"""
        return f'{self}\n - File Path:{'\n    - ' if len(self.file_paths) > 1 else '     '}{'\n    - '.join(self.file_paths)}\n - Optional Data: {self.__optional_data}'

    def __repr__(self) -> str:
        """:return: Verbose string representation of the Boot Entry"""
 #       return f'{self.__class__.__name__}(variable={self.efivar_name}))'
        return f'{self.__class__.__name__}(variable={self.efivar_name}, path={self.efivar_fullpath}))'
#        return f'{self.__class__.__name__}(variable={self.efivar_name}, path={self.efivar_fullpath}, value={self._value}({self.hex_value}))'

    def delete(self) -> None:
        """
        Delete this Boot Entry UEFI variable

        **NOTE**: Class instance will be invalid after calling this method. Should delete instance
        """
        self._log.debug(f'Deleting Boot Entry {self.__index} variable')
        self._delete()

    # ---------- PROPERTIES ----------
    @property
    def hex_index(self) -> str:
        """:return: Boot Entry index number as a four character hexadecimal string"""
        return self.__hex_index

    @property
    def index(self) -> int:
        """:return: Boot Entry index number as an integer"""
        return self.__index

    @property
    def active(self) -> bool:
        """:return: Whether this Boot Entry is active"""
        return self.__is_active

    @property
    def force_reconnect(self) -> bool:
        """:return: Whether this Boot Entry has the Force Reconnect flag set"""
        return self.__is_force_reconnect

    @property
    def hidden(self) -> bool:
        """:return: Whether this Boot Entry is hidden"""
        return self.__is_hidden

    @property
    def label(self) -> str:
        """:return: Boot Entry label"""
        return self.__label

    @property
    def kernel_file(self) -> str | None:
        """:return: Boot Entry kernel file to load if it exists, otherwise None"""
        return self.__path_list.kernel_file

    @property
    def file_paths(self) -> list[str]:
        """:return: List of file paths to load"""
        return self.__path_list.str_path_lists

    @property
    def optional_data(self) -> OptionalData:
        """:return: Optional data from this Boot Entry"""
        return self.__optional_data
