import logging
import shutil
import subprocess


__log = logging.getLogger(__name__)
"""Create the module logger"""

__efibootmgr_cmd = shutil.which('efibootmgr')
"""Locate the efibootmgr command, module raises exception if not found"""

if __efibootmgr_cmd is None:
    raise RuntimeError(f'The "efibootmgr" executable could not be found on your system')


def __execute_efibootmgr(args: list[str]) -> subprocess.CompletedProcess:
    """
    Execute the efibootmgr command with the provided parameters

    :param args: List of strings containing the command line arguments. As a private function, no need to validate args is a list of strings
    :return:
    :raise subprocess.CalledProcessError: If efibootmgr command fails
    """
    __log.debug(f'Executing efibootmgr with parameters: {args}')
    result = subprocess.run([__efibootmgr_cmd] + args, capture_output=True, text=True, check=True)
    return result


def __validate_bootnum_param(param: int | str) -> str:
    """
    Validate that param is either an integer mapping to a valid boot number (0000-ffff) or a string matching a valid boot number

    :param param: Integer or string value containing the parameter to validate
    :return: Sanitised string representation of boot number that can be passed to efibootmgr
    :raise ValueError: If param is not an integer or a valid boot number
    """
    if isinstance(param, int) and 0 <= param <= 0xffff:
        return f'{param:04x}'

    if isinstance(param, str):
        if len(param) == 4 and all(c in '0123456789abcdefABCDEF' for c in param):
            return param

    raise ValueError(f'Provided parameter({param} must be integer or string containing hexadecimal value in range 0x0000-0xffff')


def set_timeout(seconds: int):
    """
    Set the EFI Timeout variable to "seconds" seconds

    :param seconds: Integer value for the EFI Timeout variable
    """
    if not isinstance(seconds, int):
        raise TypeError(f'Provided parameter({seconds} must be integer value representing timeout to set in seconds')

    __log.debug(f'Setting EFI Timeout to {seconds}')
    __execute_efibootmgr(['--timeout', f'{seconds}'])


def delete_timeout():
    """
    Delete the currently set EFI Timeout
    """
    __log.debug('Removing EFI Timeout variable')
    __execute_efibootmgr(['--delete-timeout'])


def set_boot_next(entry: int | str):
    """
    Set the BootNext variable to entry

    :param entry: Boot entry in range 0x0000-0xffff. Must be valid integer in range or string value matching requirements
    """
    entry = __validate_bootnum_param(entry)

    __log.debug(f'Setting BootNext to {entry}')
    __execute_efibootmgr(['--bootnext', entry])


def delete_boot_next():
    """
    Delete the currently set BootNext entry
    """
    __log.debug('Removing BootNext variable')
    __execute_efibootmgr(['--delete-bootnext'])


def set_boot_order(entries: list[int] | list[str]):
    """
    Set the BootOrder variable to the list of boot entry numbers provided in entries

    :param entry: Boot entry in range 0x0000-0xffff. Must be valid integer in range or string value matching requirements
    """
    if (not isinstance(entries, list)  # raise exception if entries is not a list
            or not entries  # raise exception if entries is an empty list
            or not (all(isinstance(entry, int) for entry in entries)  # Raise exception if not list of all integers or list of all strings
                    or all(isinstance(entry, str) for entry in entries))):
        raise ValueError(f'Provided list of entries({entries}) must be a list of integers or a list of strings')

    entries = [__validate_bootnum_param(entry) for entry in entries]

    __log.debug(f'Setting boot order to: {entries}')
    __execute_efibootmgr(['--bootorder', ','.join(entries)])


def delete_boot_order():
    """
    Delete the currently set BootOrder entry
    """
    __log.debug('Removing all entries in the BootOrder variable')
    __execute_efibootmgr(['--delete-bootorder'])


def delete_entry(entry: int | str):
    """
    Execute efibootmgr to delete the nominated boot entry number

    :param entry: Boot entry in range 0x0000-0xffff. Must be valid integer in range or string value matching requirements
    """
    entry = __validate_bootnum_param(entry)

    __log.debug(f'Deleting entry {entry}')
    __execute_efibootmgr(['--delete-bootnum', '--bootnum', entry])


def add_entry(kernel):
    pass
    # print_command('Adding EFI Entry')
    # result = subprocess.run([ '/usr/sbin/efibootmgr', '--create-only', '--disk', self.bootdisk.get_disk(), '--part', self.bootdisk.get_partition(), '--label', kernel.efilabel, '--loader', kernel.efifile, '--unicode', kernel.efiextra ], capture_output=True, text=True)
    #
    # if result.returncode != 0: raise Exception(f'Error running efibootmgr\n\n{result.stderr}')
    # print_result(f'Label({kernel.efilabel}) InitRD({kernel.initrd_file})')
