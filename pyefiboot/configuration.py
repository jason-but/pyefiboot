"""
This module implements the Configuration class which is used to manage Default paths and names
"""

# Import System Libraries
import logging
import pathlib


# Initialised default locations put here to make easier to find when updating system defaults
EFIVARFS_PATH = '/sys/firmware/efi/efivars/'
EFI_GLOBAL_GUID = '8be4df61-93ca-11d2-aa0d-00e098032b8c'


class Configuration:
    """
    Manages the application configuration using a singleton pattern.

    This class ensures that only one instance of the configuration is created and shared across the application. It dynamically loads configuration
    from a TOML file, either specified by the user or found in predefined default paths. The configuration file must include required sections like
    'smartrack_servers' and 'manage'. Additionally, the class integrates logging configuration if the debug section is present in the file.

    :ivar _instance: Singleton instance of the class; ensures one instance across the application.
    :ivar _initialized: Indicates if the configuration has already been initialized to prevent reinitialization.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """
        Implements a singleton pattern to ensure only one instance of the class is created, shared across any number of instantiations. Each call to
        this class returns the same instance, maintaining the state across calls.

        :param cls: The class being instantiated.
        :param args: Positional arguments that are passed during instantiation.
        :param kwargs: Keyword arguments that are passed during instantiation.

        :returns: A single instance of the class.
        """
        if not cls._instance: cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes the configuration of the library, setting the default efivarfs path and EFI Global GUID

        The constructor checks if a configuration has already been instantiated (via the `_initialized` flag) to prevent reinitialization. Otherwise
        it creates and initialises the two internal variables.
        """
        # If a configuration has already been loaded, just return
        if self._initialized: return
        self._initialized = True

        self.__log = logging.getLogger(self.__class__.__name__)

        # Initialise variables
        self.__efivarfs_path: pathlib.Path = pathlib.Path(EFIVARFS_PATH)
        self.__log.debug(f'Initialise "efivarfs": {self.__efivarfs_path}')
        self.__efi_global_guid: str = EFI_GLOBAL_GUID
        self.__log.debug(f'Initialise "efi_global_guid": {self.__efi_global_guid}')

    @property
    def efivarfs_path(self) -> pathlib.Path:
        """
        :return: The configured path to the efivarfs as a pathlib.Path object
        """
        return self.__efivarfs_path

    @efivarfs_path.setter
    def efivarfs_path(self, value: pathlib.Path) -> None:
        """
        Update the EFI efivarfs path to the provided pathlib.Path value

        :param value: New EFI efivarfs path
        :raises TypeError: If `value` is not a pathlib Path object
        """
        if not isinstance(value, pathlib.PurePath): raise TypeError('efivarfs_path must be a pathlib.Path')

        self.__log.debug(f'Update "efivarfs": {self.__efivarfs_path}')
        self.__efivarfs_path = value

    @property
    def efi_global_guid(self) -> str:
        """
        :return: The configured EFI Global GUID as a string
        """
        return self.__efi_global_guid

    @efi_global_guid.setter
    def efi_global_guid(self, value: str) -> None:
        """
        Update the EFI Global GUID to the provided string value

        :param value: New EFI Global GUID
        :raises TypeError: If `value` is not a string
        """
        if not isinstance(value, str): raise TypeError("efi_global_guid must be a string")

        self.__log.debug(f'Update "efi_global_guid": {self.__efi_global_guid}')
        self.__efi_global_guid = value
