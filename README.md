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

### Reading the `BootCurrent`, `BootNext`, `BootTimeout` and `BootOrder` EFI Variables

```python
import pyefiboot

cur = pyefiboot.BootCurrent()

# Integer value of the current EFI Boot Entry
x: int = cur.value

# String representation of the current EFI Boot Entry, four character hex number
y: str = cur.hex_value

# BootNext and BootTimeout have similar functionality to BootCurrent

ord = pyefiboot.BootOrder()

# List of integers mapping the current programmed order of EFI Boot Entries
x: list[int] = ord.value

# String representation of the current EFI Boot Entry order, displayed as comma separated string of four character hex numbers
y: str = ord.hex_value
```
Creation of any of the above four classes will raise an exception if the nominated EFI variable does not exist

### Reading an EFI Boot Entry variable

```python
import pathlib
import pyefiboot

entry1 = pyefiboot.BootEntry(efivar_name='Boot0001')
entry2 = pyefiboot.BootEntry(efivar_fullpath=pathlib.Path('/sys/firmware/efi/efivars/Boot0002-8be4df61-93ca-11d2-aa0d-00e098032b8c'))

# Print string representation of boot entry to screen
print(entry1)

# Print verbose string representation of boot entry to screen
print(entry1.verbose_str())

# String representation of Boot Entry Index, four character hex number
x: str = entry2.entry_num

# If the Boot Entry refers to an actual local kernel to boot, returns the string representing the kernel file name, otherwise None
y: str | None = entry2.kernel_file
```

Access to other variables within the `BootEntry` will be in future versions

## Public Class Properties and APIs

### `BootTimeout`

Upon creation will read the current value of the UEFI Timeout variable. If the variable does not exist, it will be stored as `None`

#### Properties

| Property Name | Type            | Action  | Description                                                                                                       |
|:--------------|:----------------|:--------|:------------------------------------------------------------------------------------------------------------------|
| `value`       | `int` or `None` | Read    | <ul><li>Return timeout in seconds as an integer</li><li>Return `None` if variable does not exist</li></ul>        |
| `value`       | `int` or `None` | Write   | <ul><li>Set the timeout to the provided value</li><li>Delete the UEFI Timeout variable if set to `None`</li></ul> |
| `hex_value`   | `string`        | Read    | Return the current UEFI Timeout variable as a four-digit hex string                                               |
| `__str__`     | &mdash;         | &mdash; | Class can be converted to string representation in format "BootTimeout: x seconds"                                |   

### `BootCurrent`

Upon creation will read the current value of the UEFI BootCurrent variable

#### Properties

| Property Name | Type            | Action    | Description                                                                   |
|:--------------|:----------------|:----------|:------------------------------------------------------------------------------|
| `value`       | `int`           | Read Only | Return the current UEFI BootCurrent variable as an integer                    |
| `hex_value`   | `string`        | Read      | Return the current UEFI BootCurrent variable as a four-digit hex string       |
| `__str__`     | &mdash;         | &mdash;   | Class can be converted to string representation in format "BootCurrent: xxxx" |   

### `BootNext`

Upon creation will read the current value of the UEFI BootNext variable. If the variable does not exist, it will be stored as `None`

#### Properties

| Property Name | Type            | Action  | Description                                                                                                                          |
|:--------------|:----------------|:--------|:-------------------------------------------------------------------------------------------------------------------------------------|
| `value`       | `int` or `None` | Read    | <ul><li>Return the Boot Entry index to be used on next boot as an integer</li><li>Return `None` if variable does not exist</li></ul> |
| `value`       | `int` or `None` | Write   | <ul><li>Set the BootNext variable to the provided value</li><li>Delete the UEFI BootNext variable if set to `None`</li></ul>         |
| `hex_value`   | `string`        | Read    | Return the current UEFI BootNext variable as a four-digit hex string                                                                 |
| `__str__`     | &mdash;         | &mdash; | Class can be converted to string representation in format "BootNext: xxxx" or "BootNext <No Value>"                                  |   

### `BootOrder`

Upon creation will read the current value of the UEFI BootOrder variable. If the variable does not exist, it will be stored as `None`

#### Properties

| Property Name | Type                                 | Action  | Description                                                                                                                                      |
|:--------------|:-------------------------------------|:--------|:-------------------------------------------------------------------------------------------------------------------------------------------------|
| `value`       | `list[int]` or `None`                | Read    | <ul><li>Return list of Boot Entry indexes as integers</li><li>Return `None` if variable does not exist</li></ul>                                 |
| `value`       | `list[int]` or 'list[str]' or `None` | Write   | <ul><li>Set the Boot Order to the provided list of integers OR hex strings</li><li>Delete the UEFI BootOrder variable if set to `None`</li></ul> |
| `hex_value`   | `string`                             | Read    | Return the current UEFI BootOrder as a comma separated list of hex boot entry values                                                             |
| `__str__`     | &mdash;                              | &mdash; | Class can be converted to string representation in format "BootOrder: xxxx,yyyy,zzzz"                                                   |   

## Logging

All modules within `pyefiboot` support Python `logging`, enabling logging and an appropriate log level in your 
application will allow these logs to be captured
