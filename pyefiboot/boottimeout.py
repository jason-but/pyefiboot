"""
This file implements the BootTimeout class within the pyefiboot library

BootTimeout provides access to the current value of the BootTimeout EFI Variable
"""
# Import efivar modules and classes
import pyefiboot.efibootmgr as efibootmgr
from pyefiboot.efivar import EFIVarInt


class BootTimeout(EFIVarInt):
    """
    BootTimeout class - Stores the EFI Timeout Variable
    """
    def __init__(self) -> None:
        """
        Inherit from the base class to read the Timeout variable
        """
        super().__init__(efivar_name='Timeout')

    def __str__(self) -> str:
        """:return: Default string representation of the Boot Timeout"""
        return f'BootTimeout: {self.hex_value} seconds'

    @EFIVarInt.value.setter
    def value(self, new_value: int | None) -> None:
        """
        Update the EFI Timeout variable to the provided value (None will delete the Timeout variable)

        :param new_value: New timeout value in seconds. If None is provided, Timeout is cleared
        """
        if new_value is None:
            self._log.debug(f'Deleting the EFI Timeout variable')
            efibootmgr.delete_timeout()
        else:
            self._log.debug(f'Set EFI Timeout variable to {new_value}')
            efibootmgr.set_timeout(new_value)

        self.__value = new_value
