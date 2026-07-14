"""
This file implements the BootCurrent class within the pyefiboot library

BootCurrent provides access to the current value of the BootCurrent EFI Variable
"""
# Import efivar modules and classes
from pyefiboot.efivar import EFIVarInt


class BootCurrent(EFIVarInt):
    """
    BootCurrent class - Stores the EFI Timeout Variable
    """
    def __init__(self) -> None:
        """
        Inherit from the base class to read the Current variable
        """
        super().__init__(efivar_name='BootCurrent')

    def __str__(self) -> str:
        """:return: Default string representation of the Boot Current"""
        return f'BootCurrent: {self.hex_value}'
