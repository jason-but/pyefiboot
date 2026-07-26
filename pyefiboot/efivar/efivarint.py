"""
This file implements the EFIVarInt class within the pyefiboot library

EFIVarInt is an internal base class to read and parse and EFI Variable that contains a single integer
"""
# Import System Libraries
import pathlib
import struct

# Import efivar sub-module classes
from . import EFIVarBase


class EFIVarIntRO(EFIVarBase):
    def __init__(self, efivar_name: str | None = None, efivar_fullpath: pathlib.Path | None = None) -> None:
        """
        Initialise a read-only integer EFI Variable based on either the variable name OR the full path to the file containing the variable:
         - Call the base class constructor to load the variable data in self._raw_data as a bytes sequence
         - Convert self._raw_data to an integer to store in _value

        **WARNING: ONLY one of efivar_name or efivar_fullpath must be provided**

        :param efivar_name: EFI variable name to read
        :param efivar_fullpath: Fully qualified path of the EFI Variable file
        """
        super().__init__(efivar_name, efivar_fullpath)
        self._value: int | None = int.from_bytes(self._raw_data, byteorder="little") if self._raw_data else None
        self._log.info(f'Integer variable initialised to {self._value}')

    def __repr__(self) -> str:
        """:return: Verbose string representation of class for debugging purposes"""
        return f'{self.__class__.__name__}(variable={self.efivar_name}, path={self.efivar_fullpath}, value={self._value}({self.hex_value}))'

    @property
    def value(self) -> int | None:
        """:return: Return integer value of the read EFI Variable"""
        return self._value

    @property
    def hex_value(self) -> str:
        """:return: Hexadecimal representation of the read EFI Variable"""
        if self._value is None:
            return '<No Value>'
        return f'{self._value:04x}'


class EFIVarIntRW(EFIVarIntRO):
    def __init__(self, efivar_name: str | None = None, efivar_fullpath: pathlib.Path | None = None) -> None:
        """
        Initialise a read/write integer EFI Variable based on either the variable name OR the full path to the file containing the variable:
         - Call the base class constructor to load the variable data in self._raw_data as a bytes sequence and self._value as an integer value

        **WARNING: ONLY one of efivar_name or efivar_fullpath must be provided**

        :param efivar_name: EFI variable name to read
        :param efivar_fullpath: Fully qualified path of the EFI Variable file
        """
        super().__init__(efivar_name, efivar_fullpath)

    @EFIVarIntRO.value.setter
    def value(self, new_value: int | str | None) -> None:
        """
        Update the EFI variable to the provided value (None will delete the EFI variable)

        :param new_value: Boot entry in range 0x0000-0xffff (as string or integer) OR None. If a valid value is provided, EFI variable is updated. If None is provided, EFI variable is deleted
        """
        match new_value:
            case None:
                # Provided new value is none. Delete EFI variable
                self._log.debug(f'Deleting the {self.efivar_name} variable')
                self._delete()
                self._value = None
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
        self._value = new_value
        self._log.debug(f'{self.efivar_name}: Updated value to {self._value} ({self.hex_value})')
