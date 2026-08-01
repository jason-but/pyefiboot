import logging
from collections import defaultdict
from pyefiboot import Configuration, BootCurrent, BootNext, BootTimeout, BootOrder, BootEntry


class BootManager:
    def __init__(self):
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
        self.__boot_entries = {}
        self.__kernel_entries = defaultdict(list)

        # For each Boot Entry file in the efifs file system
        for boot_entry_file in sorted(Configuration().efivarfs_path.glob('Boot[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]-*')):
            # Create the BootEntry instance
            entry = BootEntry(efivar_fullpath=boot_entry_file)
            # Add entry to __boot_entries
            self.__boot_entries[entry.index] = entry
            if entry.kernel_file:
                # If BootEntry has a kernel file specified, add to __kernel_entries as well
                self.__kernel_entries[entry.kernel_file].append(entry)

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

    @property
    def boot_entries(self) -> dict[int, BootEntry]:
        """:return: Return internal variable storing dictionary of BootEntry instances"""
        return self.__boot_entries

    def _delete_from_kernel_entry(self, kernel_file: str, entry: BootEntry):
        self.__log.debug(f'Delete Boot Entry Boot{entry.hex_index} from entries associated with "{kernel_file}"')
        self.__kernel_entries[kernel_file] = [x for x in self.__kernel_entries[kernel_file] if x != entry]
        if not self.__kernel_entries[kernel_file]: del self.__kernel_entries[kernel_file]

    def delete_entries_by_index(self, indexes: list[int]):
        for index in indexes:
            try:
                print(f'Deleting boot entry {index}')
                # Try to extract the boot entry with index, exception will be raised if it does not exist
                bootentry = self.__boot_entries[index]
                print(f'Need to delete boot entry: Boot{bootentry.hex_index}')
                if bootentry.kernel_file:
                    self._delete_from_kernel_entry(bootentry.kernel_file, bootentry)
            except KeyError as e:
                raise ValueError(f'Deleting Boot Entry Boot{e.args[0]:04X}: Boot Entry does not exist') from None

    def delete_entries_by_kernel_file(self, kernel_files: list[str]) -> None:
        for kernel_file in kernel_files:
            try:
                print(f'Deleting all boot entries associated with {kernel_file}')
                for bootentry in self.__kernel_entries[kernel_file]:
                    print(f'Need to delete boot entry: {bootentry.hex_index}')
                    del self.__boot_entries[bootentry.index]
                del self.__kernel_entries[kernel_file]

            except KeyError as e:
                raise ValueError(f'Deleting Boot Entries with kernel {e.args[0]}: No entries associated with this kernel') from None

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

        print(self.__kernel_entries)
