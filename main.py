import logging
import serial
import time
import bl_errors

# Notes
# bytes(dlen) may be tricky !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def config_logging(level = logging.DEBUG):
    format = '%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s' \
             '| %(funcName)s() | %(message)s'
    logging.basicConfig(format = format,
                        level = level)

class BLUart:
    def __init__(self,
                 port = '/dev/ttyUSB0',
                 baudrate = 500_000):
        self.device = serial.Serial(port,
                                    baudrate,
                                    bytesize = serial.EIGHTBITS,
                                    parity = serial.PARITY_NONE,
                                    stopbits = serial.STOPBITS_ONE,
                                    timeout = 2)

    def send_data(self, data):
        logging.debug(f"Data length {len(data)} , Data to send: {data}")
        self.device.write(data)

    def wait_for_response(self, timeout=1):
        logging.debug(f"Timeout: {timeout}")
        self.device.timeout = timeout
        len = self.device.in_waiting
        logging.debug(f"Waiting data amount = {len}")
        if len == 0:
            len = 1
        data = self.device.read(len)
        logging.debug(f"Received data: {data}")
        return data

class UartProtocol:
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
        command = self.cmd_id['handshake'] * int(0.006 * (self.interface.device.baudrate / 10))
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
        command = self.cmd_id['load_boot_header'] + b'\x00\xb0\x00' + boot_header
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
        response = self.send_data_wait_for_response(command)
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

    def xip_read_start(self):
        command = self.cmd_id['xip_read_start'] + b'\x00\x00\x00'
        response = self.send_data_wait_for_response(command)

    def flash_xip_readsha(self):
        #?????????????????????????????
        pass

    def xip_read_finish(self):
        command = self.cmd_id['xip_read_finish'] + b'\x00\x00\x00'
        response = self.send_data_wait_for_response(command)

    def load_full_data(self, file):
        logging.info("LoadFullData Procedure")
        data = file.read(4080)
        while len(data) > 0:
            self.load_segment_data(data)
            data = file.read(4080)



def main():
    config_logging()
    bl_uart = BLUart()
    uart_proto = UartProtocol(bl_uart)

    #Handshake
    uart_proto.handshake()

    #GetBootInfo
    boot_info = uart_proto.get_boot_info()
    logging.info(f"GetBootInfo response: {boot_info}")

    #LoadBootHeader
    file = open('eflash_loader_32m.bin', 'rb')
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
    uart_proto.memory_write(b'\x00\xf1\x00\x40\x45\x48\x42\x4E')
    uart_proto.memory_write(b'\x04\xf1\x00\x40\x00\x00\x01\x22')
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
    file = open('bootinfo.bin', 'rb')
    uart_proto.flash_write(0x0000, file.read(176))






main()
