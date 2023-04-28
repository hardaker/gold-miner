import sys
import collections
import numpy as np
from logging import debug, info, warning, error, critical
from apropos.goldminer.trainer import GoldMineBase


class GoldMineWidthTrainer(GoldMineBase):
    def __init__(self, addresses=None, max_width=10000, max_pkt_size=1500):
        super().__init__(addresses)
        self.packet_data = collections.defaultdict(collections.Counter)

        # create the data keys to use
        self.packet_keys = ["size_count"]
        self.percent_keys = ["percent_size_count"]

        self.all_keys = self.packet_keys + self.percent_keys

        self.storage = np.zeros((max_pkt_size, max_width), dtype=bool)

    def analyze_packet(self, pkt, count):
        """Analyzes a packet to pull out features."""
        # count the packet sizes
        self.storage[pkt.len][count] = True

    def generate_results(self):
        """Normalize the counts to fractions"""
        import pdb

        pdb.set_trace()
        self.total_counts = collections.Counter()

        # calculate totals
        for data_key in self.packet_data:
            for key in self.packet_keys:
                self.total_counts["percent_" + key] += int(
                    self.packet_data[data_key][key]
                )

        # now divide:
        for data_key in self.packet_data:
            for key in self.packet_keys:
                self.packet_data[data_key]["percent_" + key] = float(
                    (self.packet_data[data_key][key])
                    / float(self.total_counts["percent_" + key])
                )

        if self.do_timing_analysis:
            self.analyze_packet_size_delays()

    def analyze_packet_size_delays(self):
        import numpy  # only required if doing time delays

        for size in self.packet_size_delays:
            arr = numpy.array(self.packet_size_delays[size])
            self.packet_data[size]["timing_mean"] = arr.mean()
            self.packet_data[size]["timing_median"] = numpy.median(arr)
            self.packet_data[size]["timing_std"] = numpy.std(arr)
            self.packet_data[size]["timing_max"] = arr.max()

            if len(self.packet_size_timestamps[size]) > 1:
                deltas = []
                for n in range(1, len(self.packet_size_timestamps[size])):
                    deltas.append(
                        self.packet_size_timestamps[size][n]
                        - self.packet_size_timestamps[size][n - 1]
                    )
                arr = numpy.array(deltas).astype(float)
                self.packet_data[size]["ipa_mean"] = arr.mean()
                self.packet_data[size]["ipa_min"] = arr.min()
                self.packet_data[size]["ipa_max"] = arr.max()
                self.packet_data[size]["ipa_std"] = numpy.std(arr)

                quantiles = numpy.quantile(arr, [0.25, 0.5, 0.75])
                self.packet_data[size]["ipa_q1"] = quantiles[0]
                self.packet_data[size]["ipa_median"] = quantiles[1]
                self.packet_data[size]["ipa_q3"] = quantiles[2]

            else:
                self.packet_data[size]["ipa_mean"] = 0
                self.packet_data[size]["ipa_min"] = 0
                self.packet_data[size]["ipa_max"] = 0
                self.packet_data[size]["ipa_std"] = 0
                self.packet_data[size]["ipa_q1"] = 0
                self.packet_data[size]["ipa_median"] = 0
                self.packet_data[size]["ipa_q3"] = 0

    def output_to_fsdb(self, out_file_handle):
        import pyfsdb

        outh = pyfsdb.Fsdb(out_file_handle=out_file_handle)
        outh.out_column_names = ["key"] + self.all_keys

        for data_key in self.packet_data:
            outh.append(
                [data_key] + [self.packet_data[data_key][x] for x in self.all_keys]
            )
        outh.close()
