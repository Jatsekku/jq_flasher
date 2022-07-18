import configparser

import logging
import zlib
from ctypes import Structure, Union, c_uint8, c_uint32

from bootinfo.constants.BootinfoConstants import SPI_FLASH_CFG_FIELDS, SPI_FLASH_CFG_TRANSLATION_DICT, \
    SPI_BOOT_HEADER_FIELDS, IMG_START_FIELDS, IMG_SEGMENT_INFO_FIELDS, BOOT_CFG_FIELDS, BOOT_CFG_BITS_FIELDS, \
    BOOT_CLK_CFG_FIELDS, SYS_CLK_CFG_FIELDS, BOOT_FLASH_CFG_FIELDS


class SpiFlashCfg(Structure):
# 84 bytes

    _fields_ = SPI_FLASH_CFG_FIELDS

    #TODO(Jacek): Break the object init in case of error
    def __init__(self, config_source):
        super().__init__()
        self.__translation_dict = SPI_FLASH_CFG_TRANSLATION_DICT

        for key in self.__translation_dict.keys():
            # Check for missing fields in provided config
            try:
                value = int(config_source[key], 0)
            except KeyError as e:
                 logging.error(f" {e} is missing in configuration file")
                 return

            field_name = self.__translation_dict[key]

            # Prevent creating new attribiutes
            if not hasattr(self, field_name):
                logging.error(f" Structure do not have {field_name} field")
                return
            setattr(self, self.__translation_dict[key], value)

    def __repr__(self):
        rep_string = ''
        for field in self._fields_:
            rep_string += f"{field[0]} = {getattr(self, field[0])} \n"

        # Cut off the last newline
        return rep_string[:-1]


class BootFlashCfg(Structure):
    # 92 bytes
    _fields_ = BOOT_FLASH_CFG_FIELDS

    def __init__(self, config_source):
        super().__init__()
        self.magic_code = int(config_source['flashcfg_magic_code'], 0)
        self.cfg = SpiFlashCfg(config_source)
        self.crc32 = zlib.crc32(self.cfg)

    def __repr__(self):
        rep_string = ''
        for field in self._fields_:
            rep_string += f"{field[0]} = {getattr(self, field[0])} \n"

        # Cut off the last newline
        return rep_string[:-1]


class SysClkCfg(Structure):
    #8 bytes
    _fields_ = SYS_CLK_CFG_FIELDS

    def __init__(self, config_source):
        super().__init__()
        self.xtal_type =      int(config_source['xtal_type'], 0)
        self.pll_clk =        int(config_source['pll_clk'], 0)
        self.hclk_div =       int(config_source['hclk_div'], 0)
        self.bclk_div =       int(config_source['bclk_div'], 0)
        self.flash_clk_type = int(config_source['flash_clk_type'], 0)
        self.flash_clk_div =  int(config_source['flash_clk_div'], 0)

    def __repr__(self):
        rep_string = ''
        for field in self._fields_:
            rep_string += f"{field[0]} = {getattr(self, field[0])}\n"

        # Cut off the last newline
        return rep_string[:-1]


class BootClkCfg(Structure):
    # 16 bytes
    _fields_ = BOOT_CLK_CFG_FIELDS

    def __init__(self, config_source):
        super().__init__()
        self.magic_code = int(config_source['clkcfg_magic_code'], 0)
        self.cfg = SysClkCfg(config_source)
        self.crc32 = zlib.crc32(self.cfg)

    def __repr__(self):
        rep_string = ''
        for field in self._fields_:
            rep_string += f"{field[0]} = {getattr(self, field[0])}\n"

        # Cut off the last newline
        return rep_string[:-1]


class BootCfgBits(Structure):
    #4 bytes
    _fields_ = BOOT_CFG_BITS_FIELDS

    def __init__(self, config_source):
        super().__init__()
        self.sign                = int(config_source['sign'], 0)
        self.encrypt_type        = int(config_source['encrypt_type'], 0)
        self.key_sel             = int(config_source['key_sel'], 0)
        self.no_segment          = int(config_source['no_segment'], 0)
        self.cache_select        = int(config_source['cache_enable'], 0)
        self.not_load_to_bootrom = int(config_source['notload_in_bootrom'], 0)
        self.aes_region_lock     = int(config_source['aes_region_lock'], 0)
        self.cache_way_disable   = int(config_source['cache_way_disable'], 0)
        self.crc_ignore          = int(config_source['crc_ignore'], 0)
        self.hash_ignore         = int(config_source['hash_ignore'], 0)
        #self.halt_cpu1           = int(config_source['halt_ap'], 0)

    def __repr__(self):
        rep_string = ''
        for field in self._fields_:
            rep_string += f"{field[0]} = {getattr(self, field[0])}\n"

        # Cut off the last newline
        return rep_string[:-1]


class BootCfg(Union):
    #4 bytes
    _fields_ = BOOT_CFG_FIELDS

    def __init__(self, config_source):
        super().__init__()
        self.bval = BootCfgBits(config_source)

    def __repr__(self):
        return repr(self.bval)


class ImgSegmentInfo(Union):
    #4 bytes
    _fields_ = IMG_SEGMENT_INFO_FIELDS

    def __init__(self, config_source):
        super().__init__()
        self.img_len = int(config_source['img_len'], 0)

    def __repr__(self):
        return f"segment_cnt/img_len = {self.segment_cnt}"


class ImgStart(Union):
    #4 bytes
    _fields_ = IMG_START_FIELDS

    def __init__(self, config_source):
        super().__init__()
        self.ram_addr = int(config_source['img_start'], 0)

    def __repr__(self):
        return f"ram_addr/flash_offset = {self.ram_addr}"


class BootHeader(Structure):
    # 176 bytes
    _fields_ = SPI_BOOT_HEADER_FIELDS

    def __init__(self, config_source):
        self.magic_code = int(config_source['magic_code'], 0)
        self.revision = int(config_source['revision'], 0)
        self.flash_cfg = BootFlashCfg(config_source)
        self.clk_cfg = BootClkCfg(config_source)
        self.boot_cfg = BootCfg(config_source)
        self.img_segment_info = ImgSegmentInfo(config_source)
        self.boot_entry = int(config_source['bootentry'], 0)
        self.img_start = ImgStart(config_source)
        self.hash0 = int(config_source['hash_0'], 0)
        self.hash1 = int(config_source['hash_1'], 0)
        self.hash2 = int(config_source['hash_2'], 0)
        self.hash3 = int(config_source['hash_3'], 0)
        self.hash4 = int(config_source['hash_4'], 0)
        self.hash5 = int(config_source['hash_5'], 0)
        self.hash6 = int(config_source['hash_6'], 0)
        self.hash7 = int(config_source['hash_7'], 0)
        self.boot2_pt_table_0 = int(config_source['boot2_pt_table_0'], 0)
        self.boot2_pt_table_1 = int(config_source['boot2_pt_table_1'], 0)
        self.crc32 = int(config_source['crc32'], 0)

    def __repr__(self):
        rep_string = ''
        for field in self._fields_:
            rep_string += f"{field[0]} = {getattr(self, field[0])}\n"


class BootInfo():
    def __init__(self, file):
        config = configparser.ConfigParser()
        config.read(file)

        bootheader_cfg_source = config['BOOTHEADER_CFG']
        self.bootheader = BootHeader(bootheader_cfg_source)

    def get_bytes(self):
        return bytes(self.bootheader)

    def set_img_len(self, img_len):
        self.bootheader.img_segment_info.img_len = img_len
