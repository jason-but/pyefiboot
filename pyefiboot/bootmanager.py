import logging
from pyefiboot import Configuration, BootCurrent, BootNext, BootTimeout, BootOrder, BootEntry


class BootManager:
    def __init__(self):
        self.__log = logging.getLogger(self.__class__.__name__)

        self.boot_current: BootCurrent | None = None
        self.boot_next: BootNext | None = None
        self.boot_timeout: BootTimeout | None = None
        self.boot_order: BootOrder | None = None
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
        self.boot_current = self._create_class_or_none(BootCurrent)
        self.boot_next = self._create_class_or_none(BootNext, log_warning=False)
        self.boot_timeout = self._create_class_or_none(BootTimeout)
        self.boot_order = self._create_class_or_none(BootOrder)

        for boot_entry_file in sorted(Configuration().efivarfs_path.glob('Boot[!N]???-*')):
            entry = BootEntry(efivar_fullpath=boot_entry_file)
            self.boot_entries[entry.entry_num] = entry
            if entry.kernel_file:
                self.kernel_entries[entry.kernel_file] = entry

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
