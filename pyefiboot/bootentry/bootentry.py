
import struct
import pathlib

from pyefiboot.efivar import EFIVarBase
from pyefiboot.bootentry.filepath import FilePath
from pyefiboot.bootentry.optionaldata import OptionalData


class BootEntry(EFIVarBase):
    def __init__(self, efivar_name: str | None = None, efivar_fullpath: pathlib.Path | None = None) -> None:
        """
        Read an EFI Variable represented as a single integer from the EFI file and store in __value

        .. warning::
           ONLY one of global_namespace or efivar_fullpath must be provided

        :param efivar_name: EFI variable name to read
        :param efivar_fullpath: Fully qualified path of the EFI Variable file
        """
        def decode_optional_data(optional_data: bytes) -> str:
            try:
                # Try decoding using UTF-16 first
                result = optional_data.decode('utf-16le').strip('\x00')
                if result.isprintable(): return result + ' - ' + ':'.join(f'{b:02x}' for b in optional_data)
            except UnicodeDecodeError:
                pass

            try:
                # Try decoding using UTF-16 first
                result = optional_data.decode('utf-8').strip('\x00')
                if result.isprintable(): return result
            except UnicodeDecodeError:
                pass

            return ':'.join(f'{b:02x}' for b in optional_data) + ' - ' + ''.join(chr(b) if 32 <= b <= 126 else '.' for b in optional_data)

            try:
                if len(optional_data) > 1 and 0 in optional_data[:2]:
                    # If optional_data has at least two bytes AND one of these is a zero byte, then this could be a UTF-16 string, otherwise definitely NOT UTF-16
                    result = optional_data.decode('utf-16le', errors='ignore')
                    if all(c.isprintable() or c.isspace() for c in
                           result): return f'{result}raw<{optional_data}>u8<{optional_data.decode("utf-8", errors='ignore')}>'

                # UTF-16 failed, try UTF-8
                result = optional_data.decode('utf-8', errors='ignore').strip(' \x00')
                if all(c.isprintable() or c.isspace() for c in result): return f'{result}raw<{optional_data}>u8<{optional_data.decode("utf-8", errors='ignore')}>'

            except UnicodeDecodeError:
                pass

            # Error decoding OR both UTF-16 and UTF-8 failed
            return f'<Binary Data>raw<{optional_data}>u8<{optional_data.decode("utf-8", errors='ignore')}>u16<{optional_data.decode("utf-16le", errors="ignore")}>'

        super().__init__(efivar_name, efivar_fullpath)

        self.__index: str = self.efivar_name[4:]
        self._log.debug(f'Boot Entry Index: {self.__index}')

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

        # Extract Boot Entry Labelself._raw_data[label_index:null_index] maps to UTF-16 string excluding NULL terminator
        self.__label = self._raw_data[label_index:null_index].decode('utf-16le', errors='ignore')
        self._log.debug(f'Boot Entry Label: {self.__label}')

        # Decode File Path List
        self.__path_list: FilePath = FilePath(self._raw_data[path_list_index:optional_data_index])
        self._log.debug(f'File Path Data: {self.__path_list}')

        # Decode Optional Data
        self.__optional_data = OptionalData(self._raw_data[optional_data_index:])
        self._log.debug(f'Optional Data: {self.__optional_data}')

    def __str__(self) -> str:
        """
        :return: Default string representation of the Boot Entry
        """
        return f'Boot{self.__index}{'*' if self.__is_active else ''} {self.__label}'

    def verbose_str(self) -> str:
        """
        :return: Verbose string representation of the Boot Entry
        """
        return f'{self} - {self.__path_list} - Extra({self.__optional_data})'

    # ---------- PROPERTIES ----------
    @property
    def entry_num(self) -> str:
        """:return: Boot Entry index number as a four character hexadecimal string"""
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
    def kernel_file(self) -> str | None:
        """:return: Boot Entry kernel file to load if it exists, otherwise None"""
        return self.__path_list.kernel_file

    @property
    def label(self) -> str:
        """:return: Boot Entry label"""
        return self.__label

    @property
    def file_paths(self) -> list[str]:
        """:return: List of file paths to load"""
        return self.__path_list.str_path_lists

    @property
    def optional_data(self) -> OptionalData:
        """:return: Optional data from this Boot Entry"""
        return self.__optional_data
