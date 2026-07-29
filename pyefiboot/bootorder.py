"""
This file implements the BootOrder class within the pyefiboot library

BootOrder provides access to the current value of the BootOrder EFI Variable
"""
# Import efivar modules and classes
import pyefiboot.efibootmgr as efibootmgr
from pyefiboot.efivar import EFIVarIntListRW


class BootOrder(EFIVarIntListRW):
    """
    BootOrder class - Stores the EFI Boot Order Variable
    """
    def __init__(self) -> None:
        """
        Inherit from the base class to read the BootOrder variable
        """
        super().__init__(efivar_name='BootOrder')

    def __str__(self) -> str:
        """:return: Default string representation of the Boot Order"""
        return f'BootOrder: {self.hex_value}'

    def _validate_new_value(self, new_value: list[int | str] | None) -> list[int] | None:
        """
        Private method called to validate the parameter provided to the value setter.

        Base class method will validate that the provided value is a valid EFI Integer List variable

        Following this, if the clean value is of type list[int], we need to also validate that all values in the list refer to valid and current Boot Entrys on the system

        Method will validate all allowed types provided to the getter, and return a clean version of new_value of either list[int] or None type (list[str] will
        be converted to list[int])

        :param new_value: 16-bit Integer value in range 0x0000-0xffff (as string containing hex digits or as integer) OR None. If a valid value is provided, EFI variable is updated. If None is provided, EFI variable is deleted
        :return: Integer value of provided int|str parameter, or None
        :raise: ValueError if provided int or string value is not a valid and current Boot Entry on the system
        """
        # Call base class method to validate provided value is a valid EFI Integer value. new_value is now int | None
        new_value = super()._validate_new_value(new_value)

        if isinstance(new_value, list):
            # new_value is pre-validated list of integers, more checks to be done
            if not set(new_value).issubset(self._current_valid_indexes()):
                # At least one index in new_value is not a valid Boot Entry Index
                raise ValueError(f'Setting {self.efivar_name} EFI Variable to {new_value}. At least one entry in {new_value} is not a valid Boot Entry Index')

            if len(new_value) != len(set(new_value)):
                # Duplicate values in list
                self._log.debug(f'Removing duplicate values from {new_value}')
                new_value[:] = dict.fromkeys(new_value).keys()

        return new_value

    def append(self, append_list: list[int | str]) -> None:
        """
        Append the provided Boot Entry indexes to the end of the existing Boot Order

        :param append_list: Boot entry in range 0x0000-0xffff (as string or integer). If a valid value is provided, it is appended to the end of the current list
        """
        # Validate provided parameter
        append_list = self._validate_new_value(append_list)

        self._log.debug(f'Appending {append_list} to the end of the existing Boot Order: {self.value}')
        EFIVarIntListRW.value.fset(self, self._value + append_list)

    def prepend(self, prepend_list: list[int | str]) -> None:
        """
        Prepend the provided Boot Entry indexes to the start of the existing Boot Order

        :param prepend_list: Boot entry in range 0x0000-0xffff (as string or integer). If a valid value is provided, it is prepended to the start of the current list
        """
        # Validate provided parameter
        prepend_list = self._validate_new_value(prepend_list)

        self._log.debug(f'Prepending {prepend_list} to the start of the existing Boot Order: {self.value}')
        EFIVarIntListRW.value.fset(self, prepend_list + self._value)

    def remove_non_existent(self) -> None:
        """Remove all Boot Entry indexes from the current Boot Order where the nominated Index is not a valid Boot Entry Index"""
        valid_indexes = self._current_valid_indexes()
        new_order = [index for index in self._value if index in valid_indexes]

        self._log.debug(f'Removing invalid Boot Entries from {self._value}. Clean order will be {new_order}')
        EFIVarIntListRW.value.fset(self, new_order)
