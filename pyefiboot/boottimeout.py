"""
This file implements the BootTimeout class within the pyefiboot library

BootTimeout provides access to the current value of the BootTimeout EFI Variable
"""
# Import efivar modules and classes
from pyefiboot.efivar import EFIVarIntRW


class BootTimeout(EFIVarIntRW):
    """
    BootTimeout class - Manages the EFI Timeout Variable
    """
    def __init__(self) -> None:
        """Inherit from the base class to read the Timeout variable"""
        super().__init__(efivar_name='Timeout')

    def __str__(self) -> str:
        """:return: Default string representation of the Boot Timeout variable"""
        return f'BootTimeout: {self.value} seconds' if self.value is not None else f'Boot Timeout: {self.hex_value}'
