"""
This file implements the BootNext class within the pyefiboot library

BootNext provides access to the current value of the BootNext EFI Variable
"""
# Import efivar sub-module classes
from pyefiboot.efivar import EFIVarIntRW


class BootNext(EFIVarIntRW):
    """
    BootNext class - Manages the EFI BootNext Variable
    """
    def __init__(self) -> None:
        """Inherit from the base class to read the BootNext variable"""
        super().__init__(efivar_name='BootNext')

    def __str__(self) -> str:
        """:return: Default string representation of the BootNext variable"""
        return f'BootNext: {self.hex_value}'

    def _validate_new_value(self, new_value: int | str | None) -> int | None:
        """
        Private method called to validate the parameter provided to the value setter.

        Method will validate all allowed types provided to the getter, and return a clean version of new_value of either int or None type (str will be
        converted to int)

        Base class method will validate that the provided value is a valid EFI Integer variable or None

        Following this, if the clean value is of type int, we need to also validate that the provided value refers to valid and current Boot Entry on the system

        :param new_value: 16-bit Integer value in range 0x0000-0xffff (as string containing hex digits or as integer) OR None
        :return: Integer value of provided int|str parameter, or None
        :raise: ValueError if provided int or string value is not in range 0x0000-0xffff OR is not a valid and current Boot Entry on the system
        :raise: TypeError if provided value is not None, int, or string
        """
        # Call base class method to validate provided value is a valid EFI Integer value. new_value is now int | None
        new_value = super()._validate_new_value(new_value)

        if isinstance(new_value, int) and new_value not in self._current_valid_indexes():
            # new_value is not a valid Boot Entry Index
            raise ValueError(f'Validating {self.efivar_name} EFI value ({new_value}): {new_value} is not a valid Boot Entry Index')

        return new_value
