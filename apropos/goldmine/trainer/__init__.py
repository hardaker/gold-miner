import sys
import collections
from logging import debug, info, warning, error, critical
import dpkt


class GoldMineBase:
    def __init__(self, do_timing_analysis=True, addresses=None):
        self.address_filters = addresses
        self.reset()

    def reset(self):
        self.n = -1  # since we increment immediately, start at -1 to get to zero
        self.last_size = 0

    def analyze(self, timestamp, packet):
        # discard non-ips
        try:
            self.n += 1

            eth = dpkt.ethernet.Ethernet(packet)
            ip = eth.data
            if not isinstance(ip, dpkt.ip.IP):
                warning("A non-IP packet was received")

            # ignore things out of the address block we want to inspect
            if self.address_filters:
                for address in self.address_filters:
                    if "{}.{}.{}.{}".format(*ip.src).startswith(address):
                        break
                else:
                    return  # skip this packet

            self.analyze_packet(timestamp, ip, self.last_size + self.n)
            self.last_size += self.n + 1

        except Exception:
            warning(f"packet #{self.n} could not be parsed")

    def analyze_files(self, pcap_files: list, count: int = 0, pkt_filter: str = None):
        self.reset()
        for n, pcap_file in enumerate(pcap_files):
            info(f"ANALYZING: {pcap_file} with {pkt_filter=} {count=}")

            # open the pcap file
            pcap = dpkt.pcap.Reader(open(pcap_file, "rb"))

            # optionally set the filter
            if pkt_filter:
                pcap.setfilter(pkt_filter)

            pcap.dispatch(0, self.analyze)


class GoldMineTrainer(GoldMineBase):
    def __init__(self, do_timing_analysis=True, addresses=None):
        super().__init__(addresses)
        self.packet_data = collections.defaultdict(collections.Counter)
        self.timing_keys = ["timing_mean", "timing_max", "timing_median", "timing_std"]
        self.ipa_keys = [
            "ipa_mean",
            "ipa_median",
            "ipa_q1",
            "ipa_q3",
            "ipa_min",
            "ipa_max",
            "ipa_std",
        ]
        self.first_packet_time = None
        self.last_packet_time = None
        self.packet_size_delays = {}
        self.packet_size_timestamps = {}
        self.do_timing_analysis = do_timing_analysis

        # create the data keys to use
        if do_timing_analysis:
            self.packet_keys = ["ipa_time", "size_count"]
        else:
            self.packet_keys = ["size_count"]
        self.percent_keys = ["percent_" + x for x in self.packet_keys]  # transform

        self.all_keys = self.packet_keys + self.percent_keys
        if do_timing_analysis:
            self.all_keys += self.timing_keys + self.ipa_keys

    def analyze_packet(self, timestamp, packet, count):
        """Analyzes a packet to pull out features."""
        global last_packet_time
        global first_packet_time

        # get the length
        packet_len = len(packet)

        # count the packet sizes
        self.packet_data[packet_len]["size_count"] += 1

        if self.do_timing_analysis:
            # calculate the time since the last packet
            # (this turns out to be pretty much always 0)
            this_time = timestamp
            if self.last_packet_time:
                self.packet_data[int(this_time - self.last_packet_time)][
                    "ipa_time"
                ] += 1

            # remember this timestamp
            self.last_packet_time = this_time

            # create a list of real times since this last *size* was seen
            if not self.first_packet_time:
                self.first_packet_time = this_time

            if len(packet) not in self.packet_size_delays:
                self.packet_size_delays[packet_len] = [0.0]
                self.packet_size_timestamps[packet_len] = [this_time]
            else:
                self.packet_size_delays[packet_len].append(
                    float(this_time - self.first_packet_time)
                )
                self.packet_size_timestamps[packet_len].append(this_time)

            self.first_packet_time = this_time

    def generate_results(self):
        """Normalize the counts to fractions"""
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

    @property
    def results(self):
        data = []
        for data_key in self.packet_data:
            data.append(
                [data_key] + [self.packet_data[data_key][x] for x in self.all_keys]
            )
        return data
