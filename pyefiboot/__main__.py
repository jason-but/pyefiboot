"""
This file is executed when the swinburne_smartrack is executed as 'python -m pyefiboot'

Provides an example of functionality of the pyefiboot library
"""
# Import System Libraries
import argparse
import pathlib
import logging

# Import pyefiboot modules
from pyefiboot import Configuration, BootManager


def parse_arguments() -> argparse.Namespace:
    """
    Parses and returns the command-line arguments for the pyefiboot module.

    :returns: argparse.Namespace: A Namespace object containing the parsed command-line arguments.

    :raises: This function will raise errors related to incorrect command-line argument parsing using argparse.ArgumentParser.
    """
    class ValidPath:
        """ArgParse Validator to validate if a given directory path exists."""

        def __call__(self, path) -> pathlib.Path:
            """
            :param path: Command line argument specifying a directory path.
            :return: Parameter path if validation is successful.
            :raises: Exception argparse.ArgumentTypeError if validation fails.
            """
            print(f'CHECKING DIRECTORY: {path}')
            print(f'CHECKING DIRECTORY TYPE: {type(path)}')
            if pathlib.Path(path).is_dir(): return pathlib.Path(path)
            raise argparse.ArgumentTypeError(f'Nominated directory "{path}" does not exist.')

    class SetLogLevel(argparse.Action):
        """
        Process the specified log-level parameter and set the default system log level as an action

        NOTE: This class is designed to be used for validating a formatted parameter in the context of command-line argument parsing.
        Should be used with an argument type of "choices" to ensure no incorrect values are applied
        """
        def __call__(self, parser, namespace, values, option_string=None):
            """
            Parse command line option as DEBUG, INFO, WARNING, ERROR, or CRITICAL, then set the logging log-level to match

            :param parser: ArgParse instance, used to send errors back to the parser.
            :param namespace: Current parsed parameters.
            :param values: Current option being parsed.
            :param option_string: Actual option (e.g. --urgency)
            """
            logging.basicConfig(level=values)

            # Save the value to the namespace for standard argparse behavior
            setattr(namespace, self.dest, values)

    # Create the main parser with global CLI parameters
    parser = argparse.ArgumentParser(description='pfEFIBoot',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     allow_abbrev=False
                                     )
    parser.add_argument('-p', '--efifs-path', type=ValidPath(), help=f'Specify EFI Var File System Path (default: {Configuration().efivarfs_path})')
    parser.add_argument('-g', '--global-guid', type=str, help=f'Specify Global EFI GUID (default: {Configuration().efi_global_guid})')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-l', '--log-level', action=SetLogLevel, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the logging level')

    return parser.parse_args()


if __name__ == '__main__':
    try:
        # Parse all command line arguments, if the '-c' argument exists, load the Configuration file now, otherwise it will be loaded by the submodules using default properties
        arguments = parse_arguments()

        if arguments.efifs_path: Configuration.efivarfs_path = arguments.efifs_path
        if arguments.global_guid: Configuration.efi_global_guid = arguments.global_guid

        # Create the boot manager instance and read from current variables
        boot_mgr = BootManager()
        boot_mgr.update_from_efi()

        # Display contents of EFI Boot variables to screen
        boot_mgr.display(arguments.verbose)

    except KeyboardInterrupt as err:
        pass
    except Exception as err:
        print(err)
