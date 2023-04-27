#!/usr/bin/python3

import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
import logging
from logging import debug, info, warning, error, critical
from apropos.goldmine.trainer import GoldMineTrainer
from apropos.goldmine.trainer.widthtrainer import GoldMineWidthTrainer


def parse_args():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=__doc__,
        epilog="Exmaple Usage: " + "pcap-to-fsdb.py -o output.fsdb input.pcap",
    )

    parser.add_argument(
        "-o",
        "--output",
        default=sys.stdout,
        type=FileType("w"),
        help="Where to write the output file (else stdout)",
    )

    parser.add_argument(
        "-a",
        "--addresses",
        default=None,
        type=str,
        nargs="*",
        help="Only look at packets from these addresses",
    )

    parser.add_argument(
        "-f",
        "--filter",
        default=None,
        help="Use a pcap filter to filter packets",
    )

    parser.add_argument(
        "-T",
        "--no-timing",
        action="store_true",
        help="Don't do timing analysis (expensive in memory)",
    )

    parser.add_argument(
        "--log-level",
        "--ll",
        default="info",
        help="Define the logging verbosity level (debug, info, warning, error, fotal, critical).",
    )

    parser.add_argument(
        "-W",
        "--width-trainer",
        action="store_true",
        help="Use the [beta] width trainer",
    )

    parser.add_argument(
        "pcap_files", nargs="+", help="Where to read the pcap file(s) from"
    )

    args = parser.parse_args()

    log_level = args.log_level.upper()
    logging.basicConfig(level=log_level, format="%(levelname)-10s:\t%(message)s")

    return args


def main():
    """main routine for arg wrapping and calling analysis"""
    args = parse_args()

    if args.width_trainer:
        trainer = GoldMineWidthTrainer(addresses=args.addresses)
    else:
        trainer = GoldMineTrainer(
            do_timing_analysis=(not args.no_timing), addresses=args.addresses
        )

    trainer.analyze_files(args.pcap_files, pkt_filter=args.filter)
    trainer.generate_results()
    trainer.output_to_fsdb(out_file_handle=args.output)


if __name__ == "__main__":
    main()
