"""
This file implements the EFIVarInt class within the pyefiboot library

EFIVarInt is an internal base class to read and parse and EFI Variable that contains a single integer
"""
# Import System Libraries
import pathlib

# Import efivar sub-module classes
from . import EFIVarBase


class EFIVarInt(EFIVarBase):
    """
    EFIVarInt class

    Base class to process an EFI Variable that contains a single integer

    Should be inherited for individual variable names
    """
    def __init__(self, efivar_name: str | None = None, efivar_fullpath: pathlib.Path | None = None) -> None:
        """
        Read an EFI Variable represented as a single integer from the EFI file and store in __value

        .. warning::
           ONLY one of global_namespace or efivar_fullpath must be provided

        :param efivar_name: EFI variable name to read
        :param efivar_fullpath: Fully qualified path of the EFI Variable file
        """
        super().__init__(efivar_name, efivar_fullpath)

        self.__value = int.from_bytes(self._raw_data, 'little')
        self._log.info(f'Read integer value: {self.__value}')

    @property
    def value(self) -> int:
        """:return: Return integer value of the read EFI Variable"""
        return self.__value

    @property
    def hex_value(self) -> str:
        """:return: Hexadecimal representation of the read EFI Variable"""
        return f'{self.__value:04x}'
