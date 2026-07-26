"""
This file implements the EFIVarInt class within the pyefiboot library

EFIVarInt is an internal base class to read and parse and EFI Variable that contains a single integer
"""
# Import System Libraries
import pathlib
import struct

# Import efivar sub-module classes
from . import EFIVarBaseOld, EFIVarBase


class EFIVarIntRO(EFIVarBase):
    def __init__(self, efivar_name: str | None = None, efivar_fullpath: pathlib.Path | None = None) -> None:
        super().__init__(efivar_name, efivar_fullpath)
        self.__value: bytes | None = int.from_bytes(self._raw_data, byteorder="little") if self._raw_data else None
        self._log.info(f"EFI Variable {self.efivar_name} Int Initialized to {self.__value}")

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(variable={self.efivar_name}, path={self.efivar_fullpath}, value={self.__value}({self.hex_value}))'

    @property
    def value(self) -> int | None:
        """:return: Return integer value of the read EFI Variable"""
        return self.__value

    @property
    def hex_value(self) -> str:
        """:return: Hexadecimal representation of the read EFI Variable"""
        if self.__value is None:
            return '<No Value>'
        return f'{self.__value:04x}'


class EFIVarIntRW(EFIVarBase):
    def __init__(self, efivar_name: str | None = None, efivar_fullpath: pathlib.Path | None = None) -> None:
        super().__init__(efivar_name, efivar_fullpath)
        self.__value: bytes | None = int.from_bytes(self._raw_data, byteorder="little") if self._raw_data else None
        self._log.info(f"EFI Variable {self.efivar_name} Int Initialized to {self.__value}")

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(variable={self.efivar_name}, path={self.efivar_fullpath}, value={self.__value}({self.hex_value}))'

    @property
    def value(self) -> int | None:
        """:return: Return integer value of the read EFI Variable"""
        return self.__value

    @property
    def hex_value(self) -> str:
        """:return: Hexadecimal representation of the read EFI Variable"""
        if self.__value is None:
            return '<No Value>'
        return f'{self.__value:04x}'

    @value.setter
    def value(self, new_value: int | str | None) -> None:
        """
        Update the EFI BootNext variable to the provided value (None will delete the BootNext variable)

        :param new_value: Boot entry in range 0x0000-0xffff OR None. If a valid value is provided, BootNext is updated. If None is provided, BootNext is cleared
        """
        match new_value:
            case None:
                # Provided new value is none. Delete EFI variable
                self._log.debug(f'Deleting the {self.efivar_name} variable')
                self._delete()
                self.__value = None
                return
            case int():
                # Provided new value is an integer. Check range and raise exception if out of range
                if new_value < 0 or new_value > 0xffff:
                    raise ValueError(f'Setting {self.efivar_name} to {new_value}. Integer must be in range [0x0000-0xffff]')
            case str():
                # Provided new value is a string. Check string is a 4 character hex-number and raise exception if invalid
                if len(new_value) != 4 or not all(c in '0123456789abcdefABCDEF' for c in new_value):
                    raise ValueError(f'Setting {self.efivar_name} to {new_value}. String must be hex-number in range [0000-ffff]')
                # Convert string to integer
                new_value = int(new_value, base=16)
            case _:
                # Provided new value is invalid type, raise exception
                raise TypeError(f'Setting {self.efivar_name} - new value must be integer or string containing hexadecimal value in range 0x0000-0xffff')

        # Try to update EFI variable (may throw an exception)
        self._write(struct.pack(f'<H', new_value))

        # EFI Update successful, update internal variable
        self.__value = new_value
        self._log.debug(f'{self.efivar_name}: Updated value to {self.__value} ({self.hex_value})')


class EFIVarIntOld(EFIVarBaseOld):
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

        self.__value = int.from_bytes(self._raw_data, 'little') if self._raw_data else None
        self._log.info(f'Read integer value: {self.__value}')

    @property
    def value(self) -> int | None:
        """:return: Return integer value of the read EFI Variable"""
        return self.__value

    @property
    def hex_value(self) -> str:
        """:return: Hexadecimal representation of the read EFI Variable"""
        if self.__value is None:
            return '<No Value>'
        return f'{self.__value:04x}'
