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
        return '<No Value>' if self._value is None else f'{self._value:04x}'


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

    def _validate_new_value(self, new_value: int | str | None) -> int | None:
        """
        Private method called to validate the parameter provided to the value setter.

        This is intended to be overloaded when subclassed to provide a higher level of value validation specific to the individual EFI Variable

        Method will validate all allowed types provided to the getter, and return a clean version of new_value of either int or None type (str will be
        converted to int)

        Base class method will:
         - Validate provided None value, returning None
         - Validate provided integer value is in range 0x0000-0xffff, returning provided integer
         - Validate provided string value is a hexadecimal number that can be converted to an integer in the range 0x0000-0xffff, returning string converted to integer
         - Other values will raise an exception

        :param new_value: 16-bit Integer value in range 0x0000-0xffff (as string containing hex digits or as integer) OR None. If a valid value is provided, EFI variable is updated. If None is provided, EFI variable is deleted
        :return: Integer value of provided int|str parameter, or None
        :raise: ValueError if provided int or string value is not in range 0x0000-0xffff
        :raise: TypeError if provided value is not None, int, or string
        """
        match new_value:
            case None:
                # None is valid, return None
                return None
            case int():
                # 16-bit integer value is valid, return provided value
                if 0x0000 <= new_value <= 0xffff: return new_value
                # Raise exception for other integer values
                raise ValueError(f'Setting {self.efivar_name} EFI Variable to {new_value}. Integer must be in range [0x0000-0xffff]')
            case str():
                try:
                    # Try to convert the string to an integer using base 16, then validate it is a 16-bit integer and return
                    result = int(new_value, base=16)
                    if 0x0000 <= result <= 0xffff: return result
                    # String can be converted to an integer, but is outside the range. Raise ValueError, it will be caught by the except below and re-raise with a nice error message
                    raise ValueError()
                except ValueError:
                    # String unable to be converted to an integer OR can be converted but is not a valid 16-bit integer
                    raise ValueError(f'Setting {self.efivar_name} to "{new_value}". String is not a hex-number in range [0000-ffff]')
            case _:
                # Any other parameter type is a Type Error
                raise TypeError(f'Setting {self.efivar_name} - new value must be integer or string containing hexadecimal value in range 0x0000-0xffff')

    @EFIVarIntRO.value.setter
    def value(self, new_value: int | str | None) -> None:
        """
        Update the EFI variable to the provided value (None will delete the EFI variable)

        :param new_value: Boot entry in range 0x0000-0xffff (as string or integer) OR None. If a valid value is provided, EFI variable is updated. If None is provided, EFI variable is deleted
        """
        # Validate provided parameter
        new_value = self._validate_new_value(new_value)

        # new_value is valid and EFI variable can be updated
        match new_value:
            case None:
                # Provided new value is None. Delete EFI variable (may throw an exception)
                self._log.debug(f'Deleting the {self.efivar_name} variable')
                # self._delete()

            case int():
                # Provided new value is an integer, try to update EFI variable (may throw an exception)
                self._log.debug(f'Creating/updating {self.efivar_name} variable to {new_value}')
                # self._write(struct.pack(f'<H', new_value))

        # EFI Update successful, update internal variable
        self._value = new_value
        self._log.debug(f'{self.efivar_name}: Updated value to {self._value} ({self.hex_value})')
