import logging
import bl_errors
import bootinfo
from bl_protocol import BLProtocol
from bl_uart import BLUart
from args_parser import ArgsParser

class BLFlasher:
    def __init__(self, bl_uart):
        self.__bl_uart = bl_uart
        self.__bl_proto = BLProtocol(bl_uart)

    def single_connect(self):
        self.__bl_uart.enter_bootloader()
        try:
            self.__bl_proto.handshake()
        except bl_errors.InvalidResponseError:
            return False
        else:
            return True

    def connect(self, retries_amount = 3):
        for attempt in range(retries_amount):
            if self.single_connect():
                return True
        return False

    def flash_efloader(self, efl_path):
            #Get bootinfo
            boot_info = self.__bl_proto.get_boot_info()
            logging.debug(f"GetBootInfo response: {boot_info}")

            with open(efl_path, 'rb') as efl_file:
                # Load bootheader of eflash loader
                self.__bl_proto.load_boot_header(efl_file.read(176))
                # Load segment header of eflash loader
                shr = self.__bl_proto.load_segment_header(efl_file.read(16))
                logging.debug(f"LoadSegmentHeader response: {shr}")
                self.__bl_proto.load_full_data(efl_file)
                img_status = self.__bl_proto.check_image()

            if img_status is True:
                logging.info("Eflash loader has been loaded succesfully")

    def flash_img_bootheader(self, data):
            # Make space for img's bootheader
            self.__bl_proto.flash_erase(0x0000, 0x00AF)
            # Load bootheader of img
            self.__bl_proto.flash_write(0x0000, data)
            # Check write
            fwcr = self.__bl_proto.flash_write_check()
            logging.debug(f"Flash write check response {fwcr}")
            # Check sha
            self.__bl_proto.xip_read_start()
            sha = self.__bl_proto.flash_xip_readsha(b'\xB8\x08\x00\x00\x00\x00\x00\xB0\x00\x00\x00')
            logging.info(f"FlashXipReadSha response: {sha}")
            self.__bl_proto.xip_read_finish()
