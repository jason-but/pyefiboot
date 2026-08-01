import argparse
import logging

from pyefiboot.pyefibootmgr import EfibootmgrArgumentParser
from pyefiboot import BootManager


def register_action(name: str):
    """
    Decorator to register a method as an action that can be called

    :param name: The text name under which to register this method that can later be used to search for the callable
    """
    def decorator(method):
        """Add the tag (name) as a hidden parameter to the decorated method"""
        method._action_name = name
        return method
    return decorator


def action_map(cls):
    """
    Used in conjunction with @register_action, builds an internal class lookup table for all registered actions mapping the action name to the registered
    class method

    :param cls: The class to register the actions for
    """
    # Executed once when the class is defined
    # Create an empty action map
    cls.ACTION_MAP = {}

    for attr_name in dir(cls):
        # Search each attribute within the class
        attr = getattr(cls, attr_name)
        if hasattr(attr, '_action_name'):
            # If the attribute has been registered, add it to the lookup table
            cls.ACTION_MAP[attr._action_name] = attr

    return cls


@action_map
class PyEFIBootMgr():
    def __init__(self, args: argparse.Namespace):
        self.__log = logging.getLogger('pyefibootmgr')

        self.__actions = args.actions
        self.__params = args.params
        self.__log.debug(f'Registered actions: {self.__actions}')
        self.__log.debug(f'Registered params: {self.__params}')

        self.__boot_mgr = BootManager()

    @register_action('active')
    def _active(self, bootnum: int, verbose: bool) -> None:
        """
        Make the nominated boot number active

        :param bootnum: Integer representing the boot number to make active
        :param verbose: Should we print more information
        """
        print(f'PLACEHOLDER: Make boot entry {bootnum:04x} active')

        if verbose: print(f'Make boot entry {bootnum:04x} active')

        self.__log.debug(f'Make boot entry {bootnum:04x} active is currently a placeholder function')

    @register_action('inactive')
    def _inactive(self, bootnum: int, verbose: bool) -> None:
        """
        Make the nominated boot number inactive

        :param bootnum: Integer representing the boot number to make inactive
        :param verbose: Should we print more information
        """
        print(f'PLACEHOLDER: Make boot entry {bootnum:04x} inactive')

        if verbose: print(f'Make boot entry {bootnum:04x} inactive')

        self.__log.debug(f'Make boot entry {bootnum:04x} inactive is currently a placeholder function')

    @register_action('delete_bootnum')
    def _delete_bootnum(self, bootnum: int, verbose: bool) -> None:
        """
        Delete the Boot Entry stored at the nominated boot number

        :param bootnum: Integer representing the index of the boot Entry to delete
        :param verbose: Should we print more information
        """
        print(f'PLACEHOLDER: Delete Boot Entry {bootnum:04x}')

        if verbose: print(f'Delete Boot Entry {bootnum:04x}')

        self.__log.debug(f'Delete Boot Entry {bootnum:04x} is currently a placeholder function')

    @register_action('create')
    def _create(self, disk: str, part: str, loader: str, label: str, index: int, verbose: bool) -> None:
        """
        Create a new boot entry with the provided parameters

        :param disk:
        :param part:
        :param loader:
        :param label:
        :param index:
        :param verbose: Should we print more information
        """
        print(f'PLACEHOLDER: Create new Boot Entry at index {index:04x} with (disk: {disk}, part: {part}, loader: {loader}, label: {label}) - update boot order')

        if verbose: print(f'Creating a new Boot Entry')

    @register_action('create_only')
    def _create_only(self, disk: str, part: str, loader: str, label: str, index: int, verbose: bool) -> None:
        """
        Create a new boot entry with the provided parameters

        :param disk:
        :param part:
        :param loader:
        :param label:
        :param index:
        :param verbose: Should we print more information
        """
        print(f'PLACEHOLDER: Create new Boot Entry at index {index:04x} with (disk: {disk}, part: {part}, loader: {loader}, label: {label}) - do NOT update boot order')

        if verbose: print(f'Creating a new Boot Entry')

    @register_action('remove_dups')
    def _remove_duplicate_entries_in_bootorder(self, verbose: bool) -> None:
        """
        Create a new boot entry with the provided parameters

        :param verbose: Should we print more information
        """
        print(f'PLACEHOLDER: Remove duplicate Boot Entries from the BootOrder variable')

        if verbose: print(f'Removing duplicate Boot Entries from the BootOrder variable')

    @register_action('bootnext')
    def _set_bootnext(self, bootnext: int, verbose: bool) -> None:
        """
        Set the Boot Entry stored at the nominated boot number to be booted on next startup

        :param bootnext: Integer representing the index of the boot Entry to set as BootNext
        :param verbose: Should we print more information
        """
        print(f'PLACEHOLDER: Set BootNext EFI variable to be Boot Entry {bootnext:04x}')

        if verbose: print(f'Setting BootNext variable to {bootnext:04x}')

    @register_action('delete_bootnext')
    def _delete_bootnext(self, verbose: bool) -> None:
        """
        Delete the BootNext variable

        :param verbose: Should we print more information
        """
        print(f'PLACEHOLDER: Deleting the current BootNext variable')

        if verbose: print(f'Deleting the BootNext variable')

    @register_action('bootorder')
    def _set_bootorder(self, bootorder: list[int], verbose: bool) -> None:
        """
        Set the Boot Entry stored at the nominated boot number to be booted on next startup

        :param bootorder: List of integers the Boot Order indexes of existing Boot Entries to try on next startup
        :param verbose: Should we print more information
        """
        print(f'PLACEHOLDER: Set BootOrder EFI variable to be Boot Entries: {','.join(f'{i:04x}' for i in bootorder)} ({bootorder})')

        if verbose: print(f'Setting BootNext variable to {bootorder}')

    @register_action('delete_bootorder')
    def _delete_bootorder(self, verbose: bool) -> None:
        """
        Delete the BootOrder variable

        :param verbose: Should we print more information
        """
        print(f'PLACEHOLDER: Deleting the current BootOrder variable')

        if verbose: print(f'Deleting the BootOrder variable')

    @register_action('timeout')
    def _set_timeout(self, timeout: int, verbose: bool) -> None:
        """
        Set the Boot Timeout to the nominated of seconds

        :param timeout: Integer representing the number of seconds to set as the timeout value
        :param verbose: Should we print more information
        """
        print(f'PLACEHOLDER: Set Timeout EFI variable to {timeout} seconds')

        if verbose: print(f'Setting Timeout variable to {timeout}')

    @register_action('delete_timeout')
    def _delete_timeout(self, verbose: bool) -> None:
        """
        Delete the Timeout variable

        :param verbose: Should we print more information
        """
        print(f'PLACEHOLDER: Deleting the current Timeout variable')

        if verbose: print(f'Deleting the Timeout variable')

    @register_action('No action')
    def _display_boot_settings(self, verbose: bool, **kwargs) -> None:
        self.__boot_mgr.display(verbose)

    def execute(self) -> None:
        self.__boot_mgr.update_from_efi()

        for action in self.__actions:
            self.__log.debug(f'Executing {action} action')
            try:
                self.ACTION_MAP[action](self, **self.__params)
            except KeyError as e:
                print(f'Requested action "{e}" is currently not implemented')
            except Exception as e:
                print(f'Other error when executing "{action}" action: {e}')


def pyefibootmgr():
    parser = EfibootmgrArgumentParser()

    args = parser.parse_args()

    # Create the boot manager instance and read from current variables
    boot_mgr = PyEFIBootMgr(args)
    boot_mgr.execute()

#    boot_mgr.display(args.verbose)


if __name__ == "__main__":
    pyefibootmgr()
