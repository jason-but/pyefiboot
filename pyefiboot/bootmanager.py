import logging
from pyefiboot import Configuration, BootCurrent, BootNext, BootTimeout, BootOrder, BootEntry


class BootManager:
    def __init__(self):
        self.__log = logging.getLogger(self.__class__.__name__)

        self.__boot_current: BootCurrent = BootCurrent()
        self.__boot_next: BootNext = BootNext()
        self.__boot_timeout: BootTimeout = BootTimeout()
        self.__boot_order: BootOrder = BootOrder()
        self.__boot_entries: dict[str, BootEntry] = {}
        self.__kernel_entries: dict[int, BootEntry] = {}

        self._read_boot_entries()

    def _read_boot_entries(self):
        """(Re-)Create the BootEntry objects for all current Boot Entries and store copies in the __boot_entries and __kernel_entries dictionaries"""
        self.__boot_entries = {}
        self.__kernel_entries = {}

        # For each Boot Entry file in the efifs file system
        for boot_entry_file in sorted(Configuration().efivarfs_path.glob('Boot[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]-*')):
            # Create the BootEntry instance
            entry = BootEntry(efivar_fullpath=boot_entry_file)
            # Add entry to __boot_entries
            self.__boot_entries[entry.index] = entry
            if entry.kernel_file:
                # If BootEntry has a kernel file specified, add to __kernel_entries as well
                self.__kernel_entries[entry.kernel_file] = entry

    def refresh(self):
        """Update all EFI variables by re-reading from NVRAM"""
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

    def delete_entries_by_index(self, indexes: list[int]):
        print(f'Deleting the following boot entries: {indexes}')

    def display(self, verbose: bool = False):
        """
        Display all available Boot Entries on the system

        :param verbose: If True, display verbose messages
        """
        print(self.__boot_current)
        print(self.__boot_next)
        print(self.__boot_timeout)
        print(self.__boot_order)

        # Display all available boot entries
        for boot_entry in self.__boot_entries.values():
            print(boot_entry.verbose_str() if verbose else boot_entry)
