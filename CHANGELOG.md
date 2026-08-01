# Roadmap

 - Update `BootEntry` to support read/write/delete/create functionality
 - Update `BootManager` to support `BootEntry` changes
 - Update `pyefibootmgr` to support `BootEntry` changes

# 0.0.4 (2026-xx-xx) - unreleased

## New Features
 - Update `BootManager` to support most of the functionality of the `efibootmgr` command
   - Create/Delete/Edit of `BootEntry` not implemented  
 - Add `pyefibootmgr` script to installation to bring almost feature parity with `efibootmgr`
   - All command line parameters addressing local file Boot Entries have been implemented
   - Create/Delete/Edit of Boot Entries served by placeholder functions

## Code Changes
 - Change of string representation of `BootEntry`
 - Refactor `BootManager` to come closer to likely final implementation

# 0.0.3 (2026-07-31)

## New Features
 - API Documentation on GitHub Wiki for all publicly facing Classes **EXCEPT** `BootManager`
 - All basic read/write EFI Variables (`BootTimeout`, `BootNext`, and `BootOrder`) now have update ability to allow write-back
 - `BootEntry` class interface mostly stabilised with access to all internal variables

## Bug Fixes
 - Fix decoding of Optional Data within `BootEntry`

## Code Changes
 - `BootEntry` moved from top-level class to `pyefiboot.bootentry` sub-module. Sub-module `filepath` moved to sub-module of `pyefiboot.bootentry`
 - Re-factoring of class structure for Integer and Integer List EFI Variables for better code sharing and scalability
 
# 0.0.2 (2026-07-22)

## New Features
 - Read/Write implementation of `BootTimeout`, `BootCurrent`, `BootNext` and `BootOrder`
 - Addition of new File Path Node types
 - Addition of internal `efibootmgr` wrapper to manage updating UEFI variables
 - Documentation cleanup

## Bug Fixes
 - Support buffering bytes at end of File Path Node
 - Clean up of Extra Data decoding
 - Allow for EFI Variable classes to be created with a value of `None` if variable does not exist

## Code Changes
 - Restructure File Path Node parsing to use base classes and sub-classing to simplify parsing each Node and to simplify
   adding new sub-types in the future
 - All File Path Nodes now decoded using `struct` in the Base class
 - Create `EFIVarBase`, `EFIVarInt` and `EFIVarIntList` as base classes for simple EFI Variable parsing
 
## Known Issues
 - `BootEntry` is still read-only and public interface not yet finalised
 - `BootManager` is still read-only and public interface not yet finalised

# 0.0.1 (2026-07-14)

## Original Release

### Features
 - Simple replacement of `efibootmgr` and `efibootmgr -v` via execution of `python -m pyefiboot`
 - Class based infrastructure to read EFI variables into structure
 - Internal Class Logging implemented