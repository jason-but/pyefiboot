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