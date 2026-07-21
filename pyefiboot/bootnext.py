"""
This file implements the BootNext class within the pyefiboot library

BootNext provides access to the current value of the BootNext EFI Variable
"""
# Import efivar modules and classes
import pyefiboot.efibootmgr as efibootmgr
from pyefiboot.efivar import EFIVarInt


class BootNext(EFIVarInt):
    """
    BootNext class - Stores the EFI Timeout Variable
    """
    def __init__(self) -> None:
        """
        Inherit from the base class to read the Next variable
        """
        super().__init__(efivar_name='BootNext')

    def __str__(self) -> str:
        """:return: Default string representation of the Boot Next"""
        return f'BootNext: {self.hex_value}'

    @EFIVarInt.value.setter
    def value(self, new_value: int | str | None) -> None:
        """
        Update the EFI BootNext variable to the provided value (None will delete the BootNext variable)

        :param new_value: Boot entry in range 0x0000-0xffff OR None. If a valid value is provided, BootNext is updated. If None is provided, BootNext is cleared
        """
        if new_value is None:
            self._log.debug(f'Deleting the BootNext variable')
            efibootmgr.delete_boot_next()
        else:
            self._log.debug(f'Set BootNext variable to {new_value}')
            efibootmgr.set_boot_next(new_value)

        self.__value = int(new_value, base=16) if isinstance(new_value, str) else new_value
