enum sf_io_mode {
  SF_IO_MODE_NORMAL,
  SF_IO_MODE_DUAL_OUTPUT,
  SF_IO_MODE_QUAD_OUTPUT,
  SF_IO_MODE_DUAL_IO,
  SF_IO_MODE_QUAD_IO,
};


/*
union {
  struct { uint8_t interface : 4, unwrap : 1, rsvd : 3; };
  uint8_t value;
} io_mode;
*/
struct spi_flash_cfg {
  uin8_t io_mode;

  uint8_t continuous_read_support;
  uint8_t clock_delay;
  uint8_t clock_invert;

  uint8_t reset_enable_cmd;
  uint8_t reset_cmd;

  /* Exit continuous read mode command */
  uint8_t exit_continuous_read_cmd;
  uint8_t exit_continuous_read_cmd_size;

  uint8_t jedec_id_cmd;
  uint8_t jedec_id_cmd_dmy_clk;
  uint8_t qpi_jedec_id_cmd;
  uint8_t qpi_jedec_id_cmd_dmy_clk;

  uint8_t sector_size;
  uint8_t manufacturer_id;
  uint16_t page_size;

  uint8_t chip_erase_cmd;
  uint8_t sector_erase_cmd;
  uint8_t block32K_erase_cmd;
  uint8_t block64K_erase_cmd;

  uint8_t write_enable_cmd;
  uint8_t page_program_cmd;

  uint8_t qio_page_program_cmd;
  uint8_t qio_page_program_addr_mode;

  uint8_t fast_read_cmd;
  uint8_t fast_read_cmd_dmy_clk;

  uint8_t fast_read_do_cmd;
  uint8_t fast_read_do_cmd_dmy_clk;

  uint8_t fast_read_dio_cmd;
  uint8_t fast_read_dio_cmd_dmy_clk;

  uint8_t fast_read_qo_cmd;
  uint8_t fast_read_qo_cmd_dmy_clk;

  uint8_t fast_read_gio_cmd;
  uint8_t fast_read_gio_cmd_dmy_clk;

  uint8_t qpi_fast_read_qio_cmd;
  uint8_t qpi_fast_read_qio_cmd_dmy_clk;

  uint8_t qpi_page_program_cmd;

  //TODO(Jacek): Heavy shit here
  uint8_t write_reg_enable_cmd;
  uint8_t write_enable_idx;
  uint8_t qe_idx;
  uint8_t busy_idx;
  uint8_t write_enable_bit_pos;
  uint8_t quad_enable_bit_pos;
  uint8_t busy_status_bit_pos;
  uint8_t write_enable_write_reg_len;
  uint8_t write_enable_read_reg_len;

  uint8_t qeWriteRegLen;
  uint8_t qeReadRegLen;

  uint8_t quad_enable_read_reg_len;
  uint8_t release_power_down_cmd;
  uint8_t busy_read_reg_len;

  uint8_t read_reg_cmd_buff[4];
  uint8_t write_reg_cmd_buff[4];

  uint8_t enter_qpi_cmd;
  uint8_t exit_qpi_cmd;

  uint8_t continuous_read_mode_config;
  uint8_t exit_continuous_read_mode_config;

  uint8_t enable_burst_wrap_cmd;
  uint8_t enable_burst_wrap_cmd_dmy_clk;
  uint8_t enable_burst_wrap_cmd_data_mode;
  uint8_t enable_burst_wrap_cmd_data;

  uint8_t disable_burst_wrap_cmd;
  uint8_t disable_burst_wrap_cmd_dmy_clk;
  uint8_t disable_burst_wrap_cmd_data_mode;
  uint8_t disable_burst_wrap_cmd_data;

  uint16_t sector_erase_time;
  uint16_t block32K_erase_time;
  uint16_t block64K_erase_time;
  uint16_t page_program_time;
  uint16_t chip_erase_time;

  uint8_t pdDelay;
  uint8_t qe_data;
};

struct boot_flash_cfg {
  uint32_t magiccode;
  struct spi_flash_cfg flash_cfg;
  uint32_t crc32;
};
