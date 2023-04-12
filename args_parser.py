import argparse

class ArgsParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()

        #------------------------- Bouffalolab flags ---------------------------
        self.parser.add_argument('--chipname', required = False,
                                 help = 'chip name')

        self.parser.add_argument('--interface', default = 'uart',
                                 help = 'interface to use')

        self.parser.add_argument('--bootsrc', default = 'flash',
                                 help = 'select boot source')

        self.parser.add_argument('--port', required = False,
                                 help = 'serial port to use')

        self.parser.add_argument('--baudrate', type = int,
                                 default = 500_000,
                                 help = 'serial port baudrate')

        self.parser.add_argument('--xtal',
                                 help = 'MCU cristal oscilator frequency')

        self.parser.add_argument('--flashclk',
                                 help = 'MCU flash clock')

        self.parser.add_argument('--pllclk',
                                 help = 'MCU pll clock')

        self.parser.add_argument('--firmware',
                                 help = 'image to write onto MCU')
        
        self.parser.add_argument('--debug', action = 'store_true', default=False, help='enable debug mode')

        # Helper function to automatically detect int base
        def auto_int(x):
            return int(x, 0)

        self.parser.add_argument('--addr', type = auto_int,
                                 default = 0x2000,
                                 help = 'start address for firmware write')

        self.parser.add_argument('--dts',
                                 help = 'device tree')

        #---------------------------- Custom flags -----------------------------
        self.parser.add_argument('--enpin', default = 'DTR',
                                 help = 'select signal connected to ENABLE pin')

        self.parser.add_argument('--bootpin', default = 'RTS',
                                 help = 'select signal connected to BOOT pin')


    def parse_args(self):
        return self.parser.parse_args()
