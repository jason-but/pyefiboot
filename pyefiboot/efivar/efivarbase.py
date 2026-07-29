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
        """
        if not isinstance(raw_data, bytes):
            raise TypeError('Raw EFI Variable Data must be a bytes sequence')

        try:
            self._log.debug(f'{self.__efivar_name}: Writing raw data sequence - {raw_data}')
            self.__efivar_fullpath.write_bytes(self.READWRITE_ATTR + raw_data)
            self._raw_data = raw_data
        except FileNotFoundError as e:
            print(f'ERROR: File not found: {e}')
        except PermissionError as e:
            print(f'ERROR: Permissions: {e}')

    @property
    def efivar_name(self) -> str:
        """:return: EFI variable name"""
        return self.__efivar_name

    @property
    def efivar_fullpath(self) -> pathlib.Path:
        """:return: Fully qualified path of the EFI Variable file"""
        return self.__efivar_fullpath

# int_list = [258, 1025, 65535]

# # Convert to 16-bit unsigned integers (Little-Endian)
# byte_sequence_le = struct.pack(f'<{len(int_list)}H', *int_list)
# print(byte_sequence_le)
#
#
#
#
# import os
# import struct
# import sys
#
# # EFI Variable Path and GUID for the global variable namespace
# EFIVARS_DIR = "/sys/firmware/efi/efivars"
# EFI_GLOBAL_VARIABLE_GUID = "8be4df61-93ca-11d2-aa0d-00e098032b8c"
# BOOT_NEXT_FILE = os.path.join(EFIVARS_DIR, f"BootNext-{EFI_GLOBAL_VARIABLE_GUID}")
# BOOT_ORDER_FILE = os.path.join(EFIVARS_DIR, f"BootOrder-{EFI_GLOBAL_VARIABLE_GUID}")
#
# # EFI Attribute bits (NV + BS + RT)
# EFI_VARIABLE_NON_VOLATILE = 0x00000001
# EFI_VARIABLE_BOOTSERVICE_ACCESS = 0x00000002
# EFI_VARIABLE_RUNTIME_ACCESS = 0x00000004
# STANDARD_ATTR = EFI_VARIABLE_NON_VOLATILE | EFI_VARIABLE_BOOTSERVICE_ACCESS | EFI_VARIABLE_RUNTIME_ACCESS
#
#
# def check_environment():
#     """Verify script running conditions."""
#     if not os.path.exists(EFIVARS_DIR):
#         print(f"Error: {EFIVARS_DIR} not found. Is EFI vars fs mounted?", file=sys.stderr)
#         sys.exit(1)
#     if os.getuid() != 0:
#         print("Error: This script must be run with root privileges (sudo).", file=sys.stderr)
#         sys.exit(1)
#
#
# def read_bootnext():
#     """Read and decode current BootNext variable."""
#     if not os.path.exists(BOOT_NEXT_FILE):
#         print("BootNext: Not set")
#         return
#
#     try:
#         with open(BOOT_NEXT_FILE, "rb") as f:
#             data = f.read()
#
#         if len(data) < 6:
#             print("Error: BootNext file contains invalid data size.")
#             return
#
#         attrs, boot_num = struct.unpack("<IH", data[:6])
#         print(f"BootNext: {boot_num:04X}")
#
#     except IOError as e:
#         print(f"Error reading BootNext: {e}", file=sys.stderr)
#
#
# def set_bootnext(hex_string):
#     """Create or overwrite BootNext variable."""
#     try:
#         boot_num = int(hex_string, 16)
#     except ValueError:
#         print(f"Error: '{hex_string}' is not a valid hexadecimal number.", file=sys.stderr)
#         sys.exit(1)
#
#     try:
#         payload = struct.pack("<IH", STANDARD_ATTR, boot_num)
#         with open(BOOT_NEXT_FILE, "wb") as f:
#             f.write(payload)
#         print(f"Successfully set BootNext to {boot_num:04X}")
#     except IOError as e:
#         print(f"Error writing BootNext: {e}", file=sys.stderr)
#
#
# def delete_bootnext():
#     """Delete the BootNext variable file."""
#     if not os.path.exists(BOOT_NEXT_FILE):
#         print("BootNext is already not set.")
#         return
#
#     try:
#         os.remove(BOOT_NEXT_FILE)
#         print("Successfully deleted BootNext variable.")
#     except IOError as e:
#         print(f"Error deleting BootNext: {e}", file=sys.stderr)
#
#
# def read_bootorder():
#     """Read and decode current BootOrder array."""
#     if not os.path.exists(BOOT_ORDER_FILE):
#         print("BootOrder: Not set")
#         return
#
#     try:
#         with open(BOOT_ORDER_FILE, "rb") as f:
#             data = f.read()
#
#         if len(data) < 4:
#             print("Error: BootOrder file contains invalid data size.")
#             return
#
#         # Header attributes
#         attrs = struct.unpack("<I", data[:4])[0]
#
#         # Array of 2-byte integers following the attributes
#         order_bytes = data[4:]
#         count = len(order_bytes) // 2
#
#         # Unpack multiple unsigned shorts
#         boot_order = struct.unpack(f"<{count}H", order_bytes)
#
#         order_strings = [f"{num:04X}" for num in boot_order]
#         print(f"BootOrder: {','.join(order_strings)}")
#
#     except IOError as e:
#         print(f"Error reading BootOrder: {e}", file=sys.stderr)
#
#
# def set_bootorder(hex_list_string):
#     """Overwrite BootOrder variable with a comma-separated list of entries."""
#     # Split list by comma (e.g. "0001,000A,0002")
#     hex_entries = [entry.strip() for entry in hex_list_string.split(",")]
#
#     boot_numbers = []
#     for hex_str in hex_entries:
#         try:
#             boot_numbers.append(int(hex_str, 16))
#         except ValueError:
#             print(f"Error: '{hex_str}' is not a valid hexadecimal number.", file=sys.stderr)
#             sys.exit(1)
#
#     try:
#         # Layout: 4 bytes attributes + dynamic count of 2-byte entries
#         count = len(boot_numbers)
#         payload = struct.pack(f"<I{count}H", STANDARD_ATTR, *boot_numbers)
#
#         with open(BOOT_ORDER_FILE, "wb") as f:
#             f.write(payload)
#
#         order_strings = [f"{num:04X}" for num in boot_numbers]
#         print(f"Successfully set BootOrder to {','.join(order_strings)}")
#
#     except IOError as e:
#         print(f"Error writing BootOrder: {e}", file=sys.stderr)
#
#
# if __name__ == "__main__":
#     check_environment()
#
#     if len(sys.argv) < 2:
#         print("Usage:")
#         print("  sudo python efi_raw.py status")
#         print("  sudo python efi_raw.py set-next <hex_num>       (e.g., 0001)")
#         print("  sudo python efi_raw.py del-next")
#         print("  sudo python efi_raw.py set-order <hex_list>     (e.g., 0001,000A,0002)")
#         sys.exit(1)
#
#     command = sys.argv.lower()
#
#     if command == "status":
#         read_bootnext()
#         read_bootorder()
#     elif command == "set-next":
#         if len(sys.argv) < 3:
#             print("Error: Missing hex boot target index number.")
#             sys.exit(1)
#         set_bootnext(sys.argv)
#     elif command == "del-next":
#         delete_bootnext()
#     elif command == "set-order":
#         if len(sys.argv) < 3:
#             print("Error: Missing comma-separated hex list.")
#             sys.exit(1)
#         set_bootorder(sys.argv)
#     else:
#         print(f"Unknown command: {command}")
#         sys.exit(1)


class EFIVarBaseOld:
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
