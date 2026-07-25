# pyefiboot

Python Library to manage EFI Boot Entries

The aim of this library is to provide an API to the functionality of the `efibootmgr` (https://github.com/rhinstaller/efibootmgr)
application. This provides a programmatic mechanism to read and update the EFI Boot Variables, allowing scripting of tasks to 
manage the EFI boot process.

[!NOTE]
The initial release is a straightforward read-only solution, effectively mimicking the features of `efibootmgr` and `efibootmgr -v` calls.

## Installation

When complete, should be:

```console
pip install pyefiboot
```

Seek information elsewhere about installing in a virtual environment

This library currently has no dependencies

## Usage

Most work can be done via the `BootManager` class which reads and provides access to all Boot related EFI variables

### Reading current Boot Entries

```python
import pyefiboot

bootmgr = pyefiboot.BootManager()

bootmgr.update_from_efi()
```

### Printing to screen

To get output similar to `efibootmgr`:

```python
bootmgr.display()
```

To get output similar to `efibootmgr -v`:

```python
bootmgr.display(verbose=True)
```

### Simple Program to Replicate `efibootmgr` and `efibootmgr -v`

```python
import argparse
import pathlib
import logging

from pyefiboot import Configuration, BootTimeout, BootCurrent, BootNext, BootOrder, BootEntry

def main() -> None:
    # Create argument parser and add -v parameter
    parser = argparse.ArgumentParser(description='pfEFIBoot', formatter_class=argparse.RawTextHelpFormatter, allow_abbrev=False)

    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')

    # Get user options
    arguments = parser.parse_args()

    # Load Simple EFI variables
    boot_timeout: BootTimeout = BootTimeout()
    boot_current: BootCurrent = BootCurrent()
    boot_next: BootNext  = BootNext()
    boot_order: BootOrder  = BootOrder()
    
    # Create dictionary mapping Boot Entry index to BootEntry instance
    boot_entries: dict[str, BootEntry] = {}
    for boot_entry_file in sorted(Configuration().efivarfs_path.glob('Boot[!N]???-*')):
        # For each filename that starts with Boot, followed by a character that is NOT 'N', then three more characters, followed by a '-'
        entry = BootEntry(efivar_fullpath=boot_entry_file)
        boot_entries[entry.entry_num] = entry

    # Display contents of EFI Boot variables to screen
    print(boot_current)
    print(boot_next)
    print(boot_timeout)
    print(boot_order)

    # Display each Boot Entry in turn, with more detail if run in verbose mode
    for num, boot_entry in boot_entries.items():
        print(boot_entry)
        if arguments.verbose:
            print(' - File Path:')
            for path in boot_entry.file_paths:
                print(f'    - {path}')
            print(f' - Optional Data: {boot_entry.optional_data}')


if __name__ == '__main__':
    main()
```

## Public Class APIs and Properties

The API documentation for each of the publicly exposed classes can be found on the project Wiki

 - [API: Configuration Class](https://github.com/jason-but/pyefiboot/wiki/API:-Configuration-Class) 
 - [API: BootTimeout Class](https://github.com/jason-but/pyefiboot/wiki/API:-BootTimeout-Class)
 - [API: BootCurrent Class](https://github.com/jason-but/pyefiboot/wiki/API:-BootCurrent-Class)
 - [API: BootNext Class](https://github.com/jason-but/pyefiboot/wiki/API:-BootNext-Class)
 - [API: BootOrder Class](https://github.com/jason-but/pyefiboot/wiki/API:-BootOrder-Class)
 - [API: BootEntry Class](https://github.com/jason-but/pyefiboot/wiki/API:-BootEntry-Class)

## Logging

All modules within `pyefiboot` support Python `logging`, enabling logging and an appropriate log level in your 
application will allow these logs to be captured
