# Introduction

jq_flasher is small python project which let you upload image onto BL702. \
It implements ISP protocol designed by Bouffalo Lab Team.

## ISP protocol

Most of information about bootloader's protocol can be found here: \
https://github.com/bouffalolab/bl_docs/blob/main/BL602_ISP/en/BL602_ISP_protocol.pdf \
Missing commands has been reverse engineered by using logic analyzer

## Why?

The original soft for flashing BL MCUs is quite messy and hard to analyze. \
My main goal was to replicate only the part responsible for actual flashing via UART and add some custom behavior
in order to automate the process of entering the bootloader mode. 

## Usage

TODO

