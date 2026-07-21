"""
This file implements the Messaging Device Path (File Path Node parsing) classes within the pyefiboot library

Each class parses a single node, providing a string representation for display purposes
"""
# Import System Libraries
import ipaddress

# Import BaseNodePathParser sub-module classes
from .basenodepathparser import BaseNodePathParser


class MessagingATAPIDevice_3_1(BaseNodePathParser):
    """Messaging (ATAPI) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<BBH')

        self._log.debug('Messaging (ATAPI) Device Path')

        self.__pri_sec, self.__mast_slave, self.__number = self._fields

    def __str__(self) -> str:
        """:return: String representation of the ATAPI Node"""
        return f'ATAPI({'primary' if self.__pri_sec == 0 else 'secondary'},{'master' if self.__mast_slave == 0 else 'slave'},{self.__number})'


class MessagingSCSIDevice_3_2(BaseNodePathParser):
    """Messaging (SCSI) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<HH')

        self._log.debug('Messaging (SCSI) Device Path')

        self.__target_id, self.__number = self._fields

    def __str__(self) -> str:
        """:return: String representation of the SCSI Node"""
        return f'SCSI(target={self.__target_id},{self.__number})'


class MessagingFibreChannelDevice_3_3(BaseNodePathParser):
    """Messaging (Fibre Channel) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<LQQ')

        self._log.debug('Messaging (Fibre Channel) Device Path')

        _, self.__name, self.__number = self._fields

    def __str__(self) -> str:
        """:return: String representation of the Fibre Channel Node"""
        return f'FibChn({self.__name},{self.__number})'


class MessagingI394Device_3_4(BaseNodePathParser):
    """Messaging (I394) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<LQ')

        self._log.debug('Messaging (I394) Device Path')

        _, self.__guid = self._fields

    def __str__(self) -> str:
        """:return: String representation of the I394 Node"""
        return f'I394(guid={self.__guid})'


class MessagingUSBDevice_3_5(BaseNodePathParser):
    """Messaging (USB) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<BB')

        self._log.debug('Messaging (USB) Device Path')

        self.__port, self.__interface = self._fields

    def __str__(self) -> str:
        """:return: String representation of the USB Node"""
        return f'USB({self.__port:#04x},{self.__interface:#04x})'


class MessagingI2ODevice_3_10(BaseNodePathParser):
    """Messaging (I2O Random Block Storage) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<L')

        self._log.debug('Messaging (I2O Random Block Storage) Device Path')

        self.__tid, = self._fields

    def __str__(self) -> str:
        """:return: String representation of the MAC Node"""
        return f'I2O(ID:{self.__tid})'


class MessagingMACDevice_3_11(BaseNodePathParser):
    """Messaging (MAC) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<32sB')

        self._log.debug('Messaging (MAC) Device Path')

        self.__mac, self.__type = self._fields
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


class MessagingIPv4Device_3_12(BaseNodePathParser):
    """Messaging (IPv4) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<4s4sHHHB4sL')

        self._log.debug('Messaging (IPv4) Device Path')

        laddr, raddr, self.__lport, self.__rport, self.__protocol, self.__static, gateway, mask = self._fields
        self.__laddr = str(ipaddress.IPv4Address(laddr))
        self.__raddr = str(ipaddress.IPv4Address(raddr))
        self.__gateway = str(ipaddress.IPv4Address(gateway))
        self.__prefix = 32 - (mask ^ 0xffffffff).bit_length()
        self.__mask = str(ipaddress.IPv4Address(mask))

    def __str__(self) -> str:
        """:return: String representation of the IPv4 Node"""
        return f'IPv4(local={self.__laddr}/{self.__prefix}:{self.__lport},{'DHCP' if self.__static == 0 else 'Static'},remote={self.__raddr}:{self.__rport}, mask={self.__mask},gateway={self.__gateway})'


class MessagingIPv6Device_3_13(BaseNodePathParser):
    """Messaging (IPv6) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<16s16sHHHBB16s')

        self._log.debug('Messaging (IPv6) Device Path')

        laddr, raddr, self.__lport, self.__rport, self.__protocol, origin, self.__prefix, gateway = self._fields
        self.__laddr = str(ipaddress.IPv6Address(laddr))
        self.__raddr = str(ipaddress.IPv6Address(raddr))
        self.__gateway = str(ipaddress.IPv6Address(gateway))
        self.__origin = 'static' if origin == 0 else 'auto' if origin == 1 else 'stateful'

    def __str__(self) -> str:
        """:return: String representation of the IPv6 Node"""
        def ip_string(addr: bytes) -> str:
            return '.'.join(f'{b}' for b in addr)

        return f'IPv6(local={self.__laddr}/{self.__prefix}:{self.__lport},{self.__origin},remote={self.__raddr}:{self.__rport},gateway={self.__gateway})'


class MessagingNVMExpressDevice_3_23(BaseNodePathParser):
    """Messaging (USB) Device Path Parser"""
    def __init__(self, node_data: bytes):
        """:param node_data: Python bytes object containing data to be parsed"""
        super().__init__(node_data, '<LQ')

        self._log.debug('Messaging (USB) Device Path')

        self.__namespace_id, self.__extended_uid = self._fields

    def __str__(self) -> str:
        """:return: String representation of the USB Node"""
        return f'NVME({self.__namespace_id:#010x},{self.__extended_uid:#018x})'


# Class factory registration mapping Messaging Device node subtypes to the class for construction
MESSAGING_DEVICE_REGISTRY = {
    1: MessagingATAPIDevice_3_1,
    2: MessagingSCSIDevice_3_2,
    3: MessagingFibreChannelDevice_3_3,
    4: MessagingI394Device_3_4,
    5: MessagingUSBDevice_3_5,
    10: None,
    11: MessagingMACDevice_3_11,
    12: MessagingIPv4Device_3_12,
    13: MessagingIPv6Device_3_13,
    23: MessagingNVMExpressDevice_3_23,
}
