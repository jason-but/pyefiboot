"""
This file implements the FilePath class within the pyefiboot library

FilePath is an internal class to store File Path information stored within an EFI Boot Entry
"""
# Import System Libraries
import logging

# Import File Path Node Parsing classes
from .hardware_device_path import *
from .acpi_device_path import *
from .messaging_device_path import *
from .media_device_path import *
from .bios_device_path import *


class FilePath:
    """
    FilePath class

    Used within BootEntry to parse and store the file path information associated with an EFI Boot Entry variable

    Class verifies data, and allows for pretty display of path and extraction of any kernel file names associated
    with the path
    """
    # Map node type/subtype information to registries to allow creation
    DEVICE_REGISTRY = {
        1: HARDWARE_DEVICE_REGISTRY,
        2: ACPI_DEVICE_REGISTRY,
        3: MESSAGING_DEVICE_REGISTRY,
        4: MEDIA_DEVICE_REGISTRY,
        5: BIOS_DEVICE_REGISTRY,
    }

    def __init__(self, path_list_data: bytes) -> None:
        """
        FilePath constructor

        Parse file path data contained in path_list_data and construct an internal variable storing Path information

        :param path_list_data: bytes object containing path nodes to parse
        """
        self.__log = logging.getLogger(self.__class__.__name__)

        self.__path_lists: list[list] = [[]]

        unprocessed_data = path_list_data

        # Loop until all nodes in unprocessed data have been parsed
        while len(unprocessed_data) > 0:
            # Extract length of next node in list of nodes
            node_len = int.from_bytes(unprocessed_data[2:4], byteorder='little')
            # Process and append node to self.__path_lists
            self._append_node(unprocessed_data[:node_len])
            # Remove processed node from data to process
            unprocessed_data = unprocessed_data[node_len:]

        # Path Lists contains empty list element (from processing final node), remove it
        self.__log.debug('All nodes parsed, removing empty path list')
        self.__path_lists.pop()

        # If any elements in the list contain a kernel file name, pull it out and store, otherwise __kernel_file is set to None
        self.__kernel_file = next(filter(None, [getattr(node, 'kernel_file', None) for path_list in self.__path_lists for node in path_list]), None)
        self.__log.info(f'Detected kernel file path: {self.__kernel_file}')

    def _append_node(self, node_data: bytes) -> None:
        """
        Create an instance of the class required to parse the node type contained within node_data and append
        it to the internal path_list variable

        :param node_data: bytes object containing the node header and payload
        :raises FilePath.PathTerminator: If this node signifies the end of the File Path chain
        """
        # Decode node header and prepare node_payload for processing
        node_type = node_data[0]
        node_subtype = node_data[1]
        node_len = int.from_bytes(node_data[2:4], byteorder='little')
        node_payload = node_data[4:]

        self.__log.info(f'Parsing node type {node_type:#04x}/{node_subtype:#04x}')
        self.__log.debug(f'Node length: {node_len}')
        self.__log.debug(f'Node payload: {node_payload}')

        # If this node type signifies the end of the file path, create a new file path for the next node and return
        if node_type == 0x7f and node_subtype == 0xFF:
            self.__log.info('End of path list, creating new path list')
            self.__path_lists.append([])
            return

        try:
            # Create the class to parse the node payload and append to the path list
            self.__path_lists[-1].append(FilePath.DEVICE_REGISTRY[node_type][node_subtype](node_payload))
            self.__log.info(f'New Node: {self.__path_lists[-1][-1]}')

        except KeyError:
            # No class implemented yet for this node type
            self.__log.warning(f'Node Parser for {node_type}/{node_subtype} not found')

    @property
    def kernel_file(self) -> str | None:
        """
        :return: Internal (read-only) property stored in __kernel_file
        """
        return self.__kernel_file

    def __str__(self):
        """
        :return: String representation of File Paths stored in __path_lists
        """
        return '\n'.join('/'.join(map(str, path_list)) for path_list in self.__path_lists)

