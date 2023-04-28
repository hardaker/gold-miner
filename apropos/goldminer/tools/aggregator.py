#!/usr/bin/python3

import sys
import pyfsdb
import collections
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
import logging
from logging import debug, info, warning, error, critical
from apropos.goldminer.trainer import GoldMineTrainer


def parse_args():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=__doc__,
        epilog="Exmaple Usage: "
        + "trainer-aggregator.py -o output.fsdb web web.fsdb email email.fsdb",
    )

    parser.add_argument(
        "-o",
        "--output",
        default=sys.stdout,
        type=FileType("w"),
        help="Where to write the output file (else stdout)",
    )

    parser.add_argument(
        "--log-level",
        "--ll",
        default="info",
        help="Define the logging verbosity level (debug, info, warning, error, fotal, critical).",
    )

    parser.add_argument(
        "input_data", nargs="+", help="pairs (label SPACE file ...) to aggregate"
    )

    args = parser.parse_args()

    log_level = args.log_level.upper()
    logging.basicConfig(level=log_level, format="%(levelname)-10s:\t%(message)s")

    if len(args.input_data) % 2 != 0 or len(args.input_data) < 1:
        error("input_file_pairs must be an even number of arguments")

    return args


def aggregate_results(pairs, output):
    results = collections.defaultdict(collections.Counter)
    total_counts = collections.Counter()
    keys = set()
    labels = set()
    converters = {}

    # merge all the data
    for n in range(0, len(pairs), 2):
        (label, filename) = pairs[n : n + 2]
        labels.add(label)
        converters[label] = float

        fh = pyfsdb.Fsdb(filename, return_type=pyfsdb.RETURN_AS_DICTIONARY)
        for row in fh:
            results[label][row["key"]] += row["size_count"]
            total_counts[label] += row["size_count"]
            keys.add(row["key"])

    # make fractions again out of aggregated sizes
    for label in results:
        for key in results[label]:
            results[label][key] /= total_counts[label]

    labels = sorted(labels)

    # output the conglomerates
    oh = pyfsdb.Fsdb(out_file_handle=output, converters=converters)
    oh.out_column_names = ["e_pkt_len"] + labels

    for key in sorted(keys, key=int):
        row = [key] + [results[label][key] for label in labels]
        oh.append(row)

    oh.close()


def main():
    """main routine for arg wrapping and calling analysis"""
    args = parse_args()
    aggregate_results(args.input_data, args.output)


if __name__ == "__main__":
    main()
