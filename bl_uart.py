import serial
import queue
import time
import logging
import threading

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

        self.__rx_thread_start()

    def send_data(self, data):
        """Send data over UART.

        Args:
            data (bytearray): Data to sent.
        """

        self.uart.write(data)

    def __rx_thread(self):
        while self.uart.is_open:
            time.sleep(0.02)
            len = self.uart.in_waiting
            if len > 0 and self.rx_callback is not None:
                self.rx_callback(self.uart.read(len))

    def __rx_thread_start(self):
        self.rx_thread = threading.Thread(target = self.__rx_thread)
        self.rx_thread.start()

    def register_rx_callback(self, rx_callback):
        self.rx_callback = rx_callback

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
        time.sleep(0.5)
        self.reset()
        time.sleep(0.5)
        self.boot_pin_set(False)

    def reset(self):
        self.en_pin_set(False)
        time.sleep(1)
        self.en_pin_set(True)
