import logging
import serial
import time

def config_logging(level = logging.DEBUG):
    format = '%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s' \
             '| %(funcName)s() | %(message)s'
    logging.basicConfig(format = format,
                        level = level)

class BLUart:
    def __init__(self,
                 port = '/dev/ttyUSB0',
                 baudrate = 2_000_000):
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
        self.commands = {
            'handshake' : b'\x55',
            'get_boot_info' : b'\x10\x00\x00\x00',
            'load_boot_header': b'0x00',

        }

    @staticmethod
    def is_response_ok(response):
        logging.debug(f"Response: {response}")

        # [INFO@JK] Response can't be NoneType and be shorter than 2 bytes
        if response is None:
            result = False
        elif len(response) < 2:
            result = False
        else:
            # [TODO@JK] Idk what to do with "FL"
            result = (response[0:2] == b'OK')

        logging.debug(f"Returned 'OK'?: {result}")
        return result

    def establish_connection(self):
        command = self.commands['handshake'] * int(0.006 * (self.interface.device.baudrate / 10))
        self.interface.send_data(command)
        time.sleep(0.1)
        response = self.interface.wait_for_response()
        result = self.is_response_ok(response)
        logging.debug(f"Connection established?: {result}")
        return result

    def get_boot_info(self):
        command = self.commands['get_boot_info']
        self.interface.send_data(command)
        time.sleep(0.1)
        response = self.interface.wait_for_response()
        logging.debug(f"Response {response}")
        result = self.is_response_ok(response)
        if result is False:
            pass #exception


def main():
    config_logging()
    bl_uart = BLUart()
    uart_proto = UartProtocol(bl_uart)
    uart_proto.establish_connection()
    uart_proto.get_boot_info()

    #len = bl_uart.device.in_waiting
    #print(f"Len: {len}")
    #print(bl_uart.device.read(100))



main()
