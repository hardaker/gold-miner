#!/usr/bin/python3

"""Scans an interface or pcap file for the likelihood of traffic
within an ipsec/encrypted tunnel for a particular class that you may
want to prioritize."""

import sys
import os

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
import collections
import pyfsdb
import numpy as np
import pprint
import logging
from logging import debug, info, warning, error, critical
import time

try:
    import curses
except Exception:
    pass

from apropos.goldminer.pickaxe.pickaxe import PickAxe


def get_parser():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=__doc__,
        epilog="Exmaple Usage: gold-miner.py -i " + "INTERFACE -g profilename",
    )

    parser.add_argument(
        "-i", "--interface", type=str, help="The interface to monitor for ESP traffic"
    )

    parser.add_argument(
        "-r", "--pcap-file", type=str, help="Read in a PCAP file to analyze"
    )

    parser.add_argument(
        "-p",
        "--training_profile",
        type=str,
        help="The training profile to read for calculating percentages",
    )

    parser.add_argument(
        "-t",
        "--thresholds",
        type=str,
        help="Threshold file to use for determining success",
    )

    parser.add_argument(
        "-j", "--output-json", action="store_true", help="Output data in json format"
    )

    parser.add_argument(
        "-J",
        "--output-flattened-json",
        action="store_true",
        help="Output data in json format, but flattened",
    )

    parser.add_argument(
        "-u", "--output_ui", action="store_true", help="Output data in a window"
    )

    parser.add_argument(
        "-g",
        "--gold-profiles",
        type=str,
        nargs="+",
        help="profiles to identify as 'gold' ; put multiple separated by ,s in an argument",
    )

    parser.add_argument(
        "-a",
        "--all-profiles",
        default=[],
        type=str,
        nargs="*",
        help="Keys to use for all the columns (gold and non-gold)",
    )

    parser.add_argument(
        "--algorithm",
        default="comparison",
        type=str,
        help="Algorithm value to use (lms, linear, comparison)",
    )

    parser.add_argument(
        "-n",
        "--max-packets",
        default=-1,
        type=int,
        help="Maximum number of packets to read",
    )

    parser.add_argument(
        "-N",
        "--report-every",
        default=None,
        type=int,
        help="only report results every N packets",
    )

    parser.add_argument(
        "-L", "--live-results", action="store_true", help="Print live results"
    )

    parser.add_argument(
        "-C",
        "--curses",
        action="store_true",
        help="Turn on a curses view of the output results",
    )

    parser.add_argument(
        "-P",
        "--percentage",
        action="store_true",
        help="Display results as a percentage",
    )

    parser.add_argument(
        "-R",
        "--raw-values",
        action="store_true",
        help="Display raw-value results instead of confidence",
    )

    parser.add_argument(
        "-k",
        "--size-key",
        default="e_pkt_len",
        type=str,
        help="The key to use for pkt size data",
    )

    parser.add_argument(
        "-F",
        "--packet-filter",
        default=None,
        type=str,
        help="Only process these sniffed packets",
    )

    parser.add_argument(
        "-w",
        "--high-low-watermark",
        default=None,
        type=float,
        nargs=2,
        help="Use high/low watermarks to restrict output.  The first argument should be the high value, and the second the low value.",
    )

    parser.add_argument(
        "-3",
        "--three-tuple-only",
        action="store_true",
        help="Only use 3-tuples for analyzing packets instead of 5",
    )

    parser.add_argument(
        "--timing",
        action="store_true",
        help="Add the analysis time length information to the output",
    )

    parser.add_argument(
        "-T",
        "--search-window-length",
        default=None,
        type=float,
        help="Fixed time stamp length to check data over",
    )

    parser.add_argument(
        "-U",
        "--search-window-time-file",
        default=None,
        type=str,
        help="A FSDB file of times to search per packet size",
    )

    parser.add_argument(
        "--log-level",
        "--ll",
        default="info",
        help="Define the logging verbosity level (debug, info, warning, error, fotal, critical).",
    )

    parser.add_argument(
        "--log-file",
        "--lf",
        help="Define a logfile to save logging output to instead of stderr",
    )

    parser.add_argument(
        "--window-analysis",
        action="store_true",
        help="Do window analysis (developer mode)",
    )

    parser.add_argument(
        "output_file",
        type=FileType("w"),
        nargs="?",
        default=sys.stdout,
        help="Where to send the output data to",
    )

    return parser


def parse_args():
    parser = get_parser()
    args = parser.parse_args()

    log_level = args.log_level.upper()
    log_file = args.log_file
    logging.basicConfig(
        level=log_level, filename=log_file, format="%(levelname)-10s:\t%(message)s"
    )

    if not args.gold_profiles or len(args.gold_profiles) == 0:
        raise ValueError("-g is a required parameter")

    if not args.interface and not args.pcap_file:
        raise ValueError("either -i or -r is required")

    return args


def process_arguments(args, axe):
    if args.live_results:
        from apropos.goldminer.output.goldTextDump import GoldTextDump

        axe.output = GoldTextDump()
    elif args.curses:
        from apropos.goldminer.output.goldCurses import GoldCurses

        axe.output = GoldCurses(
            as_percentage=args.percentage, parameter_file=args.thresholds
        )
    elif args.output_json or args.output_flattened_json:
        from apropos.goldminer.output.goldJson import GoldJson

        axe.output = GoldJson(
            as_percentage=args.percentage,
            raw_values=args.raw_values,
            as_list=True,
            parameter_file=args.thresholds,
            flatten=args.output_flattened_json,
        )
    elif args.output_ui:
        try:
            from apropos.goldminer.output.goldQt import GoldQt
        except Exception:
            error("The goldQt module was not found -- please install gold-miner-ui")
            exit(1)

        axe.output = GoldQt()
    else:
        # default to FSDB output formatted
        from apropos.goldminer.output.goldFsdb import GoldFsdb

        axe.output = GoldFsdb(
            out_file_handle=args.output_file,
            as_percentage=args.percentage,
            raw_values=args.raw_values,
            parameter_file=args.thresholds,
        )

    if args.high_low_watermark:
        from apropos.goldminer.output.goldHighLowWatermark import GoldHighLowWatermark

        highlow = GoldHighLowWatermark(
            high=args.high_low_watermark[0],
            low=args.high_low_watermark[1],
            output=axe.output,
        )
        debug("inserted a high-low process")
        axe.output = highlow


def main() -> None:
    """main routine for arg wrapping and calling analysis"""
    args = parse_args()

    # create our searcher
    axe = PickAxe(
        gold_profiles=args.gold_profiles,
        training_data_file=args.training_profile,
        training_key=args.size_key,
        support_windowing=args.window_analysis,
        algorithm=args.algorithm,
        report_every_n=args.report_every,
        three_tuple_only=args.three_tuple_only,
    )

    # read in our training data files, and the keys/etc we expect
    # for both gold and dirty

    process_arguments(args, axe)

    debug("ready to read packets")

    search_window_length = args.search_window_length
    if args.search_window_time_file:
        search_window_length = pyfsdb.Fsdb(
            args.search_window_time_file, return_type=pyfsdb.RETURN_AS_DICTIONARY
        ).get_all()

    run_time_start = time.time()
    if args.interface:
        debug(f"  sniffing({args.interface})")
        axe.process_interface(args.interface, args.packet_filter)
    else:
        (identifiers, counts, processed_data) = axe.process_pcap(
            args.pcap_file,
            None,
            args.max_packets,
            search_window_length,
            dig_for_gold=(not args.window_analysis),
        )
        if args.window_analysis:
            axe.window_analysis()
    run_time_end = time.time()

    if args.timing:
        print(f"# run-time: {run_time_end - run_time_start} seconds")

    info("End of data stream")
    axe.close()


if __name__ == "__main__":
    main()
