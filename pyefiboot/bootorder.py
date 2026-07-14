"""
This file implements the BootOrder class within the pyefiboot library

BootOrder provides access to the current value of the BootOrder EFI Variable
"""
# Import efivar modules and classes
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
