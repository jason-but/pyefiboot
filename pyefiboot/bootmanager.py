import logging
from pyefiboot import Configuration, BootCurrent, BootNext, BootTimeout, BootOrder, BootEntry


class BootManager:
    def __init__(self):
        self.__log = logging.getLogger(self.__class__.__name__)

        self.boot_current: BootCurrent = BootCurrent()
        self.boot_next: BootNext = BootNext()
        self.boot_timeout: BootTimeout = BootTimeout()
        self.boot_order: BootOrder = BootOrder()
        self.boot_entries: dict[str, BootEntry] = {}
        self.kernel_entries: dict[str, BootEntry] = {}

    def _create_class_or_none(self, cls, log_warning: bool = True, *args, **kwargs):
        try:
            return cls(*args, **kwargs)
        except Exception as e:
            if log_warning: self.__log.warning(f'Exception raised while initializing BootManager: {e}')
            return None

    def update_from_efi(self):
        # Read basic EFI Boot variables
        self.boot_current.refresh()
        self.boot_next.refresh()
        self.boot_timeout.refresh()
        self.boot_order.refresh()

        for boot_entry_file in sorted(Configuration().efivarfs_path.glob('Boot[!N]???-*')):
            entry = BootEntry(efivar_fullpath=boot_entry_file)
            self.boot_entries[entry.hex_index] = entry
            if entry.kernel_file:
                self.kernel_entries[entry.kernel_file] = entry

    def set_timeout(self, timeout: int):
        self.__log.debug(f'Setting BootTimeout to {timeout} seconds')
        # noinspection PyPropertyAccess
        self.boot_timeout.value = timeout

    def delete_timeout(self):
        self.__log.debug(f'Deleting BootTimeout')
        # noinspection PyPropertyAccess
        self.boot_timeout.value = None

    def set_bootnext(self, index: int):
        self.__log.debug(f'Setting BootNext to {index:04X}')
        # noinspection PyPropertyAccess
        self.boot_next.value = index

    def delete_bootnext(self):
        self.__log.debug(f'Deleting BootNext')
        # noinspection PyPropertyAccess
        self.boot_next.value = None

    def set_bootorder(self, indexes: list[int]):
        self.__log.debug(f'Setting BootOrder to {indexes}')
        # noinspection PyPropertyAccess
        self.boot_order.value = indexes

    def delete_bootorder(self):
        self.__log.debug(f'Deleting BootOrder')
        # noinspection PyPropertyAccess
        self.boot_order.value = None

    def bootorder_remove_duplicates(self):
        self.__log.debug(f'Removing BootOrder duplicates')
        self.boot_order.remove_duplicate_entries()

    def delete_entries_by_index(self, indexes: list[int]):
        print(f'Deleting the following boot entries: {indexes}')

    def display(self, verbose: bool = False):
        if self.boot_current: print(self.boot_current)
        if self.boot_next: print(self.boot_next)
        if self.boot_timeout: print(self.boot_timeout)
        if self.boot_order: print(self.boot_order)

        for num, boot_entry in self.boot_entries.items():
            print(boot_entry)
            if verbose:
                print(' - File Path:')
                for path in boot_entry.file_paths:
                    print(f'    - {path}')
                print(f' - Optional Data: {boot_entry.optional_data}')
