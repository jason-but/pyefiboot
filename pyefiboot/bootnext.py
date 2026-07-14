"""
This file implements the BootNext class within the pyefiboot library

BootNext provides access to the current value of the BootNext EFI Variable
"""
# Import efivar modules and classes
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
        return f'BootNext: {self.value}'
