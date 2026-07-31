import argparse
import logging


from pyefiboot import BootManager

class EfibootmgrArgumentParser(argparse.ArgumentParser):
    """Argument parser for the pyefibootmgr application - subclasses argparse.ArgumentParser"""
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
            if not hasattr(namespace, 'actions'):
                setattr(namespace, 'actions', [])

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
            if not hasattr(namespace, 'actions'):
                setattr(namespace, 'actions', [])

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
        self.add_argument('-f', '--forbid-reorder', action='store_true', help='Do not reorder BootOrder on entry creation.')
        self.add_argument('-n', '--bootnext', type=EfibootmgrArgumentParser.ValidBootNum(), action=EfibootmgrArgumentParser.StoreParamAsAction, metavar='XXXX', help='Set BootNext for the next boot cycle.')
        self.add_argument('-N', '--delete-bootnext', action=EfibootmgrArgumentParser.StoreFlagAsAction, help="Delete BootNext.")
        self.add_argument('-o', '--bootorder', type=EfibootmgrArgumentParser.ValidBootOrder(), action=EfibootmgrArgumentParser.StoreParamAsAction, metavar='XXXX,YYYY,...', help='Explicitly set BootOrder.')
        self.add_argument('-O', '--delete-bootorder', action=EfibootmgrArgumentParser.StoreFlagAsAction, help='Delete BootOrder completely.')
        self.add_argument('-t', '--timeout', type=int, action=EfibootmgrArgumentParser.StoreParamAsAction, metavar='N', help='Set boot manager timeout in seconds.')
        self.add_argument('-T', '--delete-timeout', action=EfibootmgrArgumentParser.StoreFlagAsAction, help='Delete boot manager timeout.')

        # Other Action parameters/options (often used with -c / -C)
        self.add_argument('-d', '--disk', default='/dev/sda', help='The disk containing the EFI System Partition (default: /dev/sda).')
        self.add_argument('-p', '--part', type=int, default=1, help='The partition number holding the EFI System Partition (default: 1).')
        self.add_argument('-l', '--loader', help='Path to the EFI loader executable (e.g., "\\EFI\\ubuntu\\grubx64.efi").')
        self.add_argument('-L', '--label', help='User-friendly text label for the new boot entry.')
        self.add_argument("-u", "--unicode", action='store_true', help='Pass extra command line options as UC-2 encoded string.')

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
        def check_invalid_params(params, required_params: list[str], invalid_params: list[str]) -> None:
            """
            Check that the provided parameters in the parsed namespace exist, and that the invalid parameters are missing or set to None

            Raise an argparse.error() if processing fails

            :param params: argparse Namespace after parsing
            :param required_params: List of parameter names that must have a value in the namespace
            :param invalid_params: List of parameter names that must not have a value in the namespace
            """
            error_template: str = f'Selected action ({parsed.actions[0]})' if parsed.actions else 'Selected action ({parsed.actions[0]})'
            # Get list of missing parameters, if any exist, raise an error
            missing_params = [f'{p}' for p in required_params if params[p] is None]
            if missing_params: self.error(f'Selected action ({parsed.actions[0]}) requires the following missing parameter(s): {', '.join(missing_params)}')

            # Get list of invalid parameters, if any exist, raise an error
            invalid_params = [f'{k}={v}' for k, v in params.items() if k in invalid_params and v is not None]
            if invalid_params: self.error(f'Selected action ({parsed.actions[0] if 'actions' in parsed else 'No action'}) does not allow the following invalid parameter(s): {', '.join(invalid_params)}')

        # Call base class method to parse arguments and store in internal variable
        parsed = super().parse_args(args=args, namespace=namespace)

        # No action specified, selected action is to display current configuration
        if 'actions' not in parsed: parsed.actions = ['display']

        # Ensure that mutually exclusive actions have not been specified
        if len(parsed.actions) > 1: self.error(f"The following options are mutually exclusive and cannot be run together: {', '.join(parsed.actions)}")

        match parsed.actions[0]:
            case 'active' | 'inactive' | 'delete_bootnum':
                # These three options require bootnum to be specified and loader AND label to NOT be specified
                check_invalid_params(params=vars(parsed), required_params=['bootnum'], invalid_params=['loader', 'label'])
                parsed.params = {'bootnum': parsed.bootnum}

            case 'create' | 'create_only':
                # These two options require boot entry parameters to be specified and bootnum to NOT be specified
                check_invalid_params(params=vars(parsed), required_params=['loader', 'label'], invalid_params=['bootnum'])
                parsed.params = {'disk': parsed.disk, 'part': parsed.part, 'loader': parsed.loader, 'label': parsed.label, 'unicode': parsed.unicode}

            case _:
                # All other actions have no required parameters and all others in the list are invalid
                check_invalid_params(params=vars(parsed), required_params=[], invalid_params=['bootnum', 'loader', 'label'])
                match parsed.actions[0]:
                    case 'bootnext': parsed.params = {'bootnext': parsed.bootnext}
                    case 'bootorder': parsed.params = {'bootorder': parsed.bootorder}
                    case 'timeout': parsed.params = {'timeout': parsed.timeout}
                    case _: parsed.params = {}

        return parsed


def pyefibootmgr():
    parser = EfibootmgrArgumentParser()

    args = parser.parse_args()

    # Create the boot manager instance and read from current variables
    boot_mgr = BootManager()
    boot_mgr.update_from_efi()


    match args.actions[0]:
        case 'active':
            print(f'Execute {args.actions[0]} action with parameters {args.params}')
        case 'inactive':
            print(f'Execute {args.actions[0]} action with parameters {args.params}')
        case 'delete_bootnum':
            print(f'Execute {args.actions[0]} action with parameters {args.params}')
        case 'create':
            print(f'Execute {args.actions[0]} action with parameters {args.params}')
        case 'create_only':
            print(f'Execute {args.actions[0]} action with parameters {args.params}')
        case 'remove_dups':
            print(f'Execute {args.actions[0]} action with parameters {args.params}')
        case 'bootnext':
            print(f'Execute {args.actions[0]} action with parameters {args.params}')
        case 'delete-bootnext':
            print(f'Execute {args.actions[0]} action with parameters {args.params}')
        case 'bootorder':
            print(f'Execute {args.actions[0]} action with parameters {args.params}')
        case 'delete_bootorder':
            print(f'Execute {args.actions[0]} action with parameters {args.params}')
        case 'timeout':
            print(f'Execute {args.actions[0]} action with parameters {args.params}')
        case 'delete_timeout':
            print(f'Execute {args.actions[0]} action with parameters {args.params}')
        case _:
            print(f'Unknown action: {args.actions[0]}')

    boot_mgr.display(args.verbose)


if __name__ == "__main__":
    pyefibootmgr()
