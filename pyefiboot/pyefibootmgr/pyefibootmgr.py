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
        self.__quiet = args.quiet
        self.__verbose = False if self.__quiet else args.verbose
        self.__log.debug(f'Registered actions: {self.__actions}')
        self.__log.debug(f'Registered params: {self.__params}')

        self.__boot_mgr = BootManager()

    @register_action('active')
    def _active(self) -> None:
        """Make the nominated boot number (in params['bootnum']) active"""
        print(f'PLACEHOLDER: Make boot entry {self.__params['bootnum']:04x} active')

        if self.__verbose: print(f'Make boot entry {self.__params['bootnum']:04X} active')

        self.__log.debug(f'Make boot entry {self.__params['bootnum']:04X} active is currently a placeholder function')

    @register_action('inactive')
    def _inactive(self) -> None:
        """Make the nominated boot number (in params['bootnum']) inactive"""
        print(f'PLACEHOLDER: Make boot entry {self.__params['bootnum']:04x} inactive')

        if self.__verbose: print(f'Make boot entry {self.__params['bootnum']:04x} inactive')

        self.__log.debug(f'Make boot entry {self.__params['bootnum']:04x} inactive is currently a placeholder function')

    @register_action('delete_bootnum')
    def _delete_bootnum(self) -> None:
        """
        Delete the Boot Entry stored at the nominated boot number (in params['bootnum'])

        :param bootnum: Integer representing the index of the boot Entry to delete
        """
        print(f'PLACEHOLDER: Delete Boot Entry {self.__params['bootnum']:04x}')

        if self.__verbose: print(f'Delete Boot Entry {self.__params['bootnum']:04x}')

        self.__log.debug(f'Delete Boot Entry {self.__params['bootnum']:04x} is currently a placeholder function')

    @register_action('create')
    def _create(self) -> None:
        """Create a new boot entry using information from self.__params"""
        print(f'PLACEHOLDER: Create new Boot Entry at index {self.__params['index']:04X} with (disk: {self.__params['disk']}, part: {self.__params['part']}, loader: {self.__params['loader']}, label: {self.__params['label']}) - update boot order')

        if self.__verbose: print(f'Creating a new Boot Entry')

    @register_action('create_only')
    def _create_only(self) -> None:
        """Create a new boot entry using information from self.__params"""
        print(f'PLACEHOLDER: Create new Boot Entry at index {self.__params['index']:04X} with (disk: {self.__params['disk']}, part: {self.__params['part']}, loader: {self.__params['loader']}, label: {self.__params['label']}) - do NOT update boot order')

        if self.__verbose: print(f'Creating a new Boot Entry')

    @register_action('remove_dups')
    def _remove_duplicate_entries_in_bootorder(self) -> None:
        """Create a new boot entry with the provided parameters"""
        if self.__verbose: print(f'Removing duplicate Boot Entries from the BootOrder variable')
        try: self.__boot_mgr.bootorder.remove_duplicate_entries()
        except PermissionError as e:
            raise Exception(f'Could not set BootOrder: {e.strerror}')
        except (ValueError, TypeError) as e:
            raise Exception(f'Invalid BootOrder order entry: {e}')

    @register_action('bootnext')
    def _set_bootnext(self) -> None:
        """Set the Boot Entry stored at the nominated boot number (in params['bootnext']) to be booted on next startup"""
        if self.__verbose: print(f'Setting BootNext variable to {self.__params['bootnext']:04X}')
        try: self.__boot_mgr.bootnext.value = self.__params['bootnext']
        except PermissionError as e:
            raise Exception(f'Could not set BootNext: {e.strerror}')
        except (ValueError, TypeError) as e:
            raise Exception(f'Invalid BootEntry: {e}')

    @register_action('delete_bootnext')
    def _delete_bootnext(self) -> None:
        """Delete the BootNext variable"""
        if self.__verbose: print(f'Deleting the BootNext variable')
        try: self.__boot_mgr.bootnext.value = None
        except PermissionError as e: raise Exception(f'Could not set BootNext: {e.strerror}')

    @register_action('bootorder')
    def _set_bootorder(self) -> None:
        """Set the BootOrder to be the list of nominated boot entries (in params['bootorder'])"""
        if self.__verbose: print(f'Setting BootOrder variable to: {','.join(f'i:04X' for i in self.__params['bootorder'])}')
        try: self.__boot_mgr.bootorder.value = self.__params['bootorder']
        except PermissionError as e:
            raise Exception(f'Could not set BootOrder: {e.strerror}')
        except (ValueError, TypeError) as e:
            raise Exception(f'Invalid BootOrder order entry ({','.join(f'{i:04X}' for i in self.__params['bootorder'])}): {e}')

    @register_action('delete_bootorder')
    def _delete_bootorder(self) -> None:
        """Delete the BootOrder variable"""
        if self.__verbose: print(f'Deleting the BootOrder variable')
        try: self.__boot_mgr.bootorder.value = None
        except PermissionError as e: raise Exception(f'Could not remove entry from BootOrder: {e.strerror}')

    @register_action('timeout')
    def _set_timeout(self) -> None:
        """Set the Boot Timeout to the nominated (in params['timeout']) number of seconds with a max value of 60"""
        if self.__verbose: print(f'Setting Timeout variable to {self.__params['timeout']}')
        try: self.__boot_mgr.boottimeout.value = min(self.__params['timeout'], 60)
        except (PermissionError, ValueError) as e: raise Exception(f'Could not set Timeout: {e.strerror if isinstance(e, PermissionError) else e}')

    @register_action('delete_timeout')
    def _delete_timeout(self) -> None:
        """Delete the Timeout variable"""
        if self.__verbose: print(f'Deleting the Timeout variable')
        try: self.__boot_mgr.boottimeout.value = None
        except PermissionError as e: raise Exception(f'Could not delete Timeout: {e.strerror}')

    @register_action('No action')
    def _display_boot_settings(self) -> None:
        """Print current EFI Boot Configuration to screen"""
        if self.__quiet: return
        if self.__verbose: print(f'Displaying Current Boot Settings')
        self.__boot_mgr.display(self.__verbose)

    def execute(self) -> None:
        """Execute all registered actions"""
        for action in self.__actions:
            self.__log.debug(f'Executing {action} action')
            try: self.ACTION_MAP[action](self)
            except KeyError as e: print(f'Requested action "{e}" is currently not implemented')



def pyefibootmgr():
    parser = EfibootmgrArgumentParser()

    args = parser.parse_args()

    logging.basicConfig(format='%(name)s.%(funcName)s() - %(message)s', force=True)

    # Create the boot manager instance and read from current variables
    try:
        boot_mgr = PyEFIBootMgr(args)
        boot_mgr.execute()
    except Exception as e:
        print(f'ERROR: {e}')

