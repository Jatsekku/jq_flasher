import os
import logging
import time

from bl_uart import BLUart
from bl_protocol import BLProtocol
from args_parser import ArgsParser
from bl_flasher import BLFlasher
from bootinfo import BootInfo

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
    bl_flasher = BLFlasher(bl_uart)

    bl_flasher.connect(2)
    bl_flasher.flash_efloader('chips/bl702/image/eflash_loader/eflash_loader_32m.bin')

    #Unknown operation - these commands are not waiting for response
    bl_proto.memory_write(b'\x00\xf1\x00\x40\x45\x48\x42\x4e')
    bl_proto.memory_write(b'\x04\xf1\x00\x40\x00\x00\x01\x22')
    bl_proto.memory_write(b'\x18\x00\x00\x40\x00\x00\x00\x00')
    bl_proto.memory_write(b'\x18\x00\x00\x40\x02\x00\x00\x00')
    time.sleep(0.35)

    bl_proto.handshake()
    #ReadJedecId
    mac_addr = bl_proto.efuse_read_mac_addr()
    logging.info(f"EfuseReadMacAddr response: {mac_addr}")

    #ReadJedecId
    jedecid = bl_proto.read_jedecid()
    logging.info(f"ReadJededId response: {jedecid}")

    img_path = '/home/jatsekku/Documents/bl_mcu_sdk/out/examples/ble/ble_peripheral/ble_peripheral_bl702.bin'
    bin_size = os.path.getsize(img_path)

    bootinfo = BootInfo('/home/jatsekku/Documents/jq_flasher/constants/bootinfo.cfg')
    bootinfo.set_img_len(bin_size)

    bl_flasher.flash_img_bootheader(bootinfo.get_bytes())

    #FlashErase
    start_addr = 0x2000
    end_addr = 0x2000 + bin_size - 1
    logging.info(f"Binary size: {bin_size}, start {start_addr}, end {end_addr}")
    bl_proto.flash_erase(0x2000, end_addr)

    #FlashWrite
    file = open(img_path, 'rb')
    bl_proto.flash_write_all(0x2000, file)
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
