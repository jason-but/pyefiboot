"""
This file implements the Messaging Device Path (File Path Node parsing) classes within the pyefiboot library

Each class parses a single node, providing a string representation for display purposes
"""
# Import System Libraries
import struct
import logging
import ipaddress


class MDP_3_1_ATAPI:
    """Messaging (ATAPI) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Messaging (ATAPI) Device Path')

        self.__pri_sec, self.__mast_slave, self.__number = struct.unpack('<BBH', node_data)

    def __str__(self) -> str:
        """:return: String representation of the ATAPI Node"""
        return f'ATAPI({'primary' if self.__pri_sec == 0 else 'secondary'},{'master' if self.__mast_slave == 0 else 'slave'},{self.__number})'


class MDP_3_2_SCSI:
    """Messaging (SCSI) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Messaging (SCSI) Device Path')

        self.__target_id, self.__number = struct.unpack('<HH', node_data)

    def __str__(self) -> str:
        """:return: String representation of the SCSI Node"""
        return f'SCSI(target={self.__target_id},{self.__number})'


class MDP_3_3_Fiber_Channel:
    """Messaging (Fibre Channel) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Messaging (Fibre Channel) Device Path')

        _, self.__name, self.__number = struct.unpack('<LQQ', node_data)

    def __str__(self) -> str:
        """:return: String representation of the Fibre Channel Node"""
        return f'FibChn({self.__name},{self.__number})'


class MDP_3_4_I394:
    """Messaging (I394) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Messaging (I394) Device Path')

        _, self.__guid = struct.unpack('<LQ', node_data)

    def __str__(self) -> str:
        """:return: String representation of the I394 Node"""
        return f'I394(guid={self.__guid})'


class MDP_3_5_USB:
    """Messaging (USB) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Messaging (USB) Device Path')

        self.__port, self.__interface = struct.unpack('<BB', node_data)

    def __str__(self) -> str:
        """:return: String representation of the USB Node"""
        return f'USB({self.__port:#04x},{self.__interface:#04x})'


class MDP_3_11_MAC:
    """Messaging (MAC) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Messaging (MAC) Device Path')

        self.__mac, self.__type = struct.unpack('<32sB', node_data)
        match self.__type:
            case 1: self.__type = 'Ethernet'
            case 2: self.__type = 'ExpEthernet'
            case 3: self.__type = 'ax25'
            case 6: self.__type = 'IEEE802'
            case 7: self.__type = 'arcnet'
            case 9: self.__type = 'TokenRing'

    def __str__(self) -> str:
        """:return: String representation of the MAC Node"""
        return f'MAC({':'.join(f'{b:02x}' for b in self.__mac[:6])},{self.__type})'


class MDP_3_12_IP4:
    """Messaging (IPv4) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Messaging (IPv4) Device Path')

        laddr, raddr, self.__lport, self.__rport, self.__protocol, self.__static, gateway, mask = struct.unpack('<4s4sHHHB4sL', node_data)
        self.__laddr = str(ipaddress.IPv4Address(laddr))
        self.__raddr = str(ipaddress.IPv4Address(raddr))
        self.__gateway = str(ipaddress.IPv4Address(gateway))
        self.__prefix = 32 - (mask ^ 0xffffffff).bit_length()
        self.__mask = str(ipaddress.IPv4Address(mask))

    def __str__(self) -> str:
        """:return: String representation of the IPv4 Node"""
        return f'IPv4(local={self.__laddr}/{self.__prefix}:{self.__lport},{'DHCP' if self.__static == 0 else 'Static'},remote={self.__raddr}:{self.__rport}, mask={self.__mask},gateway={self.__gateway})'


class MDP_3_13_IP6:
    """Messaging (IPv6) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.debug('Messaging (IPv6) Device Path')

        laddr, raddr, self.__lport, self.__rport, self.__protocol, origin, self.__prefix, gateway = struct.unpack('<16s16sHHHBB16s', node_data)
        self.__laddr = str(ipaddress.IPv6Address(laddr))
        self.__raddr = str(ipaddress.IPv6Address(raddr))
        self.__gateway = str(ipaddress.IPv6Address(gateway))
        self.__origin = 'static' if origin == 0 else 'auto' if origin == 1 else 'stateful'

    def __str__(self) -> str:
        """:return: String representation of the IPv6 Node"""
        def ip_string(addr: bytes) -> str:
            return '.'.join(f'{b}' for b in addr)

        return f'IPv6(local={self.__laddr}/{self.__prefix}:{self.__lport},{self.__origin},remote={self.__raddr}:{self.__rport},gateway={self.__gateway})'


# Class factory registration mapping Messaging Device node subtypes to the class for construction
MESSAGING_DEVICE_REGISTRY = {
    1: {'len': 8, 'class': MDP_3_1_ATAPI},
    2: {'len': 8, 'class': MDP_3_2_SCSI},
    3: {'len': 24, 'class': MDP_3_3_Fiber_Channel},
    4: {'len': 16, 'class': MDP_3_4_I394},
    5: {'len': 6, 'class': MDP_3_5_USB},
    11: {'len': 37, 'class': MDP_3_11_MAC},
    12: {'len': 27, 'class': MDP_3_12_IP4},
    13: {'len': 60, 'class': MDP_3_13_IP6}
}