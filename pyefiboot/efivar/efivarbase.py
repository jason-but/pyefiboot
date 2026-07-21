"""
This file implements the EFIVarBase class within the pyefiboot library

EFIVarBase is an internal base class to manage construction and setting the fully qualified path of an EFI variable
"""
# Import System Libraries
import pathlib
import logging

from pyefiboot import Configuration


class EFIVarBase:
    """
    EFIVarInt class

    Base class to process an EFI Variable that contains a single integer

    Should be inherited for individual variable names
    """
    def __init__(self, efivar_name: str | None = None, efivar_fullpath: pathlib.Path | None = None) -> None:
        """
        Read an EFI Variable represented as a single integer from the EFI file and store in __value

        .. warning::
           ONLY one of global_namespace or efivar_fullpath must be provided

        :param efivar_name: EFI variable name to read
        :param efivar_fullpath: Fully qualified path of the EFI Variable file
        """
        self._log = logging.getLogger(self.__class__.__name__)

        if (efivar_name is None) == (efivar_fullpath is None):
            raise ValueError(f'{self.__class__.__bases__[0].__name__}: Must provide only one of \'efivar_name\' or \'efivar_fullpath\' to constructor')

        self._log.debug(f'Constructor called with (efivar_name={efivar_name}, efivar_fullpath={efivar_fullpath})')

        fullpath = pathlib.Path(Configuration().efivarfs_path, f'{efivar_name}-{Configuration().efi_global_guid}') if efivar_name else efivar_fullpath
        self._log.debug(f'Setting EFI variable path to "{fullpath}"')

        self.efivar_name = fullpath.name.split('-', 1)[0]

        self._log.info(f'EFI variable name: "{self.efivar_name}"')
        self._raw_data: bytes | None = None
        try:
            self._raw_data = fullpath.read_bytes()[4:]
        except FileNotFoundError:
            self._log.info(f'EFI variable "{self.efivar_name}" not found, value set to None')

        self._log.debug(f'Raw EFI Variable Data: {self._raw_data}')
