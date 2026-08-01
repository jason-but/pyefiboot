import argparse
import logging
from typing import Any, Callable

from pyefiboot.pyefibootmgr import EfibootmgrArgumentParser
from pyefiboot import BootManager


def pyefibootmgr():
    parser = EfibootmgrArgumentParser()

    args = parser.parse_args()

    # Create the boot manager instance and read from current variables
    boot_mgr = BootManager()
    boot_mgr.update_from_efi()

    action_map: dict[str, Callable] = {
        'delete_bootnum': boot_mgr.delete_entries_by_index,
    }

    for action in args.actions:
        match args.actions[0]:
            case 'active':
                print(f'Execute {action} action with parameters {args.params}')
            case 'inactive':
                print(f'Execute {action} action with parameters {args.params}')
            case 'delete_bootnum':
                print(f'Execute {action} action with parameters {args.params}')
            case 'create':
                print(f'Execute {action} action with parameters {args.params}')
            case 'create_only':
                print(f'Execute {action} action with parameters {args.params}')
            case 'remove_dups':
                print(f'Execute {action} action with parameters {args.params}')
            case 'bootnext':
                print(f'Execute {action} action with parameters {args.params}')
            case 'delete-bootnext':
                print(f'Execute {action} action with parameters {args.params}')
            case 'bootorder':
                print(f'Execute {action} action with parameters {args.params}')
            case 'delete_bootorder':
                print(f'Execute {action} action with parameters {args.params}')
            case 'timeout':
                print(f'Execute {action} action with parameters {args.params}')
            case 'delete_timeout':
                print(f'Execute {action} action with parameters {args.params}')
            case _:
                print(f'Unknown action: {args.actions[0]}')
        if action in action_map:
            action_map[action](**args.params)

#    boot_mgr.display(args.verbose)


if __name__ == "__main__":
    pyefibootmgr()
