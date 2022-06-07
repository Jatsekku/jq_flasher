import logging
import serial
import time
import os
import bl_errors

def config_logging(level = logging.DEBUG):
    format = '%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s' \
             '| %(funcName)s() | %(message)s'
    logging.basicConfig(format = format,
                        level = level)

class BLUart:
    def __init__(self,
                 port = '/dev/ttyUSB0',
                 baudrate = 500_000,
                 boot_pin = 'RTS',
                 boot_pin_inverted = True,
                 enable_pin = 'DTR',
                 enable_pin_inverted = True):

        # Config and open serial connection
        self.uart = serial.Serial(port,
                                  baudrate,
                                  bytesize = serial.EIGHTBITS,
                                  parity = serial.PARITY_NONE,
                                  stopbits = serial.STOPBITS_ONE,
                                  timeout = 2)

        # Define boot/enable GPIO connections
        self.boot_pin = boot_pin
        self.boot_pin_inverted = boot_pin_inverted
        self.enable_pin = enable_pin
        self.enable_pin_inverted = enable_pin_inverted

        self.pin_switcher = {
            'RTS' : self.uart.setRTS,
            'DTR' : self.uart.setDTR
        }

    def send_data(self, data):
        """
        Send data over UART

        Parameters:
            data (bytearray): Data to sent
        """

        logging.debug(f"Data length {len(data)} , Data to send: {data}")
        self.uart.write(data)

    def wait_for_response(self, timeout=2):
        """
        Wait for incoming data on UART interface

        Parameters:
            timeout (float): Desired timeout, given in seconds

        Returns:
            bytearray: Data received from UART
        """

        logging.debug(f"Timeout: {timeout}")
        self.uart.timeout = timeout
        len = self.uart.in_waiting
        logging.debug(f"Waiting data amount = {len}")
        if len == 0:
            len = 1
        data = self.uart.read(len)
        logging.debug(f"Received data: {data}")
        return data

    def enable_pin_set(self, state):
        """
        Put ENABLE pin into given state

        Parameters:
            state (boolean): Desired state of ENABLE pin
        """

        state_str = "HIGH" if state else "LOW"
        logging.debug(f"Enable pin state: {state_str}")
        if self.enable_pin_inverted:
            state = not state
        self.pin_switcher[self.enable_pin](state)

    def boot_pin_set(self, value):
        """
        Put BOOT pin into given state

        Parameters:
            state (boolean): Desired state of BOOT pin
        """

        state_str = "HIGH" if state else "LOW"
        logging.debug(f"Boot pin state: {state_str}")
        if self.boot_pin_inverted:
            state = not state
        self.pin_switcher[self.boot_pin](value)

    def enter_bootloader(self):
        """
        Put MCU into bootloader mode
        """

        logging.info("Entering bootloader.")
        self.boot_pin_set(True)
        self.enable_pin_set(True)
        time.sleep(1)

        self.enable_pin_set(False)
        time.sleep(0.5)
        self.enable_pin_set(True)

        time.sleep(1)

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
        """
        Check MCU's response

        Parameters:
            response (bytearray): MCU response data
        """
        
        logging.debug(f"Response: {response}")
        if response is None or len(response) < 2:
            raise bl_errors.InvalidResponseError()

        if response[0:2] == b'OK':
            result = True

        logging.debug(f"Returned 'OK'?: {result}")
        return result

    @staticmethod
    def calc_checksum(data):
        logging.info("Checksum calculation")
        sum = 0
        for e in data:
            sum = sum + e

        checksum = sum & 0xFF
        logging.debug(f"Checksum value: {checksum}")
        return checksum


    def send_data_wait_for_response(self, data, delay = 0.1):
        self.interface.send_data(data)
        time.sleep(delay)
        return self.interface.wait_for_response()

    def handshake(self):
        logging.info("Handshake Command")
        command = self.cmd_id['handshake'] * int(0.006 * (self.interface.uart.baudrate / 10))
        response = self.send_data_wait_for_response(command)
        return self.is_response_ok(response)

    def get_boot_info(self):
        logging.info("GetBootInfo Command")
        command = self.cmd_id['get_boot_info'] + b'\x00\x00\x00'
        response = self.send_data_wait_for_response(command)
        if self.is_response_ok(response):
            return response[2:]

    def load_boot_header(self, boot_header):
        logging.info("LoadBootHeader Command")
        if len(boot_header) != 176:
            return None #exception
        command = self.cmd_id['load_boot_header'] + b'\x00\xB0\x00' + boot_header
        response = self.send_data_wait_for_response(command)
        return self.is_response_ok(response)

    def load_segment_header(self, segment_header):
        logging.info("LoadSegmentHeader Command")
        # segment_header is always 16 bytes long
        if len(segment_header) != 16 :
            return None #exception
        command = self.cmd_id['load_segment_header'] + b'\x00\x10\x00' + segment_header
        response = self.send_data_wait_for_response(command)
        if self.is_response_ok(response):
            return response[2:]

    def load_segment_data(self, segment_data):
        logging.info("LoadSegmentData Command")
        # segment_data can't be longer than 4096 byts
        dlen = len(segment_data)
        if dlen > 4096:
            return None #exception
        command = self.cmd_id['load_segment_data'] + b'\x00' + dlen.to_bytes(2, 'little') + segment_data
        response = self.send_data_wait_for_response(command)
        return self.is_response_ok(response)

    def check_image(self):
        logging.info("CheckImage Command")
        command = self.cmd_id['check_image'] + b'\x00\x00\x00'
        response = self.send_data_wait_for_response(command)
        return self.is_response_ok(response)

    def memory_write(self, unknown):
        logging.info("MemoryWrite Command")
        command = self.cmd_id['mem_write'] + b'\x00\x08\x00' + unknown
        self.interface.send_data(command)
        #response = self.send_data_wait_for_response(command)
        #return self.is_response_ok(response)

    def read_jedecid(self):
        logging.info("ReadJedecId Command")
        command = self.cmd_id['read_jedecid'] + b'\x00\x00\x00'
        response = self.send_data_wait_for_response(command)
        if self.is_response_ok(response):
            return response[2:]

    def flash_erase(self, start_addr, end_addr):
        logging.info("FlashErase Command")
        data = b'\x08\x00' + start_addr.to_bytes(4, 'little') + end_addr.to_bytes(4, 'little')
        checksum = self.calc_checksum(data)
        command = self.cmd_id['flash_erase'] + checksum.to_bytes(1, 'little') + data
        #This operation take some time to confirm success, so delay is a bit higher
        response = self.send_data_wait_for_response(command, 5)
        return self.is_response_ok(response)

    def flash_write(self, start_addr, payload):
        logging.info("FlashWrite Command")
        dlen = len(payload)
        if dlen > 8000:
            return None
        data = (dlen + 4).to_bytes(2, 'little') + start_addr.to_bytes(4, 'little') + payload
        checksum = self.calc_checksum(data)
        command = self.cmd_id['flash_write'] + checksum.to_bytes(1, 'little') + data
        response = self.send_data_wait_for_response(command)
        return self.is_response_ok(response)

    def flash_write_check(self):
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




def main():
    path = '/home/jatsekku/Documents/bl_mcu_sdk/tools/bflb_flash_tool/'

    config_logging()
    bl_uart = BLUart()
    uart_proto = UartProtocol(bl_uart)

    bl_uart.enter_bootloader()
    #Handshake
    uart_proto.handshake()

    #GetBootInfo
    boot_info = uart_proto.get_boot_info()
    logging.info(f"GetBootInfo response: {boot_info}")

    #LoadBootHeader
    file = open('../chips/bl702/eflash_loader/eflash_loader_32m.bin', 'rb')
    uart_proto.load_boot_header(file.read(176))

    #LoadSegmentHeader
    segment_header_response = uart_proto.load_segment_header(file.read(16))
    logging.info(f"LoadSegmentHeader response: {segment_header_response}")

    #LoadSegmentData (Multiple)
    uart_proto.load_full_data(file)
    file.close()

    #CheckImage
    uart_proto.check_image()

    #Unknown operation ??????????
    uart_proto.memory_write(b'\x00\xF1\x00\x40\x45\x48\x42\x4E')
    uart_proto.memory_write(b'\x04\xF1\x00\x40\x00\x00\x01\x22')
    uart_proto.memory_write(b'\x18\x00\x00\x40\x02\x00\x00\x00')
    time.sleep(0.15)

    #Handshake
    uart_proto.handshake()

    #ReadJedecId
    jedecid = uart_proto.read_jedecid()
    logging.info(f"ReadJededId response: {jedecid}")

    #FlashErase
    uart_proto.flash_erase(0x0000, 0x00AF)

    #FlashWrite
    file = open('../chips/bl702/img_create_mcu/bootinfo.bin', 'rb')
    uart_proto.flash_write(0x0000, file.read(176))
    file.close()

    #FlashWriteCheck
    uart_proto.flash_write_check()

    #XipReadStart
    uart_proto.xip_read_start()

    #Unknown operation ??????????
    sha = uart_proto.flash_xip_readsha(b'\xB8\x08\x00\x00\x00\x00\x00\xB0\x00\x00\x00')
    logging.info(f"FlashXipReadSha response: {sha}")

    #XipReadStart
    uart_proto.xip_read_finish()

    #FlashErase
    bin_size = os.path.getsize(path + 'chips/bl702/img_create_mcu/img.bin')
    start_addr = 0x2000
    end_addr = 0x2000 + bin_size - 1
    logging.info(f"Binary size: {bin_size}, start {start_addr}, end {end_addr}")
    uart_proto.flash_erase(start_addr, end_addr)

    #FlashWrite
    file = open(path + 'chips/bl702/img_create_mcu/img.bin', 'rb')
    uart_proto.flash_write_all(start_addr, file)
    file.close()

    #FlashWriteCheck
    uart_proto.flash_write_check()

    #XipReadStart
    uart_proto.xip_read_finish()

    #Unknown operation ??????????
    sha = uart_proto.flash_xip_readsha(b'\x3D\x08\x00\x00\x20\x00\x00\xC0\x55\x00\x00')
    logging.info(f"FlashXipReadSha response: {sha}")

    #XipReadStart
    uart_proto.xip_read_finish()






main()
