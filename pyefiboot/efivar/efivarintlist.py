"""
This file implements the EFIVarIntList class within the pyefiboot library

EFIVarIntList is an internal base class to read and parse and EFI Variable that contains an array of integers
"""
# Import System Libraries
import array
import struct
import pathlib

# Import efivar sub-module classes
from . import EFIVarBase


class EFIVarIntListRO(EFIVarBase):
    def __init__(self, efivar_name: str | None = None, efivar_fullpath: pathlib.Path | None = None) -> None:
        """
        Initialise a read-only integer list EFI Variable based on either the variable name OR the full path to the file containing the variable:
         - Call the base class constructor to load the variable data in self._raw_data as a bytes sequence
         - Convert self._raw_data to a list[int] to store in _value

        **WARNING: ONLY one of efivar_name or efivar_fullpath must be provided**

        :param efivar_name: EFI variable name to read
        :param efivar_fullpath: Fully qualified path of the EFI Variable file
        """
        super().__init__(efivar_name, efivar_fullpath)
        self._value: list[int] | None = array.array('H', self._raw_data).tolist()
        self._log.info(f'Integer list variable initialise to: {self._value}')

    def __repr__(self) -> str:
        """:return: Verbose string representation of class for debugging purposes"""
        return f'{self.__class__.__name__}(variable={self.efivar_name}, path={self.efivar_fullpath}, value={self._value}({self.hex_value}))'

    def refresh(self) -> None:
        """Re-read the current EFI variable from NVRAM (base class function) and reset internal state by decoding stored value"""
        super().refresh()
        self._value = array.array('H', self._raw_data).tolist()
        self._log.info(f'Integer list variable re-set to: {self._value}')

    @property
    def value(self) -> list[int] | None:
        """:return: Return list of integer values of the read EFI Variable"""
        return self._value

    @property
    def hex_value(self) -> str:
        """:return: Hexadecimal list representation of the read EFI Variable"""
        return '<No Value>' if self._value is None else ','.join(f'{value:04x}' for value in self._value)


class EFIVarIntListRW(EFIVarIntListRO):
    def __init__(self, efivar_name: str | None = None, efivar_fullpath: pathlib.Path | None = None) -> None:
        """
        Initialise a read/write integer list EFI Variable based on either the variable name OR the full path to the file containing the variable:
         - Call the base class constructor to load the variable data in self._raw_data as a bytes sequence and self._value as a list[int] value (or None)

        **WARNING: ONLY one of efivar_name or efivar_fullpath must be provided**

        :param efivar_name: EFI variable name to read
        :param efivar_fullpath: Fully qualified path of the EFI Variable file
        """
        super().__init__(efivar_name, efivar_fullpath)

    def _convert_param_to_list_int(self, param: list[int | str]) -> list[int]:
        """
        Private method to convert a list of integers or strings to a list of integers (sanitise input parameters)

        Otherwise, raise an exception with an appropriate error message

        :param param: List of 16-bit Integer values in range 0x0000-0xffff (as string containing hex digits or as integer) OR None.
        :return: If param is a list of 16-bit integers, return param as list[int].
                 If param is a list of strings where each string can be converted to a list of 16-bit integers, return list where each string is converted to an integer.
        :raise: ValueError if provided list[int] does not contain all 16-bit integers or list[str] does not contain hex-strings that can be converted to 16-bit integers
        :raise: TypeError if provided value is not of type list[int] or list[str] or is an empty list
        """
        match param:
            case []:
                # Empty list, return as empty list
                raise TypeError(f'Must be list of integer or strings containing hexadecimal value in range 0x0000-0xffff')
            case list() if all(isinstance(x, int) and not isinstance(x, bool) and (0x0000 <= x <= 0xffff) for x in param):
                # new_value is a list of 16-bit integers, OK
                return param
            case list() if all(isinstance(x, int) and not isinstance(x, bool) for x in param):
                # new_value is a list of integers, but at least one is outside the valid range
                raise ValueError(f'Must be list of integers in range [0000-0xffff]')
            case list() if all(isinstance(x, str) for x in param):
                # new_value is a list of strings, try to conver to a list of integers
                try:
                    # Try to convert each string to an integer using base 16, then validate all are 16-bit integers and return new list
                    result = [int(x, base=16) for x in param]
                    if all(0x0000 <= x <= 0xffff for x in result): return result
                    # String can be converted to an integer, but is outside the range. Raise ValueError, it will be caught by the except below and re-raise with a nice error message
                    raise ValueError()
                except ValueError:
                    # String unable to be converted to an integer OR can be converted but is not a valid 16-bit integer
                    raise ValueError(f'Must be list of strings where each string is a hex-number in range [0000-ffff]')
            case _:
                # Any other parameter type is a Type Error
                raise TypeError(f'New value must be list of integer or strings containing hexadecimal value in range 0x0000-0xffff')

    def _validate_new_value(self, new_value: list[int | str] | None) -> list[int] | None:
        """
        Private method called to validate the parameter provided to the value setter.

        This is intended to be overloaded when subclassed to provide a higher level of value validation specific to the individual EFI Variable

        Method will validate all allowed types provided to the getter, and return a clean version of new_value of either list[int] or None type (list[str] will
        be converted to list[int])

        Base class method will:
         - Validate provided None or empty list value, returning None
         - Validate provided list[int] value is a list of all integers, with all integers in range 0x0000-0xffff, returning provided list[int]
         - Validate provided list[str] value is a list of all strings, all strings are valid hexadecimal numbers that can be converted to an integer in the range
           0x0000-0xffff, returning list[int] where all hexadecimal strings having been converted
         - Other values will raise an exception

        :param new_value: List of 16-bit Integer values in range 0x0000-0xffff (as string containing hex digits or as integer) OR None.
        :return: list[int] value of provided list[int | str] parameter, or None
        :raise: ValueError if all provided int or string values is not in range 0x0000-0xffff
        :raise: TypeError if provided value is not None, list[int], or list[str]
        """
        # An empty list is equivalent to None and signifies deleting the variable
        if new_value is None or new_value == []: return None

        try:
            # Not None, try to convert to list[int] and return, otherwise catch exception and provide more detailed error message
            return self._convert_param_to_list_int(new_value)
        except ValueError as e:
            raise ValueError(f'Validating {self.efivar_name} EFI value ({new_value}): {e}') from None
        except TypeError as e:
            raise TypeError(f'Validating {self.efivar_name} EFI value ({new_value}): {e}') from None

    @EFIVarIntListRO.value.setter
    def value(self, new_value: list[int | str] | None) -> None:
        """
        Update the EFI variable to the provided value (None will delete the EFI variable)

        :param new_value: List of 16-bit Integer values in range 0x0000-0xffff (as string containing hex digits or as integer) OR None.
        """
        # Validate provided parameter
        new_value = self._validate_new_value(new_value)

        # new_value is valid and EFI variable can be updated
        match new_value:
            case None:
                # Provided new value is None. Delete EFI variable (may throw an exception)
                self._log.debug(f'Deleting the {self.efivar_name} variable')
                self._delete()

            case list():
                # Provided new value is an integer, try to update EFI variable (may throw an exception)
                self._log.debug(f'Creating/updating {self.efivar_name} variable to {new_value}')
                self._write(struct.pack(f'<{len(new_value)}H', *new_value))

        # EFI Update successful, update internal variable
        self._value = new_value
        self._log.debug(f'{self.efivar_name}: Updated value to {self._value} ({self.hex_value})')
