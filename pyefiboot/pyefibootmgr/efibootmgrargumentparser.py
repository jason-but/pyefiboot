"""
This file implements the EfibootmgrArgumentParser class which creates the subclasses argparse.ArgumentParser to create the argument parser for the pyefibootmgr
application

EfibootmgrArgumentParser is an internal class used by the pyefibootmgr application

Currently Implemented CLI args
 -a | --active         Set bootnum active.
 -A | --inactive       Set bootnum inactive.
 -b | --bootnum XXXX   Modify BootXXXX (hex).
 -B | --delete-bootnum Delete bootnum.
 -c | --create         Create new variable bootnum and add to bootorder at index (-I).
 -C | --create-only    Create new variable bootnum and do not add to bootorder.
 -d | --disk disk      Disk containing boot loader (defaults to /dev/sda).
 -D | --remove-dups    Remove duplicate values from BootOrder.
 -I | --index number   When creating an entry, insert it in bootorder at specified position (default: 0).
 -l | --loader name     (Defaults to "\EFI\Gentoo\grub.efi").
 -L | --label label     Boot manager display label (defaults to "Linux").
 -n | --bootnext XXXX   Set BootNext to XXXX (hex).
 -N | --delete-bootnext Delete BootNext.
 -o | --bootorder XXXX,YYYY,ZZZZ,...     Explicitly set BootOrder (hex).
 -O | --delete-bootorder Delete BootOrder.
 -p | --part part        Partition containing loader (defaults to 1 on partitioned devices).
 -t | --timeout seconds  Set boot manager timeout waiting for user input.
 -T | --delete-timeout   Delete Timeout.
 -v | --verbose          Print additional information.

Not implemented but should be CLI args
 -g | --gpt            Force disk with invalid PMBR to be treated as GPT.
 -u | --unicode | --UCS-2  Handle extra args as UCS-2 (default is ASCII).

Not implemented but not sure if should be CLI args
 -e | --edd [1|3]      Force boot entries to be created using EDD 1.0 or 3.0 info.
 -E | --device num     EDD 1.0 device number (defaults to 0x80).
      --full-dev-path  Use a full device path.
      --file-dev-path  Use an abbreviated File() device path.
 -f | --reconnect      Re-connect devices after driver is loaded.
 -F | --no-reconnect   Do not re-connect devices after driver is loaded.
 -i | --iface name     Create a netboot entry for the named interface.
 -m | --mirror-below-4G t|f Mirror memory below 4GB.
 -M | --mirror-above-4G X Percentage memory to mirror above 4GB.
 -q | --quiet            Be quiet.
 -r | --driver           Operate on Driver variables, not Boot Variables.
 -w | --write-signature  Write unique sig to MBR if needed.
 -y | --sysprep          Operate on SysPrep variables, not Boot Variables.
 -@ | --append-binary-args file  Append extra args from file (use "-" for stdin).
 -V | --version          Return version and exit.
"""
# Import System Libraries
import logging
import argparse


class EfibootmgrArgumentParser(argparse.ArgumentParser):
    """
    Argument parser for the pyefibootmgr application - subclasses argparse.ArgumentParser

    Provides a sub-set of the efibootmgr command line interface for parsing and presenting to the pyefibootmgr application
    """
    @classmethod
    def hex_to_int(cls, bootnum: str) -> int:
        """
        Static method Convert bootnum as hexadecimal string to an integer and return

        :param bootnum: String in hexadecimal format
        :return: Integer value of bootnum if bootnum can be converted to an integer AND it falls in range [0000-ffff]
        :raise: argparse.ArgumentTypeError if bootnum is not a valid hexadecimal boot entry index
        """
        if isinstance(bootnum, str):
            try:
                # Try to convert the string to an integer using base 16, then validate it is a 16-bit integer and return
                result = int(bootnum, base=16)
                if 0x0000 <= result <= 0xffff: return result
            except ValueError:
                # String unable to be converted to an integer OR can be converted but is not a valid 16-bit integer
                pass

        # Parameter cannot be converted, raise relevant argparse.ArgumentTypeError exception
        raise argparse.ArgumentTypeError(f'Parameter "{bootnum}" must be a hex-number in range [0000-ffff]')

    class ValidBootNum:
        """Argparse validator to validate a four character boot number as a hexadecimal string"""
        def __call__(self, bootnum):
            """
            :param bootnum: Command line argument specifying a boot number as a hexadecimal string
            :return: Parameter bootnum as an integer if it is a valid hexadecimal string that can be converted to a 16-bit integer
            :raise: argparse.ArgumentTypeError if bootnum is not a valid hexadecimal string
            """
            return EfibootmgrArgumentParser.hex_to_int(bootnum)

    class ValidBootOrder:
        """Argparse validator to validate a comma separated list four (hexadecimal) character boot numbers as a string"""
        def __call__(self, bootorder) -> list[int]:
            """
            :param bootorder: Command line argument specifying a comma separated string of hexadecimal boot numbers
            :return: List of each bootnumber in bootorder as integers if it is a valid hexadecimal string that can be converted to a 16-bit integer
            :raise: argparse.ArgumentTypeError if bootorder is not a valid hexadecimal string
            """
            return [EfibootmgrArgumentParser.hex_to_int(bootnum) for bootnum in bootorder.split(',')]

    class StoreFlagAsAction(argparse.Action):
        """
        Process one or more command line flags (parameters with no value) and append them to a flat "actions" list

        NOTE: This class is designed to be used for actioning a formatted parameter in the context of command-line argument parsing. When executed due to
        specification on the command line, the parameter name is appended to the "actions" list as a string
        """
        def __init__(self, option_strings, dest, **kwargs):
            """Store parameter name so it can be added to list when specified"""
            self.clean_name = dest
            super().__init__(option_strings, dest=argparse.SUPPRESS, nargs=0, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            """
            Called when parameter/flag has been specified. If the "actions" name has not been created in the namespace, create it, then append the previously
            stored parameter name to the "actions" list

            :param parser: ArgParse instance, used to send errors back to the parser.
            :param namespace: Current parsed parameters.
            :param values: Current option being parsed.
            :param option_string: Actual option (e.g. --hint)
            """
            # If this is the first action being parsed, create the actions name in the namespace
            # if not hasattr(namespace, 'actions'):
            #     setattr(namespace, 'actions', [])

            # Append the selected option/action to the actions name in the namespace
            namespace.actions.append(self.clean_name)

    class StoreParamAsAction(argparse.Action):
        """
        Process one or more command line parameter (parameters with a value) and:
         1) append them to a flat "actions" list
         2) create the parameter within the parser namespace

        NOTE: This class is designed to be used for actioning a formatted parameter in the context of command-line argument parsing. When executed due to
        specification on the command line, the parameter name is appended to the "actions" list as a string and its value is stored to the parser namespace
        """
        def __call__(self, parser, namespace, values, option_string=None):
            """
            Parse command line option as KEY=LABEL or KEY:LABEL and extend the existing list with two new entries [KEY, LABEL]

            :param parser: ArgParse instance, used to send errors back to the parser.
            :param namespace: Current parsed parameters.
            :param values: Current option being parsed.
            :param option_string: Actual option (e.g. --hint)
            """
            # If this is the first action being parsed, create the actions name in the namespace
            # if not hasattr(namespace, 'actions'):
            #     setattr(namespace, 'actions', [])

            # Append the selected option/action to the actions name in the namespace
            namespace.actions.append(self.dest)

            # Store parameter value to the namespace
            setattr(namespace, self.dest, values)

    class SetLogLevel(argparse.Action):
        """
        Process the log-level parameter and set the default system log level as an action

        NOTE: This class is designed to be used for actioning a formatted parameter in the context of command-line argument parsing. When executed due to
        specification on the command line, the specified log-level is set for the application
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

    def __init__(self, *args, **kwargs):
        """
        Overloaded constructor

        Set the description and argparse parameters before calling the superclass constructor

        Then add arguments required to emulate efibootmgr
        """
        # Default options
        kwargs.setdefault('description', 'pyEFIbootmgr\n\nPython emulation of the "efibootmgr" tool')
        kwargs.setdefault('formatter_class', argparse.RawTextHelpFormatter)
        kwargs.setdefault('allow_abbrev', False)
        kwargs.setdefault('conflict_handler', 'resolve')

        # Initialise the parent class
        super().__init__(*args, **kwargs)

        self.__add_arguments()

    def __add_arguments(self):
        """ Add command line arguments to the argument parser """

        self.set_defaults(actions=[])

        # Selection of bootnum for specific arguments
        self.add_argument('-b', '--bootnum', type=EfibootmgrArgumentParser.ValidBootNum(), metavar='XXXX', help='Modify a specific boot entry (4-digit hex).')

        # Actions on specific bootnums (Requires -b)
        self.add_argument('-a', '--active', action=EfibootmgrArgumentParser.StoreFlagAsAction, help='Set selected bootnum (-b) active.')
        self.add_argument('-A', '--inactive', action=EfibootmgrArgumentParser.StoreFlagAsAction, help='Set selected bootnum (-b) inactive.')
        self.add_argument('-B', '--delete-bootnum', action=EfibootmgrArgumentParser.StoreFlagAsAction, help='Delete selected bootnum (-b) entry.')

        # Other Actions (not requiring -b)
        self.add_argument('-c', '--create', action=EfibootmgrArgumentParser.StoreFlagAsAction, help='Create new boot option and add to bootorder.')
        self.add_argument('-C', '--create-only', action=EfibootmgrArgumentParser.StoreFlagAsAction, help='Create new boot option without changing bootorder.')
        self.add_argument('-D', '--remove-dups', action=EfibootmgrArgumentParser.StoreFlagAsAction, help='Remove duplicate boot profiles.')
        self.add_argument('-n', '--bootnext', type=EfibootmgrArgumentParser.ValidBootNum(), action=EfibootmgrArgumentParser.StoreParamAsAction, metavar='XXXX', help='Set BootNext for the next boot cycle.')
        self.add_argument('-N', '--delete-bootnext', action=EfibootmgrArgumentParser.StoreFlagAsAction, help="Delete BootNext.")
        self.add_argument('-o', '--bootorder', type=EfibootmgrArgumentParser.ValidBootOrder(), action=EfibootmgrArgumentParser.StoreParamAsAction, metavar='XXXX,YYYY,...', help='Explicitly set BootOrder.')
        self.add_argument('-O', '--delete-bootorder', action=EfibootmgrArgumentParser.StoreFlagAsAction, help='Delete BootOrder completely.')
        self.add_argument('-t', '--timeout', type=int, action=EfibootmgrArgumentParser.StoreParamAsAction, metavar='N', help='Set boot manager timeout in seconds.')
        self.add_argument('-T', '--delete-timeout', action=EfibootmgrArgumentParser.StoreFlagAsAction, help='Delete boot manager timeout.')

        # Other Action parameters/options (often used with -c / -C)
        self.add_argument('-d', '--disk', default='/dev/sda', help='The disk containing the EFI System Partition (default: /dev/sda).')
        self.add_argument('-I', '--index', type=int, default=0, metavar='N', help='When creating an entry, insert it in bootorder at specified position (default: 0)')
        self.add_argument('-p', '--part', type=int, default=1, help='The partition number holding the EFI System Partition (default: 1).')
        self.add_argument('-l', '--loader', help='Path to the EFI loader executable (e.g., "\\EFI\\ubuntu\\grubx64.efi").')
        self.add_argument('-L', '--label', help='User-friendly text label for the new boot entry.')
        # self.add_argument("-u", "--unicode", action='store_true', help='Pass extra command line options as UC-2 encoded string.')

        # Global options
        self.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
        self.add_argument("--log-level", action=EfibootmgrArgumentParser.SetLogLevel, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level for the core application.")

    def parse_args(self, args=None, namespace=None):
        """
        Overload parse_args method. Performs further validation of the parsed command line arguments and creates the "params" name in the parsed namespace
          - Ensure that multiple actions are not specified
          - Ensure that required parameters (based on action) are specified and invalid parameters (based on action) are ignored
          - Create a copy of relevant parameters for the nominated action in the "params" name

        :return: Return the parsed arguments Namespace as required by parse_args()
        """
        def check_invalid_params(params: dict, required_params: list[str], invalid_params: list[str]) -> None:
            """
            Check that the provided parameters in the parsed namespace exist, and that the invalid parameters are missing or set to None

            Raise an argparse.error() if processing fails

            :param params: Dictionary containing parameter->value to check
            :param required_params: List of parameter names that must have a value in the namespace
            :param invalid_params: List of parameter names that must not have a value in the namespace
            """
            # Get list of missing parameters, if any exist, raise an error
            missing_params = [f'{p}' for p in required_params if p not in params]
            if missing_params: self.error(f'Selected action ({parsed.actions[0]}) requires the following missing parameter(s): {', '.join(missing_params)}')

            # Get list of invalid parameters, if any exist, raise an error
            invalid_params = [f'{k}={v}' for k, v in params.items() if k in invalid_params and v is not None]
            if invalid_params: self.error(f'Selected action ({parsed.actions[0]}) does not allow the following invalid parameter(s): {', '.join(invalid_params)}')

        # Call base class method to parse arguments and store in internal variable
        parsed = super().parse_args(args=args, namespace=namespace)

        # Extract selected action
        match len(parsed.actions):
            case 0 | 1:
                # Valid number of actions selected (0 or 1), append 'No action' to cause display of boot entries
                assert isinstance(parsed.actions, list)
                parsed.actions.append('No action')
            case _: self.error(f"The following options are mutually exclusive and cannot be run together: {', '.join(parsed.actions)}")

        # Extract other provided command line parameters
        params = {k: v for k, v in vars(parsed).items() if v is not None and k not in ['actions', 'log_level']}

        match parsed.actions[0]:
            case 'active' | 'inactive' | 'delete_bootnum':
                # Remove default params not needed by these actions
                params = {k: v for k, v in params.items() if k not in ['index', 'disk', 'part']}
                check_invalid_params(params=params, required_params=['bootnum'], invalid_params=['index', 'loader', 'label'])

            case 'create' | 'create_only':
                check_invalid_params(params=params, required_params=['loader', 'label'], invalid_params=['bootnum'])

            case _:
                # Remove default params not needed by remaining actions
                params = {k: v for k, v in params.items() if k not in ['index', 'disk', 'part']}
                check_invalid_params(params=params, required_params=[], invalid_params=['bootnum', 'loader', 'label'])

        parsed.params = params

        return parsed
