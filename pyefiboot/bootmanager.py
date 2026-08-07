"""
This file implements the BootManager class within the pyefiboot library

BootManager provides a global view to the EFI Boot System providing managed support of boot entries
"""
# Import System Libraries
import logging
from collections import defaultdict

# Import efivar classes
from pyefiboot import Configuration, BootCurrent, BootNext, BootTimeout, BootOrder, BootEntry


class BootManager:
    """
    BootManager class - Provided high level general management of the EFI Boot System

    This is the preferred approach to EFI Boot Variable management. Should you require lower level access, you may use the lower level classes

    Should only need to create one instance through which general system management can be performed
    """
    def __init__(self):
        """
        Class Constructor

        Create all the internal variables to store the separate EFI Variable being managed

        As there are multiple BootEntry instances, they are stored in dictionaries allowing you to search for a Boot Entry based on either it Boot Entry
        index, or on the kernel file name being loaded
        """
        self.__log = logging.getLogger(self.__class__.__name__)

        self.__boot_current: BootCurrent = BootCurrent()
        self.__boot_next: BootNext = BootNext()
        self.__boot_timeout: BootTimeout = BootTimeout()
        self.__boot_order: BootOrder = BootOrder()
        self.__boot_entries: dict[int, BootEntry] = {}
        self.__kernel_entries: defaultdict[str, list[BootEntry]] = defaultdict(list)

        self._read_boot_entries()

    def _read_boot_entries(self):
        """(Re-)Create the BootEntry objects for all current Boot Entries and store copies in the __boot_entries and __kernel_entries dictionaries"""
        self.__log.info("Loading all EFI Boot Entries")
        self.__boot_entries = {}
        self.__kernel_entries = defaultdict(list)

        # For each Boot Entry file in the efifs file system
        for boot_entry_file in sorted(Configuration().efivarfs_path.glob('Boot[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]-*')):
            self.__log.debug(f'Creating entry from: {boot_entry_file}')
            # Create the BootEntry instance
            entry = BootEntry(efivar_fullpath=boot_entry_file)
            # Add entry to __boot_entries
            self.__boot_entries[entry.index] = entry
            if entry.kernel_file:
                self.__log.debug(f'Registering Boot entry with  kernel file: {entry.kernel_file}')
                # If BootEntry has a kernel file specified, add to __kernel_entries as well
                self.__kernel_entries[entry.kernel_file].append(entry)

    def _delete_from_kernel_entry(self, entry: BootEntry):
        """
        Private method to delete the nominated BootEntry instance from the dictionary mapping kernel file names to BootEntry instances

        :param entry: BootEntry instance to be deleted from the internal __kernel_entries dictionary
        """
        # If this BootEntry does not map to a kernel file, just return
        if not entry.kernel_file: return

        self.__log.debug(f'Delete Boot Entry Boot{entry.hex_index} from entries associated with "{entry.kernel_file}"')
        # Dictionary maps kernel file name to a list of BootEntries. Remove from list
        self.__kernel_entries[entry.kernel_file] = [x for x in self.__kernel_entries[entry.kernel_file] if x != entry]
        # If this is an empty list, remove kernel file from dictionary
        if not self.__kernel_entries[entry.kernel_file]: del self.__kernel_entries[entry.kernel_file]

    def refresh(self):
        """Update all EFI variables by re-reading from NVRAM"""
        self.__log.info("Refreshing all EFI Variables")
        self.__boot_current.refresh()
        self.__boot_next.refresh()
        self.__boot_timeout.refresh()
        self.__boot_order.refresh()

        self._read_boot_entries()

    @property
    def boottimeout(self) -> BootTimeout:
        """:return: Return internal BootTimeout variable"""
        return self.__boot_timeout

    @property
    def bootnext(self) -> BootNext:
        """:return: Return internal BootNext variable"""
        return self.__boot_next

    @property
    def bootcurrent(self) -> BootCurrent:
        """:return: Return internal BootCurrent variable"""
        return self.__boot_current

    @property
    def bootorder(self) -> BootOrder:
        """:return: Return internal BootOrder variable"""
        return self.__boot_order

    @property
    def boot_entries(self) -> dict[int, BootEntry]:
        """:return: Return internal variable storing dictionary of BootEntry instances"""
        return self.__boot_entries

    def delete_entries_by_index(self, indexes: list[int]):
        """
        Remove the BootEntry instances associated with the provided indexes

        Entries are removed from both:
         - __boot_entries: dictionary mapping BootEntry index to BootEntry instance
         - __kernel_entries: dictionary mapping kernel name to a list of BootEntry instances using that kernel

        :param indexes: List of integers representing the BootEntry indexes to delete
        :raises ValueError: If indexes is a list of integers but not all integers are in the allowed range, OR if one of the indexes does not refer to an existing Boot Entry index
        :raises TypeError: If indexes is not a list of integers
        """
        match indexes:
            case []:
                # Empty list, return as empty list
                raise TypeError(f'Must be list of integers containing hexadecimal value in range 0x0000-0xffff')
            case list() if all(isinstance(x, int) and not isinstance(x, bool) and (0x0000 <= x <= 0xffff) for x in indexes):
                # List of 16-bit integers, OK
                pass
            case list() if all(isinstance(x, int) and not isinstance(x, bool) for x in indexes):
                # List of integers, but at least one is outside the valid range
                raise ValueError(f'Must be list of integers in range [0000-0xffff]')
            case _:
                # Any other parameter type is a Type Error
                raise TypeError(f'Must be list of integer or strings containing hexadecimal value in range 0x0000-0xffff')

        for index in indexes:
            try:
                print(f'Deleting boot entry {index}')
                # Try to extract the boot entry with index, exception will be raised if it does not exist
                bootentry = self.__boot_entries[index]
                bootentry.delete()
                self._delete_from_kernel_entry(bootentry)
            except KeyError as e:
                raise ValueError(f'Deleting Boot Entry Boot{e.args[0]:04X}: Boot Entry does not exist') from None

    def delete_entries_by_kernel_file(self, kernel_files: list[str]) -> None:
        """
        Remove the BootEntry instances associated with the provided list of kernel file names

        Entries are removed from both:
         - __boot_entries: dictionary mapping BootEntry index to BootEntry instance
         - __kernel_entries: dictionary mapping kernel name to a list of BootEntry instances using that kernel

        :param kernel_files: List of strings containing kernel files to select which Boot Entries to delete
        :raises ValueError: If one of the kernel files does not map to any BootEntry instances
        :raises TypeError: If kernel_files is not a list of strings
        """
        match kernel_files:
            case []:
                # Empty list, invalid
                raise TypeError(f'Must be list of strings representing kernel file names')
            case list() if all(isinstance(x, str) for x in kernel_files):
                # List of strings, OK
                pass
            case _:
                # Any other parameter type is a Type Error
                raise TypeError(f'Must be list of strings representing kernel file names')

        for kernel_file in kernel_files:
            try:
                print(f'Deleting all boot entries associated with {kernel_file}')
                for bootentry in self.__kernel_entries[kernel_file]:
                    bootentry.delete()
                    del self.__boot_entries[bootentry.index]
                del self.__kernel_entries[kernel_file]

            except KeyError as e:
                raise ValueError(f'Deleting Boot Entries with kernel {e.args[0]}: No entries associated with this kernel') from None

    def display(self, verbose: bool = False):
        """
        Display all available Boot EFI variables and Entries on the system

        :param verbose: If True, display verbose messages
        """
        print(self.__boot_current)
        print(self.__boot_next)
        print(self.__boot_timeout)
        print(self.__boot_order)

        # Display all available boot entries
        for boot_entry in self.__boot_entries.values():
            print(boot_entry.verbose_str() if verbose else boot_entry)

        print(self.__kernel_entries)
