import os
import logging
import time

from bl_uart import BLUart
from bl_protocol import BLProtocol
from args_parser import ArgsParser

def config_logging(level = logging.DEBUG):
    format = '%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s' \
             '| %(funcName)s() | %(message)s'
    logging.basicConfig(format = format,
                        level = level)

def main():

    config_logging(logging.DEBUG)

    args_parser = ArgsParser()
    args = args_parser.parse_args()

    bl_uart = BLUart(port = args.port,
                     baudrate = args.baudrate,
                     boot_pin = args.bootpin,
                     en_pin = args.enpin)

    bl_proto = BLProtocol(bl_uart)

    #Enter bootloader
    bl_uart.enter_bootloader()

    #Handshake
    bl_proto.handshake()

    #GetBootInfo
    boot_info = bl_proto.get_boot_info()
    logging.info(f"GetBootInfo response: {boot_info}")

    #LoadBootHeader
    file = open('eflash_loader_32m.bin', 'rb')
    bl_proto.load_boot_header(file.read(176))

    #LoadSegmentHeader
    segment_header_response = bl_proto.load_segment_header(file.read(16))
    logging.info(f"LoadSegmentHeader response: {segment_header_response}")

    #LoadSegmentData (Multiple)
    bl_proto.load_full_data(file)
    file.close()

    #CheckImage
    bl_proto.check_image()

    #Unknown operation ??????????
    bl_proto.memory_write(b'\x00\xF1\x00\x40\x45\x48\x42\x4E')
    bl_proto.memory_write(b'\x04\xF1\x00\x40\x00\x00\x01\x22')
    bl_proto.memory_write(b'\x18\x00\x00\x40\x02\x00\x00\x00')
    time.sleep(0.15)

    #Handshake
    bl_proto.handshake()

    #ReadJedecId
    jedecid = bl_proto.read_jedecid()
    logging.info(f"ReadJededId response: {jedecid}")

    #FlashErase
    bl_proto.flash_erase(0x0000, 0x00AF)

    #FlashWrite
    file = open('bootinfo.bin', 'rb')
    bl_proto.flash_write(0x0000, file.read(176))
    file.close()

    #FlashWriteCheck
    bl_proto.flash_write_check()

    #XipReadStart
    bl_proto.xip_read_start()

    #Unknown operation ??????????
    sha = bl_proto.flash_xip_readsha(b'\xB8\x08\x00\x00\x00\x00\x00\xB0\x00\x00\x00')
    logging.info(f"FlashXipReadSha response: {sha}")

    #XipReadFinish
    bl_proto.xip_read_finish()

    img_path = args.firmware
    #FlashErase
    bin_size = os.path.getsize(img_path)
    start_addr = 0x2000
    end_addr = 0x2000 + bin_size - 1
    logging.info(f"Binary size: {bin_size}, start {start_addr}, end {end_addr}")
    bl_proto.flash_erase(start_addr, end_addr)

    #FlashWrite
    file = open(args.firmware, 'rb')
    bl_proto.flash_write_all(start_addr, file)
    file.close()

    #FlashWriteCheck
    bl_proto.flash_write_check()

    #XipReadStart
    bl_proto.xip_read_start()

    #Unknown operation ??????????
    sha = bl_proto.flash_xip_readsha(b'\x3D\x08\x00\x00\x20\x00\x00\xC0\x55\x00\x00')
    logging.info(f"FlashXipReadSha response: {sha}")

    #XipReadStart
    bl_proto.xip_read_finish()

main()
