import pathlib
import logging
import struct
import rich
import rich.console
import rich.logging
import pyefiboot

console = rich.console.Console()
logging.basicConfig(format='%(name)s.%(funcName)s() - %(message)s',
                    handlers=[rich.logging.RichHandler(markup=True, console=console)],
                    level=logging.DEBUG
                    )


class BootManager:
    def __init__(self):
        self.__log = logging.getLogger(self.__class__.__name__)

        self.boot_current: pyefiboot.BootCurrent | None = None
        self.boot_next: pyefiboot.BootNext | None = None
        self.boot_timeout: pyefiboot.BootTimeout | None = None
        self.boot_order: pyefiboot.BootOrder | None = None
        self.boot_entries: dict[str, pyefiboot.BootEntry] = {}
        self.kernel_entries: dict[str, pyefiboot.BootEntry] = {}

    def _create_class_or_none(self, cls, *args, **kwargs):
        try:
            return cls(*args, **kwargs)
        except Exception as e:
            self.__log.warning(f'Exception raised while initializing BootManager: {e}')
            return None

    def update_from_efi(self):
        # Read basic EFI Boot variables
        self.boot_current = self._create_class_or_none(pyefiboot.BootCurrent)
        self.boot_next = self._create_class_or_none(pyefiboot.BootNext)
        self.boot_timeout = self._create_class_or_none(pyefiboot.BootTimeout)
        self.boot_order = self._create_class_or_none(pyefiboot.BootOrder)

        for boot_entry_file in sorted(pyefiboot.Configuration().efivarfs_path.glob('Boot[!N]???-*')):
            entry = pyefiboot.BootEntry(efivar_fullpath=boot_entry_file)
            self.boot_entries[entry.entry_num] = entry
            if entry.kernel_file:
                self.kernel_entries[entry.kernel_file] = entry

        # self.boot_entries = [pyefiboot.BootEntry(efivar_fullpath=filename) for filename in self.boot_files]

    def display(self, verbose: bool=False):
        if self.boot_current: print(self.boot_current)
        if self.boot_next: print(self.boot_next)
        if self.boot_timeout: print(self.boot_timeout)
        if self.boot_order: print(self.boot_order)

        for num, boot_entry in self.boot_entries.items():
            print(boot_entry.verbose_str() if verbose else boot_entry)

        for kernel, boot_entry in self.kernel_entries.items():
            print(f'Kernel{kernel}: {boot_entry}')


