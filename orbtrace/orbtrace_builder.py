#!/usr/bin/env python3

import deps

import os
import argparse

from pathlib import Path

from litex.soc.integration.soc_core import soc_core_args, soc_core_argdict
from litex.soc.integration.builder import Builder, builder_args, builder_argdict
from litex.build.lattice.trellis import trellis_args, trellis_argdict

from orbtrace.soc import OrbSoC

def main():
    parser = argparse.ArgumentParser(description = "Orbtrace", add_help = False)

    parser_actions = parser.add_argument_group('Actions')
    parser_orbtrace = parser.add_argument_group('Orbtrace options')
    parser_platform = parser.add_argument_group('Platform options')

    parser_platform.add_argument("--platform", choices = ['ecpix5', 'orbtrace_mini'], required = True, help = 'Select platform')
    parser_platform.add_argument("--profile", default = 'default', help = 'Select profile (argument defaults)')

    args, _ = parser.parse_known_args()

    if args.platform == 'ecpix5':
        from orbtrace.platforms.ecpix5 import Platform
    
    elif args.platform == 'orbtrace_mini':
        from orbtrace.platforms.orbtrace_mini import Platform

    Platform.add_arguments(parser_platform)

    # Add help after selecting platform to make sure all arguments are included
    parser_actions.add_argument('-h', '--help', action = 'help', help = 'Show this message')

    parser_actions.add_argument("--build",         action="store_true", help="Build bitstream")
    parser_actions.add_argument("--load",          action="store_true", help="Load bitstream")
    parser_actions.add_argument("--flash",         action="store_true", help="Flash bitstream to SPI Flash")

    parser_platform.add_argument("--sys-clk-freq",  default=75e6,        help="System clock frequency (default: 75MHz)")

    builder_args(parser.add_argument_group('Builder options'))
    soc_core_args(parser.add_argument_group('SoC core options'))
    trellis_args(parser.add_argument_group('Trellis options'))

    parser_orbtrace.add_argument('--with-debug', action = 'store_true', help = 'Enable debug functionality')
    parser_orbtrace.add_argument('--without-debug', action = 'store_false', dest = 'with_debug')
    parser_orbtrace.add_argument('--with-trace', action = 'store_true', help = 'Enable trace functionality')
    parser_orbtrace.add_argument('--without-trace', action = 'store_false', dest = 'with_trace')
    parser_orbtrace.add_argument('--with-target-power', action = 'store_true', help = 'Enable target power control')
    parser_orbtrace.add_argument('--without-target-power', action = 'store_false', dest = 'with_target_power')
    parser_orbtrace.add_argument('--with-dfu', choices = ['bootloader', 'runtime'], help = 'Enable DFU support')
    parser_orbtrace.add_argument('--with-test-io', action = 'store_true', help = 'Enable test IO')

    parser_orbtrace.add_argument('--usb-vid', type = lambda x: int(x, 16), default = 0x1209, help = 'USB Vendor ID')
    parser_orbtrace.add_argument('--usb-pid', type = lambda x: int(x, 16), default = 0x3443, help = 'USB Product ID')

    parser_orbtrace.add_argument('--led-default', type = lambda x: int(x, 16), default = 0xa, help = 'Default LED settings')
    parser_orbtrace.add_argument('--bootloader-auto-reset', action = 'store_true', help = 'Enable auto-reset to jump from bootloader to app')
    parser_orbtrace.add_argument('--with-reset-csr', action = 'store_true', help = 'Enable reset CSR')

    parser.set_defaults(**Platform.get_profile(args.profile))

    args = parser.parse_args()

    platform = Platform(
        device = args.device,
        #toolchain = 'trellis',
    )

    if not args.output_dir:
        args.output_dir = Path('build') / platform.name

    if not args.csr_csv:
        args.csr_csv = Path(args.output_dir) / 'gateware' / 'csr.csv'

    soc = OrbSoC(
        platform = platform,
        sys_clk_freq  = int(float(args.sys_clk_freq)),
        with_debug = args.with_debug,
        with_trace = args.with_trace,
        with_target_power = args.with_target_power,
        with_dfu = args.with_dfu,
        with_reset_csr = args.with_reset_csr,
        with_test_io = args.with_test_io,
        usb_vid = args.usb_vid,
        usb_pid = args.usb_pid,
        led_default = args.led_default,
        bootloader_auto_reset = args.bootloader_auto_reset,
        **soc_core_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))

    builder.add_software_package('liblitehyperbus', str(Path('liblitehyperbus').absolute()))
    builder.add_software_library('liblitehyperbus')

    builder.build(application_path=str(Path('app').absolute()), **trellis_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(None, os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()
