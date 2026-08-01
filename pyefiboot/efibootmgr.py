import logging
import shutil
import subprocess


__log = logging.getLogger(__name__)
"""Create the module logger"""

__efibootmgr_cmd = shutil.which('efibootmgr')
"""Locate the efibootmgr command, module raises exception if not found"""

if __efibootmgr_cmd is None:
    raise RuntimeError(f'The "efibootmgr" executable could not be found on your system')


def add_entry(kernel):
    pass
    # print_command('Adding EFI Entry')
    # result = subprocess.run([ '/usr/sbin/efibootmgr', '--create-only', '--disk', self.bootdisk.get_disk(), '--part', self.bootdisk.get_partition(), '--label', kernel.efilabel, '--loader', kernel.efifile, '--unicode', kernel.efiextra ], capture_output=True, text=True)
    #
    # if result.returncode != 0: raise Exception(f'Error running efibootmgr\n\n{result.stderr}')
    # print_result(f'Label({kernel.efilabel}) InitRD({kernel.initrd_file})')
