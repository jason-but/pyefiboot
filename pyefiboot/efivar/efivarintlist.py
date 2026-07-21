"""
This file implements the EFIVarIntList class within the pyefiboot library

EFIVarIntList is an internal base class to read and parse and EFI Variable that contains an array of integers
"""
# Import System Libraries
import array
import pathlib

# Import efivar sub-module classes
from . import EFIVarBase


class EFIVarIntList(EFIVarBase):
    """
    EFIVarInt class

    Base class to process an EFI Variable that contains an array of integers

    Should be inherited for individual variable names
    """
    def __init__(self, efivar_name: str | None = None, efivar_fullpath: pathlib.Path | None = None) -> None:
        """
        Read an EFI Variable represented as a list of 16-bit integers from the EFI file and store in __value

        .. warning::
           ONLY one of efivar_name or efivar_fullpath must be provided

        :param efivar_name: EFI variable name to read
        :param efivar_fullpath: Fully qualified path of the EFI Variable file
        """
        super().__init__(efivar_name, efivar_fullpath)

        self.__value: list[int] = array.array('H', self._raw_data).tolist()
        self._log.info(f'Read integer list: {self.__value}')

    @property
    def value(self) -> list[int] | None:
        """:return: Return list of integer values of the read EFI Variable"""
        return self.__value

    @property
    def hex_value(self) -> str:
        """:return: Hexadecimal list representation of the read EFI Variable"""
        if self.__value is None:
            return '<No Value>'

        return ','.join(f'{value:04x}' for value in self.__value)
