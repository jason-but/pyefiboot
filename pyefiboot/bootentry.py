
import struct
import pathlib

from pyefiboot.efivar import EFIVarBase
from pyefiboot.filepath import FilePath


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
                result = optional_data.decode('utf-16le', errors='ignore')
                if all(c.isprintable() or c.isspace() for c in result): return result

                # UTF-16 failed, try UTF-8
                result = optional_data.decode('utf-8', errors='ignore').strip('\x00')
                if all(c.isprintable() or c.isspace() for c in result): return result

            except UnicodeDecodeError:
                pass

            # Error decoding OR both UTF-16 and UTF-8 failed
            return '<Binary Data>'

        super().__init__(efivar_name, efivar_fullpath)

        # Ignore first four bytes of file
        data = self._raw_data

        # First 32-bits are the attributes, next 16-bits are loader location list length. All in little-endian
        attributes, path_list_length = struct.unpack("<IH", data[:6])
        self.attributes = attributes
        self.is_active = (attributes & 0x01) != 0
        self.is_force_reconnect = (attributes & 0x02) != 0
        self.is_hidden = (attributes & 0x08) != 0
        self._log.debug(f'Boot Entry Attributes: active={self.is_active}, force_reconnect={self.is_force_reconnect}, hidden={self.is_hidden}')

        # Remove parsed data
        data = data[6:]

        # Next is null terminated UTF-16 string with Boot Entry Label
        for null_index in range(0, len(data) - 1, 2):
            if data[null_index:null_index + 2] == b'\x00\x00': break
        else:
            raise ValueError("No UTF-16 null terminator found")

        self.label = data[:null_index].decode('utf-16le', errors='ignore')
        self._log.debug(f'Boot Entry Label: {self.label}')

        # Path list for Boot Entry starts 2 bytes after the null index and is of the precalculated length
        # Optional Data begins immediately after the path list
        path_list_data = data[null_index + 2:null_index + 2 + path_list_length]
        self.optional_data = decode_optional_data(data[null_index + 2 + path_list_length:])
        self._log.debug(f'Optional Data: {self.optional_data}')

        self.path_list: FilePath = FilePath(path_list_data)

    def __str__(self) -> str:
        """
        :return: Default string representation of the Boot Entry
        """
        return f'{'*' if self.is_active else ''} {self.label}'

    def verbose_str(self) -> str:
        """
        :return: Verbose string representation of the Boot Entry
        """
        return f'{self} - {self.path_list} - Extra({self.optional_data})'
