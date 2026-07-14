# pyefiboot

Python Library to ...

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

bootmgr.update()
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