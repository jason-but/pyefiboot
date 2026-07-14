"""
This file implements the BootTimeout class within the pyefiboot library

BootTimeout provides access to the current value of the BootTimeout EFI Variable
"""
# Import efivar modules and classes
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
