import configparser
from ctypes import *
import logging
import zlib

class SpiFlashCfg(Structure):
# 84 bytes
    _fields_ = [
        ('io_mode',                         c_uint8),
        ('continuous_read_support',         c_uint8),
        ('clock_delay',                     c_uint8),
        ('clock_invert',                    c_uint8),

        ('reset_enable_cmd',                c_uint8),
        ('reset_cmd',                       c_uint8),

        ('exit_continuous_read_cmd',        c_uint8),
        ('exit_continuous_read_cmd_size',   c_uint8),

        ('jedec_id_cmd',                    c_uint8),
        ('jedec_id_cmd_dmy_clk',            c_uint8),

        ('qpi_jedec_id_cmd',                c_uint8),
        ('qpi_jedec_id_cmd_dmy_clk',        c_uint8),

        ('sector_size',                     c_uint8),
        ('manufacturer_id',                 c_uint8),
        ('page_size',                       c_uint16),

        ('chip_erase_cmd',                  c_uint8),
        ('sector_erase_cmd',                c_uint8),
        ('block32K_erase_cmd',              c_uint8),
        ('block64K_erase_cmd',              c_uint8),

        ('write_enable_cmd',                c_uint8),
        ('page_program_cmd',                c_uint8),

        ('qio_page_program_cmd',            c_uint8),
        ('qio_page_program_addr_mode',      c_uint8),

        ('fast_read_cmd',                   c_uint8),
        ('fast_read_cmd_dmy_clk',           c_uint8),

        ('qpi_fast_read_cmd',               c_uint8),
        ('qpi_fast_read_cmd_dmy_clk',       c_uint8),

        ('fast_read_do_cmd',                c_uint8),
        ('fast_read_do_cmd_dmy_clk',        c_uint8),

        ('fast_read_dio_cmd',               c_uint8),
        ('fast_read_dio_cmd_dmy_clk',       c_uint8),

        ('fast_read_qo_cmd',                c_uint8),
        ('fast_read_qo_cmd_dmy_clk',        c_uint8),

        ('fast_read_qio_cmd',               c_uint8),
        ('fast_read_qio_cmd_dmy_clk',       c_uint8),

        ('qpi_fast_read_qio_cmd',           c_uint8),
        ('qpi_fast_read_qio_cmd_dmy_clk',   c_uint8),

        ('qpi_page_program_cmd',            c_uint8),

        # Write enable for Voltile Status Register
        ('vsr_write_enable_cmd',            c_uint8),

        ('write_enable_reg_idx',            c_uint8),
        ('quad_enable_reg_idx',             c_uint8),
        ('busy_reg_idx',                    c_uint8),

        ('write_enable_bit_pos',            c_uint8),
        ('quad_enable_bit_pos',             c_uint8),
        ('busy_bit_pos',                    c_uint8),

        # Length of write_enable_reg during write/read (?)
        ('write_enable_reg_len_wr',         c_uint8),
        ('write_enable_reg_len_rd',         c_uint8),

        ('quad_enable_reg_len_wr',          c_uint8),
        ('guad_enable_reg_len_rd',          c_uint8),

        ('release_power_down_cmd',          c_uint8),

        ('busy_reg_len_rd',                 c_uint8),

        ('read_reg_cmd0',                   c_uint8),
        ('read_reg_cmd1',                   c_uint8),
        ('read_reg_cmd2',                   c_uint8),   # Unused
        ('read_reg_cmd3',                   c_uint8),   # Unused

        ('write_reg_cmd0',                  c_uint8),
        ('write_reg_cmd1',                  c_uint8),
        ('write_reg_cmd2',                  c_uint8),   # Unused
        ('write_reg_cmd3',                  c_uint8),   # Unused

        ('enter_qpi_mode_cmd',              c_uint8),
        ('exit_qpi_mode_cmd',               c_uint8),

        ('continuous_read_mode_cfg',        c_uint8),
        ('continuous_read_mode_exit_cfg',   c_uint8),

        ('burst_wrap_enable_cmd',           c_uint8),
        ('burst_wrap_enable_cmd_dmy_clk',   c_uint8),
        ('burst_wrap_enable_data_mode',     c_uint8),
        ('burst_wrap_enable_data',          c_uint8),

        ('disable_burst_wrap_cmd',          c_uint8),
        ('disable_burst_wrap_cmd_dmy_clk',  c_uint8),
        ('disable_burst_wrap_data_mode',    c_uint8),
        ('disable_burst_wrap_data',         c_uint8),

        ('sector_erase_time',               c_uint16),
        ('block32K_erase_time',             c_uint16),
        ('block64K_erase_time',             c_uint16),
        ('page_program_time',               c_uint16),
        ('chip_erase_time',                 c_uint16),
        ('release_power_down_delay',        c_uint8),

        ('quad_enable_data',                c_uint8),
    ]

    #TODO(Jacek): Break the object init in case of error
    def __init__(self, config_source):
        super().__init__()
        self.__translation_dict = {
#---------------------------------- Commands -----------------------------------

            # Fast read commands
            'fast_read_cmd'             : 'fast_read_cmd',
            'fast_read_dmy_clk'         : 'fast_read_cmd_dmy_clk',
            'fast_read_do_cmd'          : 'fast_read_do_cmd',
            'fast_read_do_dmy_clk'      : 'fast_read_do_cmd_dmy_clk',
            'fast_read_dio_cmd'         : 'fast_read_dio_cmd',
            'fast_read_dio_dmy_clk'     : 'fast_read_dio_cmd_dmy_clk',
            'fast_read_qo_cmd'          : 'fast_read_qo_cmd',
            'fast_read_qo_dmy_clk'      : 'fast_read_qo_cmd_dmy_clk',
            'fast_read_qio_cmd'         : 'fast_read_qio_cmd',
            'fast_read_qio_dmy_clk'     : 'fast_read_qio_cmd_dmy_clk',
            'qpi_fast_read_cmd'         : 'qpi_fast_read_cmd',
            'qpi_fast_read_dmy_clk'     : 'qpi_fast_read_cmd_dmy_clk',
            'qpi_fast_read_qio_cmd'     : 'qpi_fast_read_qio_cmd',
            'qpi_fast_read_qio_dmy_clk' : 'qpi_fast_read_qio_cmd_dmy_clk',

            # Erase commands
            'chip_erase_cmd'            : 'chip_erase_cmd',
            'chip_erase_time'           : 'chip_erase_time',
            'sector_erase_cmd'          : 'sector_erase_cmd',
            'sector_erase_time'         : 'sector_erase_time',
            'blk32k_erase_cmd'          : 'block32K_erase_cmd',
            'blk32k_erase_time'         : 'block32K_erase_time',
            'blk64k_erase_cmd'          : 'block64K_erase_cmd',
            'blk64k_erase_time'         : 'block64K_erase_time',

            # Program commands
            'page_prog_cmd'             : 'page_program_cmd',
            'page_prog_time'            : 'page_program_time',
            'qpage_prog_cmd'            : 'qio_page_program_cmd',
            'qpi_page_prog_cmd'         : 'qpi_page_program_cmd',
            'qual_page_prog_addr_mode'  : 'qio_page_program_addr_mode',

            # JEDEC ID commands
            'jedecid_cmd'               : 'jedec_id_cmd',
            'jedecid_cmd_dmy_clk'       : 'jedec_id_cmd_dmy_clk',
            'qpi_jedecid_cmd'           : 'qpi_jedec_id_cmd',
            'qpi_jedecid_dmy_clk'       : 'qpi_jedec_id_cmd_dmy_clk',

            # Burst wrap enable command
            'burst_wrap_cmd'            : 'burst_wrap_enable_cmd',
            'burst_wrap_dmy_clk'        : 'burst_wrap_enable_cmd_dmy_clk',
            'burst_wrap_data_mode'      : 'burst_wrap_enable_data_mode',
            'burst_wrap_code'           : 'burst_wrap_enable_data',

            # Burst wrap disable command
            'de_burst_wrap_cmd'         : 'disable_burst_wrap_cmd',
            'de_burst_wrap_cmd_dmy_clk' : 'disable_burst_wrap_cmd_dmy_clk',
            'de_burst_wrap_code_mode'   : 'disable_burst_wrap_data_mode',
            'de_burst_wrap_code'        : 'disable_burst_wrap_data',

            # Read register commands
            'reg_read_cmd0'             : 'read_reg_cmd0',
            'reg_read_cmd1'             : 'read_reg_cmd1',
            #'reg_read_cmd2'             : 'read_reg_cmd2',
            #'reg_read_cmd3'             : 'read_reg_cmd3',

            # Wrtie register commands
            'reg_write_cmd0'            : 'write_reg_cmd0',
            'reg_write_cmd1'            : 'write_reg_cmd1',
            #'reg_write_cmd2'            : 'write_reg_cmd2',
            #'reg_write_cmd3'            : 'write_reg_cmd3',

            # Release power down command
            'release_power_down'        : 'release_power_down_cmd',
            'power_down_delay'          : 'release_power_down_delay',

            # Reset commands
            'reset_en_cmd'              : 'reset_enable_cmd',
            'reset_cmd'                 : 'reset_cmd',

            # QPI mode commands
            'enter_qpi_cmd'             : 'enter_qpi_mode_cmd',
            'exit_qpi_cmd'              : 'exit_qpi_mode_cmd',

            # Write enable command
            'write_enable_cmd'          : 'write_enable_cmd',

            # VSR wrtie enable command
            'write_vreg_enable_cmd'     : 'vsr_write_enable_cmd',

#--------------------------------- Registers -----------------------------------

            # Quad enable register and related fields
            'qe_reg_index'              : 'quad_enable_reg_idx',
            'qe_bit_pos'                : 'quad_enable_bit_pos',
            'qe_reg_read_len'           : 'guad_enable_reg_len_rd',
            'qe_reg_write_len'          : 'quad_enable_reg_len_wr',
            'qe_data'                   : 'quad_enable_data',

            # Write enable register and related fields
            'wel_reg_index'             : 'write_enable_reg_idx',
            'wel_bit_pos'               : 'write_enable_bit_pos',
            'wel_reg_read_len'          : 'write_enable_reg_len_rd',
            'wel_reg_write_len'         : 'write_enable_reg_len_wr',

            # Busy register register and related fields
            'busy_reg_index'            : 'busy_reg_idx',
            'busy_bit_pos'              : 'busy_bit_pos',
            'busy_reg_read_len'         : 'busy_reg_len_rd',

#------------------------------------ Misc -------------------------------------
            'io_mode'                   : 'io_mode',
            'sfctrl_clk_delay'          : 'clock_delay',
            'sfctrl_clk_invert'         : 'clock_invert',
            'sector_size'               : 'sector_size',
            'mfg_id'                    : 'manufacturer_id',
            'page_size'                 : 'page_size',

            # Continuous read
            'cont_read_support'         : 'continuous_read_support',
            'cont_read_code'            : 'continuous_read_mode_cfg',

            'exit_contread_cmd'         : 'exit_continuous_read_cmd',
            'exit_contread_cmd_size'    : 'exit_continuous_read_cmd_size',
            'cont_read_exit_code'       : 'continuous_read_mode_exit_cfg',
        }

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
    _fields_ = [
        ('magic_code', c_uint32),
        ('cfg',        SpiFlashCfg),
        ('crc32',      c_uint32),
    ]

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
    _fields_ = [
        # TODO(Jacek): Can I make more sense of that ?
        ('xtal_type',       c_uint8),
        ('pll_clk',         c_uint8),
        ('hclk_div',        c_uint8),
        ('bclk_div',        c_uint8),
        ('flash_clk_type',  c_uint8),
        ('flash_clk_div',   c_uint8),
        ('rsvd1',           c_uint8),
        ('rsvd1',           c_uint8),
    ]

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
    _fields_ = [
        ('magic_code', c_uint32),
        ('cfg',        SysClkCfg),
        ('crc32',      c_uint32),
    ]

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
    _fields_ = [
        # TODO(Jacek): Can I make more sense of that ?
        ('sign',                c_uint32, 2),
        ('encrypt_type',        c_uint32, 2),
        ('key_sel',             c_uint32, 2),
        ('rsvd1',               c_uint32, 2),
        ('no_segment',          c_uint32, 1),
        ('cache_select',        c_uint32, 1),
        ('not_load_to_bootrom', c_uint32, 1),
        ('aes_region_lock',     c_uint32, 1),
        ('cache_way_disable',   c_uint32, 4),
        ('crc_ignore',          c_uint32, 1),
        ('hash_ignore',         c_uint32, 1),
        ('halt_cpu1',           c_uint32, 1),
        ('rsvd2',               c_uint32, 13),
    ]

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
    _fields_ = [
        ('bval', BootCfgBits),
        ('wval', c_uint32),
    ]

    def __init__(self, config_source):
        super().__init__()
        self.bval = BootCfgBits(config_source)

    def __repr__(self):
        return repr(self.bval)

class ImgSegmentInfo(Union):
    #4 bytes
    _fields_ = [
        ('segment_cnt', c_uint32),
        ('img_len',     c_uint32),
    ]

    def __init__(self, config_source):
        super().__init__()
        self.img_len = int(config_source['img_len'], 0)

    def __repr__(self):
        return f"segment_cnt/img_len = {self.segment_cnt}"

class ImgStart(Union):
    #4 bytes
    _fields_ = [
        ('ram_addr', c_uint32),
        ('flash_offset', c_uint32),
    ]

    def __init__(self, config_source):
        super().__init__()
        self.ram_addr = int(config_source['img_start'], 0)

    def __repr__(self):
        return f"ram_addr/flash_offset = {self.ram_addr}"

class BootHeader(Structure):
    # 176 bytes
    _fields_ = [
        ('magic_code',          c_uint32),
        ('revision',            c_uint32),
        ('flash_cfg',           BootFlashCfg),
        ('clk_cfg',             BootClkCfg),
        ('boot_cfg',            BootCfg),
        ('img_segment_info',    ImgSegmentInfo),
        ('boot_entry',          c_uint32),
        ('img_start',           ImgStart),
        ('hash0',               c_uint32),
        ('hash1',               c_uint32),
        ('hash2',               c_uint32),
        ('hash3',               c_uint32),
        ('hash4',               c_uint32),
        ('hash5',               c_uint32),
        ('hash6',               c_uint32),
        ('hash7',               c_uint32),
        ('boot2_pt_table_0',    c_uint32),
        ('boot2_pt_table_1',    c_uint32),
        ('crc32',               c_uint32),
    ]

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

        # Cut off the last newline
        return rep_string[:-1]

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
