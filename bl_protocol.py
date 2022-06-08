import time
import logging
import bl_errors

class BLProtocol:
    def __init__(self, interface):
        self.interface = interface
        self.cmd_id = {
            'handshake' : b'\x55',
            'get_boot_info' : b'\x10',
            'load_boot_header' : b'\x11',
            'load_segment_header' : b'\x17',
            'load_segment_data' : b'\x18',
            'check_image' : b'\x19',
            'mem_write' : b'\x50',
            'read_jedecid' : b'\x36',
            'flash_erase' : b'\x30',
            'flash_write' : b'\x31',
            'flash_write_check' : b'\x3A',
            'xip_read_start' : b'\x60',
            'flash_xip_readsha' : b'\x3E',
            'xip_read_finish' : b'\x61',
        }

    @staticmethod
    def is_response_ok(response):
        """Check MCU's response.

        Args:
            response (bytearray): MCU response data.

        Returns:
            bool: True if operation was succesful.

        Raises:
            TODO
        """

        logging.debug(f"Response: {response}")
        if response is None or len(response) < 2:
            raise bl_errors.InvalidResponseError()

        if response[0:2] == b'OK':
            result = True

        if response[0:2] == b'FL':
            err_lsb = response[2]
            err_msb = response[3]
            logging.debug(f"err_msb: {err_msb}, err_lsb {err_lsb}")
            raise bl_errors.errors_agregator[err_msb][err_lsb - 1]()

        return result

    @staticmethod
    def calc_checksum(data):
        """Calculate checksum.

        Args:
            data (bytearray): Data to calculate checksum of.

        Returns:
            int: Calculated checksum.
        """

        logging.info("Checksum calculation")
        sum = 0
        for e in data:
            sum = sum + e
        checksum = sum & 0xFF
        logging.debug(f"Checksum value: {checksum}")
        return checksum

    def send_data_wait_for_response(self, data, timeout=0.1):
        """Send data to MCU and wait for its response.

        Args:
            data (bytearray): Data to sent.
            timeout (float): Max waiting time for data, given in seconds.

        Returns:
            bytearray: Data received from UART.
        """
        self.interface.send_data(data)
        time.sleep(timeout)
        return self.interface.wait_for_response()

    def handshake(self):
        """Perform handshake with MCU's bootloader.

        Returns:
            bool: True if operation was succesful.
        """
        logging.info("Handshake Command")
        command = (self.cmd_id['handshake']
                   * int(0.006 * (self.interface.uart.baudrate / 10)))
        response = self.send_data_wait_for_response(command)
        return self.is_response_ok(response)

    def get_boot_info(self):
        """Send "get_boot_info" command to MCU.

        Returns:
            bytearray: MCU's response
        """

        logging.info("GetBootInfo Command")
        command = self.cmd_id['get_boot_info'] + b'\x00\x00\x00'
        response = self.send_data_wait_for_response(command)
        if self.is_response_ok(response):
            return response[2:]

    def load_boot_header(self, boot_header):
        """Send "load_boot_header" command to MCU.

        Args:
            boot_header (bytearray): Boot header data (?).

        Returns:
            bool: True if operation was succesful.

        Raise:
            TODO
        """

        logging.info("LoadBootHeader Command")
        # boot_header is always 176 bytes long
        if len(boot_header) != 176:
            raise bl_errors.InvalidResponseError()

        command = (self.cmd_id['load_boot_header']
                   + b'\x00\xB0\x00' + boot_header)
        response = self.send_data_wait_for_response(command)
        return self.is_response_ok(response)

    def load_segment_header(self, segment_header):
        """Send "load_segment_header" command to MCU.

        Args:
            segment_header (bytearray): Segment header data (?).

        Returns:
            bytearray: MCU's response.

        Raise:
            TODO
        """

        logging.info("LoadSegmentHeader Command")
        # Segment_header is always 16 bytes long
        if len(segment_header) != 16 :
            raise bl_errors.InvalidResponseError()

        command = (self.cmd_id['load_segment_header']
                   + b'\x00\x10\x00' + segment_header)
        response = self.send_data_wait_for_response(command)
        if self.is_response_ok(response):
            return response[2:]

    def load_segment_data(self, segment_data):
        """Send "load_segment_data" command to MCU.

        Args:
            segment_data (bytearray): Segment data (?).

        Returns:
            bytearray: MCU's response.

        Raise:
            TODO
        """

        logging.info("LoadSegmentData Command")
        dlen = len(segment_data)
        if dlen > 4096:
            raise ValueError("Segment_data can't be longer than 4096 bytes")
        command = (self.cmd_id['load_segment_data']
                   + b'\x00' + dlen.to_bytes(2, 'little') + segment_data)
        response = self.send_data_wait_for_response(command)
        return self.is_response_ok(response)

    def check_image(self):
        """Send "check_image" command to MCU.

        Returns:
            bool: True if operation was succesful.
        """

        logging.info("CheckImage Command")
        command = self.cmd_id['check_image'] + b'\x00\x00\x00'
        response = self.send_data_wait_for_response(command)
        return self.is_response_ok(response)

    def memory_write(self, unknown):
        """Send "memory_write" command to MCU.

        Args:
            unknown (bytearray): IDK what is it (?).
        """
        logging.info("MemoryWrite Command")
        command = self.cmd_id['mem_write'] + b'\x00\x08\x00' + unknown
        self.interface.send_data(command)
        #response = self.send_data_wait_for_response(command)
        #return self.is_response_ok(response)

    def read_jedecid(self):
        """Read JEDEC ID

        Returns:
            bytearray: MCU's response.
        """

        logging.info("ReadJedecId Command")
        command = self.cmd_id['read_jedecid'] + b'\x00\x00\x00'
        response = self.send_data_wait_for_response(command)
        if self.is_response_ok(response):
            return response[2:]

    def flash_erase(self, start_addr, end_addr):
        """Erase MCU's given flash memory region.

        Args:
            start_addr (int): Starting address for memory erasing.
            end_addr (int): Ending address for memory erasing.

        Returns:
            bool: True if operation was succesful.
        """

        logging.info("FlashErase Command")
        data = (b'\x08\x00'
                + start_addr.to_bytes(4, 'little')
                + end_addr.to_bytes(4, 'little'))
        checksum = self.calc_checksum(data)
        command = (self.cmd_id['flash_erase']
                   + checksum.to_bytes(1, 'little') + data)
        #This operation take some time to confirm success,
        #so delay is a bit higher
        response = self.send_data_wait_for_response(command, 5)
        return self.is_response_ok(response)

    def flash_write(self, start_addr, payload):
        """Write MCU's flash memory region with given payload.

        Args:
            start_addr (int): Starting address for memory writing.
            payload (bytearray): Data which has to be written to memory.

        Returns:
            bool: True if operation was succesful.

        Raises:

        """

        logging.info("FlashWrite Command")
        dlen = len(payload)
        if dlen > 8000:
            raise ValueError("Payload can't be longer than 8000 bytes")
        data = ((dlen + 4).to_bytes(2, 'little')
                + start_addr.to_bytes(4, 'little')
                + payload)
        checksum = self.calc_checksum(data)
        command = (self.cmd_id['flash_write']
                   + checksum.to_bytes(1, 'little') + data)
        response = self.send_data_wait_for_response(command)
        return self.is_response_ok(response)

    def flash_write_check(self):
        """Check if flash memory writing was succesful.

        Returns:
            bool: True if operation was succesful.
        """

        logging.info("FlashWriteCheck Command")
        command = self.cmd_id['flash_write_check'] + b'\x00\x00\x00'
        response = self.send_data_wait_for_response(command)
        return self.is_response_ok(response)

    def xip_read_start(self):

        logging.info("XipReadStart Command")
        command = self.cmd_id['xip_read_start'] + b'\x00\x00\x00'
        response = self.send_data_wait_for_response(command)
        return self.is_response_ok(response)

    def flash_xip_readsha(self, unknown):
        logging.info("XipReadSha Command")
        command = self.cmd_id['flash_xip_readsha'] + unknown
        response = self.send_data_wait_for_response(command)
        if self.is_response_ok(response):
            return response[2:]

    def xip_read_finish(self):
        logging.info("XipReadFinish Command")
        command = self.cmd_id['xip_read_finish'] + b'\x00\x00\x00'
        response = self.send_data_wait_for_response(command)

    def load_full_data(self, file):
        logging.info("LoadFullData Procedure")
        data = file.read(4080)
        while len(data) > 0:
            self.load_segment_data(data)
            data = file.read(4080)

    def flash_write_all(self, start_addr, file):
        logging.info("FlashWriteFull Procedure")
        data = file.read(2048)
        while len(data) > 0:
            self.flash_write(start_addr, data)
            start_addr = start_addr + len(data)
            data = file.read(2048)
