import serial
import time
import logging

class BLUart:
    def __init__(self,
                 port = '/dev/ttyUSB0',
                 baudrate = 500_000,
                 boot_pin = 'RTS',
                 boot_pin_inverted = True,
                 en_pin = 'DTR',
                 en_pin_inverted = True):

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
        self.en_pin = en_pin
        self.en_pin_inverted = en_pin_inverted

        self.pin_switcher = {
            'RTS' : self.uart.setRTS,
            'DTR' : self.uart.setDTR
        }

    def send_data(self, data):
        """Send data over UART.

        Args:
            data (bytearray): Data to sent.
        """

        logging.debug(f"Data length {len(data)} , Data to send: {data}")
        self.uart.write(data)

    def wait_for_response(self, timeout=2):
        """Wait for incoming data on UART interface.

        Args:
            timeout (float): Max waiting time for data, given in seconds.

        Returns:
            bytearray: Data received from UART.
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

    def en_pin_set(self, state):
        """Put ENABLE pin into given state.

        Args:
            state (boolean): Desired state of ENABLE pin.
        """

        state_str = "HIGH" if state else "LOW"
        logging.debug(f"Enable pin state: {state_str}")
        if self.en_pin_inverted:
            state = not state
        self.pin_switcher[self.en_pin](state)

    def boot_pin_set(self, state):
        """Put BOOT pin into given state

        Args:
            state (boolean): Desired state of BOOT pin.
        """

        state_str = "HIGH" if state else "LOW"
        logging.debug(f"Boot pin state: {state_str}")
        if self.boot_pin_inverted:
            state = not state
        self.pin_switcher[self.boot_pin](state)

    def enter_bootloader(self):
        """Put MCU into bootloader mode."""

        logging.info("Entering bootloader.")
        self.boot_pin_set(True)
        self.en_pin_set(True)
        time.sleep(1)

        self.en_pin_set(False)
        time.sleep(0.5)
        self.en_pin_set(True)

        time.sleep(1)
