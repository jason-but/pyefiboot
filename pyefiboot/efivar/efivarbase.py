"""
This file implements the EFIVarBase class within the pyefiboot library

EFIVarBase is an internal base class to manage construction and setting the fully qualified path of an EFI variable
"""
# Import System Libraries
import pathlib
import struct
import logging

from pyefiboot import Configuration


class EFIVarBase:
    """
    EFIVarBase class

    Base class to process an EFI Variable and provide possible read/write/delete support

    Should be inherited for individual variable names, not meant to be instatiated on its own
    """
    EFI_VARIABLE_NON_VOLATILE = 0x00000001
    """int: Static variable indicating flag for a non-volatile EFI variable (should be written firmware/NV-RAM)"""
    EFI_VARIABLE_BOOTSERVICE_ACCESS = 0x00000002
    """int: Static variable indicating flag for a boot service editable EFI variable (variable can be updated by the UEFI boot loader)"""
    EFI_VARIABLE_RUNTIME_ACCESS = 0x00000004
    """int: Static variable indicating flag for a runtime editable EFI variable (variable can be updated by the running OS)"""

    READONLY_ATTR = struct.pack('<I', EFI_VARIABLE_BOOTSERVICE_ACCESS | EFI_VARIABLE_RUNTIME_ACCESS)
    """int: Integer value representing EFI Variable Attribute for a Read-Only Variable"""

    READWRITE_ATTR = struct.pack('<I', EFI_VARIABLE_NON_VOLATILE | EFI_VARIABLE_BOOTSERVICE_ACCESS | EFI_VARIABLE_RUNTIME_ACCESS)
    """int: Integer value representing EFI Variable Attribute for a Read/Write Variable"""

    def __init__(self, efivar_name: str | None = None, efivar_fullpath: pathlib.Path | None = None) -> None:
        """
        Initialise the EFI Variable based on either the variable name OR the full path to the file containing the variable:
         - Store variable data in self._raw_data as a bytes sequence
         - Store EFI Variable name in self.__efi_var_name as a string
         - Store fully qualified path to EFI Variable in self.__efi_var_fullpath as a pathlib.Path

        **WARNING: ONLY one of efivar_name or efivar_fullpath must be provided**

        :param efivar_name: EFI variable name to read
        :param efivar_fullpath: Fully qualified path of the EFI Variable file
        """
        self._log = logging.getLogger(self.__class__.__name__)

        if (efivar_name is None) == (efivar_fullpath is None):
            raise ValueError(f'{self.__class__.__bases__[0].__name__}: Must provide only one of \'efivar_name\' or \'efivar_fullpath\' to constructor')

        self._log.debug(f'Constructor called with (efivar_name={efivar_name}, efivar_fullpath={efivar_fullpath})')

        # Store correct values for __efivar_name and __efivar_fullpath
        self.__efivar_name = efivar_name if efivar_name else efivar_fullpath.name.split('-', 1)[0]
        self.__efivar_fullpath = efivar_fullpath if efivar_fullpath else pathlib.Path(Configuration().efivarfs_path, f'{efivar_name}-{Configuration().efi_global_guid}')
        self._log.info(f'EFI variable name: {self.__efivar_name}')
        self._log.info(f'EFI variable path: {self.__efivar_fullpath}')

        # Initialise self._raw_data variable, then call _read() to read data into the internal variable
        self._raw_data: bytes | None = None
        self._read()

    def _current_valid_indexes(self) -> list[int]:
        """
        Get a list of all current Boot Entry Index numbers in the file system and return as a list of integers

        Can be used to validate if a provided Boot Entry number maps to a valid - existing - Boot Entry

        :return: List of integers mapping to all current EFI Boot Entry Index numbers
        """
        # glob() returns a list of all files matching "BootXXXX-*" where X is a hex digit
        # file_path.name returns just the file name, file_path.name[4:8] returns string hex index of the boot entry
        # int() converts string to integer to return list[int]
        return [int(file_path.name[4:8], base=16) for file_path in Configuration().efivarfs_path.glob('Boot[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]-*')]

    def _delete(self) -> None:
        """
        Delete the EFI Variable by deleting the file
         - **WARNING: Should ONLY be called if this is a read/write variable. Subclass needs to be aware and only call if allowed for this variable name**
         - Reset self._raw_data to None to signify that the variable is non-existent

        :raise: PermissionError if the file exists and the User does not have permission to delete the variable
        """
        if self.__efivar_fullpath.exists():
            self._log.debug(f'Deleting {self.__efivar_fullpath}')
            self.__efivar_fullpath.unlink()
            self._raw_data = None

    def _read(self) -> None:
        """
        Read (or re-read) the EFI Variable from file and store value in self._raw_data
         - Variable is stored AFTER the 4 byte attributes value. Read file as bytes and make a copy of all bytes from index 4
         - If the EFI Variable file does not exist, set self._raw_data to None to signify that the variable is non-existent
        """
        try:
            self._raw_data = self.__efivar_fullpath.read_bytes()[4:]
        except FileNotFoundError:
            self._log.info(f'EFI variable "{self.__efivar_name}" not found, value set to None')
            self._raw_data = None

        self._log.debug(f'Raw EFI Variable Data: {self._raw_data}')

    def _write(self, raw_data: bytes) -> None:
        """
        Write the provided bytes sequence as the data for the EFI Variable
         - **WARNING: Should ONLY be called if this is a read/write variable. Subclass needs to be aware and only call if allowed for this variable name**
         - Reset self._raw_data to the provided dataNone to signify that the variable is non-existent

        :param raw_data: bytes sequence to save as new value for the EFI Variable
        :raise: TypeError if raw_data is not of type bytes
        :raise: PermissionError if the User does not have permission to create/update the variable
        """
        if not isinstance(raw_data, bytes):
            raise TypeError('Raw EFI Variable Data must be a bytes sequence')

        self._log.debug(f'{self.__efivar_name}: Writing raw data sequence - {raw_data}')
        self.__efivar_fullpath.write_bytes(self.READWRITE_ATTR + raw_data)
        self._raw_data = raw_data

    def refresh(self) -> None:
        """Re-read the current EFI variable from NVRAM and reset internal state"""
        self._log.debug('Reloading EFI variable from NVRAM')
        self._read()

    @property
    def efivar_name(self) -> str:
        """:return: EFI variable name"""
        return self.__efivar_name

    @property
    def efivar_fullpath(self) -> pathlib.Path:
        """:return: Fully qualified path of the EFI Variable file"""
        return self.__efivar_fullpath
