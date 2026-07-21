"""
This file implements the BootOrder class within the pyefiboot library

BootOrder provides access to the current value of the BootOrder EFI Variable
"""
# Import efivar modules and classes
import pyefiboot.efibootmgr as efibootmgr
from pyefiboot.efivar import EFIVarIntList


class BootOrder(EFIVarIntList):
    """
    BootOrder class - Stores the EFI Boot Order Variable
    """
    def __init__(self) -> None:
        """
        Inherit from the base class to read the Next variable
        """
        super().__init__(efivar_name='BootOrder')

    def __str__(self) -> str:
        """:return: Default string representation of the Boot Order"""
        return f'BootOrder: {self.hex_value}'

    @EFIVarIntList.value.setter
    def value(self, new_value: list[int] | list[str] | None) -> None:
        """
        Update the EFI BootOrder variable to the provided value (None will delete the BootOrder variable)

        :param new_value: Boot entry in range 0x0000-0xffff OR None. If a valid value is provided, BootOrder is updated. If None is provided, BootOrder is cleared
        """
        if new_value is None:
            self._log.debug(f'Deleting the BootOrder variable')
            efibootmgr.delete_boot_order()
        else:
            self._log.debug(f'Set BootOrder variable to {new_value}')
            efibootmgr.set_boot_order(new_value)

        self.__value = [int(value, base=16) for value in new_value] if isinstance(new_value[0], str) else new_value
