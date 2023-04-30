from collections import Counter, defaultdict
from logging import debug, info, warning, error, critical
import dpkt
import numpy as np
import time
import pyfsdb
import pprint
from apropos.goldminer.output.noop import GoldNoOp

#
# Analyzer
#
last_packet_time = {}


class PickAxe:
    def __init__(
        self,
        gold_profiles: list = [],
        training_data_file: str = None,
        training_key: str = "e_pkt_len",
        support_windowing: bool = False,
        threshold_file=None,
        algorithm="comparison",
        label_map=None,
        report_every_n=None,
        three_tuple_only=False,
    ):

        # dictionary of combinations to search for
        #   each entry is a sub-dict with gold/dirty names with accumulated protocol information
        self.gold_mines = {}
        self._gold_profiles = gold_profiles
        self._training_data_file = training_data_file
        self.training_key = training_key
        self.threshold_file = threshold_file
        self._label_map = label_map
        self.skip_packets = 0
        self.missing_in_profile_penalty = 1.0  # TODO: configurable
        self.missing_in_tunnel_penalty = 1.0  # TODO: configurable
        self._output = GoldNoOp()
        self.report_every_n = report_every_n
        self.three_tuple_only = three_tuple_only

        # A queue and server for us when connected to a GRPC server
        self.server = None
        self.subscriptions = {}
        self.packet_count = 0
        self.tunnels = defaultdict(dict)

        self._outputs = None
        self.all_keys = []

        # starting keep length
        self.starting_length = 30000

        if self.gold_profiles:
            self.read_percents()

        # create a (sparse) counting map
        self.maximum_identifiers = 200
        self.identifier_indexes = {}
        # we use 1550 just to account for some labeling that gets bigger than 1500
        self.support_windowing = support_windowing
        self.size_array = None
        if self.support_windowing:
            # TODO need to deal with reallocating this
            self.size_array = np.zeros(
                (self.maximum_identifiers, 1550, self.starting_length), dtype=bool
            )
        self.tunnel_packets = Counter()

        # remember the algorithm functions
        self._algorithms = {
            "lms": self.distance_by_lms,
            "linear": self.distance_by_linear,
            "comparison-wide": self.distance_by_dirty_comparison,
            "comparison": self.distance_by_dirty_comparison2,
        }
        self.calculate_distance = self.distance_by_dirty_comparison
        self.algorithm = algorithm

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        self._output = value

    @property
    def gold_profiles(self):
        return self._gold_profiles

    @gold_profiles.setter
    def gold_profiles(self, value):
        self._gold_profiles = value
        self.read_percents()

    @property
    def algorithm(self):
        "The current algorithm to be used when processing data"
        for key in self._algorithms:
            if self._algorithms[key] == self.calculate_distance:
                return key
        error("no algorithm set")
        return "unknown"

    @algorithm.setter
    def algorithm(self, value):
        "Set the current algorithm to be used when processing data"
        if value not in self._algorithms:
            error(f"unknown algorithm passed to {self}: {value}")
            raise ValueError(f"unknown algorithm: {value}")
        self.calculate_distance = self._algorithms[value]

    @property
    def algorithms(self):
        "The algorithms available to be used"
        return list(self._algorithms.keys())

    @property
    def label_map(self):
        return self._label_map

    @label_map.setter
    def label_map(self, newval):
        self._label_map = newval

    @property
    def training_data_file(self):
        "The training data file being used"
        return self._training_data_file

    @training_data_file.setter
    def training_data_file(self, value):
        "The training data file to use"
        self._training_data_file = value
        self.read_percents()

    def process_pcap(
        self,
        pcap_file: str,
        pkt_filter: str = None,
        max_packets: int = 0,
        search_window_length: int = 0,
        dig_for_gold: bool = True,
        skip_packets: int = 0,
    ) -> None:

        self.skip_packets = skip_packets
        pkt_count = max_packets + self.skip_packets
        info(
            f"ANALYZING: {pcap_file} with filter={pkt_filter} max={max_packets} skip={skip_packets}"
        )

        # open the pcap file
        pcap = dpkt.pcap.Reader(open(pcap_file, "rb"))

        # optionally set the filter
        if pkt_filter:
            pcap.setfilter(pkt_filter)

        pcap.dispatch(pkt_count, self.analyze_packet)

        return (self.identifier_indexes, self.tunnel_packets, self.size_array)

    def process_interface(self, interface: str, packet_filter: str = None):

        debug(f"  sniffing({interface})")
        sniff(prn=self.analyze_packet, iface=interface, filter=packet_filter, store=0)

    def find_count_for_time(
        self, array: list, since_timestamp: int, max_len: int, pkt_size: int
    ) -> int:
        """Find the count number of entries in an array of recorded timestamps
        for each packet size since a *since_timestamp* timestamp.

        TODO needs rethinking:
        If since_timestamp is a dictionary, we use the size as an index to
        search instead for different time lengths per size.

        TODO: this could be sped up (if nothing else, remember the point of the last time found)
        """
        if isinstance(since_timestamp, dict):
            timestamp = since_timestamp.get(pkt_size, 2147483647)
            count = max_len - array[:max_len].searchsorted(timestamp)
        else:
            count = max_len - array[:max_len].searchsorted(since_timestamp)
        return count

    def read_percents(self):
        filename = self.training_data_file
        all_gold_keys = self.gold_profiles

        fh = pyfsdb.Fsdb(filename, return_type=pyfsdb.RETURN_AS_DICTIONARY)

        # all data from the percentage file
        all_data = []

        column_names = fh.column_names

        if all_gold_keys == []:
            # assume they want all gold
            all_gold_keys = [x for x in column_names if x != self.training_key]
            self.gold_profiles = all_gold_keys
            debug(f"assuming all keys: {self.gold_profiles}")

        # reset
        self.gold_mines = {}

        # if we weren't passed dirty keys, create them
        have_dirty = True
        if len(self.all_keys) == 0:
            have_dirty = False

        # load all the TRAINING data into an array
        all_data = fh.get_all()

        # for each gold profile, build a list
        for gold_profile in all_gold_keys:
            # load all the good data into self.gold_percents per key
            self.gold_percents = {}

            # the list of keys we want to find
            gold_keys = gold_profile.split(",")

            # the list of OTHER columns in the data
            dirty_keys = []

            # for every column name, place it in a gold list or dirty list of keys
            for column in column_names:
                if column in gold_keys:
                    self.gold_percents[column] = {}
                elif not have_dirty and column != self.training_key:
                    dirty_keys.append(column)
                elif have_dirty and column in self.all_keys:
                    dirty_keys.append(column)

            # load all the dirty data as an average into percents
            percents = {}

            # loop through all data and place it in
            for row in all_data:
                try:
                    size = int(row[self.training_key])
                except Exception:
                    error(
                        f"failed to parse this training key as an integer: '{row[self.training_key]}'"
                    )
                    continue  # failed to parse to an int -- ignore this

                # collect the gold key values first
                gold_max = -1
                gold_min = 1000
                for key in gold_keys:
                    try:
                        value = float(row[key])
                    except Exception:
                        value = 0.0

                    if key not in self.gold_percents:
                        error(f"gold profile '{key}' not found in data")
                        continue

                    self.gold_percents[key][size] = value

                    gold_max = max(self.gold_percents[key][size], gold_max)
                    gold_min = min(self.gold_percents[key][size], gold_min)

                if gold_max == 0.0 and gold_min == 0.0:
                    continue

                # TODO: deal with len(self.gold_percents[key].values())  == 0
                # how do we decrease the probability of gold given other things?  or do we?
                # probably don't need to, as we assume other things in the stream is ok

                # TODO: we're not handling multiple AND/OR golds right now - just averaging
                gold_value = (gold_max - gold_min) / 2 + gold_min

                # now collect the min/max above the measured gold_min/max
                dirty_max = -1
                dirty_min = 10000
                dirty_range_max = 10000
                dirty_range_min = -1

                for key in dirty_keys:
                    try:
                        value = float(row[key])

                        # XXX TODO FIX: should be min/max nearest gold value

                        if value >= gold_value:
                            # take the lowest value above the gold value
                            # thus dirty_max is the min [sic] above gold
                            dirty_range_max = min(value, dirty_range_max)

                        if value <= gold_value:
                            # take the highest value above the gold value
                            # thus dirty_max is the max [sic] above gold
                            dirty_range_min = max(value, dirty_range_min)

                        dirty_max = max(value, dirty_max)
                        dirty_min = min(value, dirty_min)
                    except Exception:
                        pass  # value was not a float (likely '' or '-')

                # remember our dirty high/low values and the gold_value per size
                percents[size] = (
                    dirty_min,
                    gold_value,
                    dirty_max,
                    dirty_range_max,
                    dirty_range_min,
                )

                debug(
                    f"sz={size}: %s={percents[size]}  (max={gold_max}, min={gold_min})"
                )

            # we're done build the trained results for this profile
            self.gold_mines[gold_profile] = percents

            debug("gold mines:")
            debug(pprint.pformat(self.gold_mines))

    def calculate_distance(
        self,
        measured,
        dirty_min,
        gold_value,
        dirty_max,
        dirty_range_max,
        dirty_range_min,
    ):
        raise ValueError("algorithm unset")

    def distance_by_lms(
        self,
        measured,
        dirty_min,
        gold_value,
        dirty_max,
        dirty_range_max,
        dirty_range_min,
    ):
        diff = measured - gold_value
        return diff * diff

    def distance_by_linear(
        self,
        measured,
        dirty_min,
        gold_value,
        dirty_max,
        dirty_range_max,
        dirty_range_min,
    ):
        return abs(measured - gold_value)

    def distance_by_dirty_comparison(
        self,
        measured,
        dirty_min,
        gold_value,
        dirty_max,
        dirty_range_max,
        dirty_range_min,
    ):
        """Determine how far away a measured value is between the target gold
        and the nearest dirty marker(s).  Positive values are
        considered better.
        """
        difference = None
        if dirty_min == 10000 or dirty_max == -1:
            # TODO: return N/N+1 instead
            # (to accomplish this we need to remember N, which we don't yet)
            difference = 1  # no dirty records for this point .
            if not (dirty_min == 10000 and dirty_max == -1):
                error("bad math -- min/max are not both extreme indicating missing")
        elif measured < dirty_min:
            if gold_value < dirty_min:
                if measured < gold_value:
                    # measured < gold < dirty_min
                    difference = 1
                else:
                    # gold < measured < dirty_min
                    # return fraction of distance from measured to dirty
                    # (w / 1 being better)
                    difference = (dirty_min - measured) / (dirty_min - gold_value)
            else:
                # measured < dirty_min and gold > dirty_min
                difference = 0
        elif measured > dirty_max:
            if gold_value > dirty_max:
                if measured > gold_value:
                    # measured > gold > dirty_max
                    difference = 1
                else:
                    # gold > measured > dirty_max
                    # result = fraction of distance from dirty to measured
                    difference = (measured - dirty_max) / (gold_value - dirty_max)
            else:
                if measured > gold_value:  ## TODO: wrong -- gold < max here
                    # measured > gold > max
                    difference = 0
                else:
                    # gold > measured > max
                    difference = (dirty_max - measured) / (dirty_max - gold_value)
                    # measured > max
        else:
            # dirty_min < measured < dirty_max
            if gold_value < dirty_min or gold_value > dirty_max:
                difference = 0
            elif gold_value > measured:
                # min < measured < gold < max
                # return fraction of distance close to min from measured
                difference = (measured - dirty_min) / (gold_value - dirty_min)
            elif dirty_max == gold_value:
                # div/0 error if we did the below, so return 0 (not good)
                return 0
            else:
                # min < gold < measured < max
                # return fraction of distance close to max from measured
                difference = (dirty_max - measured) / (dirty_max - gold_value)

        if difference is None:
            error("OH NOOOOOOOOOOOOOOOOOOOO - empty result means we missed a case")
            error(
                f"r={difference}, gv={gold_value}, dmin={dirty_min}, dmax={dirty_max}, m={measured}"
            )
            difference = 0.5

        return 1 - difference  # we want 0 is better, so invert this

    def distance_by_dirty_comparison2(
        self,
        measured,
        dirty_min,
        gold_value,
        dirty_max,
        dirty_range_max,
        dirty_range_min,
    ):
        """Determine how far away a measured value is between the target gold
        and the nearest dirty marker(s).  Positive values are
        considered better.
        """
        dirty_min = dirty_range_min
        dirty_max = dirty_range_max

        difference = None
        if dirty_min == 10000 or dirty_max == -1:
            # TODO: return N/N+1 instead
            # (to accomplish this we need to remember N, which we don't yet)
            difference = 1  # no dirty records for this point .
            if not (dirty_min == 10000 and dirty_max == -1):
                error("bad math -- min/max are not both extreme indicating missing")
        elif measured < dirty_min:
            if gold_value < dirty_min:
                if measured < gold_value:
                    # measured < gold < dirty_min
                    difference = 1
                else:
                    # gold < measured < dirty_min
                    # return fraction of distance from measured to dirty
                    # (w / 1 being better)
                    difference = (dirty_min - measured) / (dirty_min - gold_value)
            else:
                # measured < dirty_min and gold > dirty_min
                difference = 0
        elif measured > dirty_max:
            if gold_value > dirty_max:
                if measured > gold_value:
                    # measured > gold > dirty_max
                    difference = 1
                else:
                    # gold > measured > dirty_max
                    # result = fraction of distance from dirty to measured
                    difference = (measured - dirty_max) / (gold_value - dirty_max)
            else:
                if measured > gold_value:  ## TODO: wrong -- gold < max here
                    # measured > gold > max
                    difference = 0
                else:
                    # gold > measured > max
                    difference = (dirty_max - measured) / (dirty_max - gold_value)
                    # measured > max
        else:
            # dirty_min < measured < dirty_max
            if gold_value < dirty_min or gold_value > dirty_max:
                difference = 0
            elif gold_value > measured:
                # min < measured < gold < max
                # return fraction of distance close to min from measured
                difference = (measured - dirty_min) / (gold_value - dirty_min)
            elif dirty_max == gold_value:
                # div/0 error if we did the below, so return 0 (not good)
                return 0
            else:
                # min < gold < measured < max
                # return fraction of distance close to max from measured
                difference = (dirty_max - measured) / (dirty_max - gold_value)

        if difference is None:
            error("OH NOOOOOOOOOOOOOOOOOOOO - empty result means we missed a case")
            error(
                f"r={difference}, gv={gold_value}, dmin={dirty_min}, dmax={dirty_max}, m={measured}"
            )
            difference = 0.5

        return 1 - difference  # we want 0 is better, so invert this

    def dig_4it(self, timestamp: int, window_length: int = 0, identifier=None) -> None:
        """Given a sequence of packets in various sizes, determine if anything
        is one of the hopeful packet types given their feature counts."""
        output_results = {}
        debug("----")

        beginning_timestamp = 0
        if window_length:
            if isinstance(window_length, dict):
                beginning_timestamp = window_length
            else:
                beginning_timestamp = float(timestamp) - window_length

        tunnel_list = self.tunnels

        # ignore all other tunnels but the ones marked by a passed identifier
        if identifier:
            tunnel_list = [identifier]

        # examine each tunnel we've seen or was requested to study
        for identifier in tunnel_list:

            # calculate the total number of packets seen from all tunnels
            tunnel = self.tunnels[identifier]
            tunnel_packets = self.tunnel_packets[identifier]

            # loops over the entire set of seen packets to date by pkt_size
            # mine == named search key
            for protocol_label in self.gold_mines:
                training_percents = self.gold_mines[protocol_label]
                difference_total = 0.0
                number_of_sizes = 0

                # for every protocol we are searching for,
                # evaluate it for this tunnel's packet sizes
                for pkt_size in tunnel:
                    number_of_sizes += 1

                    if pkt_size not in training_percents:
                        # since this packet size has never been seen in
                        # our target "gold" protocol, it's a sign it may
                        # be something different.  Punish it accordingly.
                        difference_total += self.missing_in_profile_penalty
                        # debug(f"unknown packet size seen: {pkt_size}")
                        continue  # skip the rest of the calculations

                    # the current percentage seen for this size
                    # measured = tunnel[pkt_size]['length'] / identifier_packets
                    measured = (
                        # TODO: this complexity isn't needed unless
                        # windowing is used should be able to just
                        # take the total length all the time for
                        # never-ending
                        self.find_count_for_time(
                            tunnel[pkt_size]["times"],
                            beginning_timestamp,
                            tunnel[pkt_size]["length"],
                            pkt_size,
                        )
                        / tunnel_packets
                    )

                    # determine the case we're measuring against,
                    # if we're the bottom, top or middle of prior measurements
                    (
                        dirty_min,
                        gold_value,
                        dirty_max,
                        dirty_range_max,
                        dirty_range_min,
                    ) = training_percents[pkt_size]

                    # debug(f"calculating '{mine}' distance: ")
                    # debug(f"  {measured}")
                    # debug(f"  {gold_value}")
                    # debug(f"  {dirty_min}")
                    # debug(f"  {dirty_max}")
                    difference = self.calculate_distance(
                        measured,
                        dirty_min,
                        gold_value,
                        dirty_max,
                        dirty_range_max,
                        dirty_range_min,
                    )

                    difference_total += difference
                    debug(
                        f"sz={pkt_size}\tm={measured}, percents={training_percents[pkt_size]}\t result: {difference}"
                    )
                    # debug(f"# {spi}\t{seen}\t{signal_importance}\t{deviation}")

                    # XXX: scale result by delta from 0 or from top other
                    # expected signal?

                    # msg = "  {} = seen={}, gold={}, dirt={}, rslt={}"
                    # debug(msg.format(seen,
                    #                  seen_percentage,
                    #                  gold_percent,
                    #                  dirty_percent,
                    #                  result))
                    # msg = "    signal={}, deviation={}"
                    # debug(msg.format(signal_importance, deviation))

                # record the result achieved for this tunnel
                if number_of_sizes > 0:
                    if self.missing_in_tunnel_penalty is not None and len(tunnel) < len(
                        training_percents
                    ):
                        delta = self.missing_in_tunnel_penalty * (
                            len(training_percents) - len(tunnel)
                        )
                        difference_total += delta
                        number_of_sizes += delta
                    average_difference = 1 - (difference_total / number_of_sizes)
                    debug(
                        f"diff total: {protocol_label} {difference_total} / {number_of_sizes} = {average_difference}"
                    )

                    label = protocol_label
                    relabelled = label
                    if self.label_map and protocol_label in self.label_map:
                        relabelled = self.label_map[protocol_label]

                    # only add it if the new confidence is better than the old
                    if (
                        relabelled in output_results
                        and output_results[relabelled][4] < average_difference
                    ):
                        output_results[relabelled] = (
                            timestamp,
                            identifier,
                            relabelled,
                            average_difference,
                            tunnel_packets,
                        )
                    else:
                        output_results[relabelled] = (
                            timestamp,
                            identifier,
                            relabelled,
                            average_difference,
                            tunnel_packets,
                        )

            # transform the dict results into an array
            output_results = [output_results[x] for x in output_results]

            # output this set of results for this packet for all tunnels
            self.output.output(
                output_results, self.packet_count, len(self.tunnels), self.subscriptions
            )
            output_results = []

        # mark that we're done with a single multi-mine-output
        self.output.end_section()

    def get_packet_identifier(self, pkt):
        identifier = None
        try:
            identifier = (pkt.proto, pkt["IP"].src, pkt["IP"].dst, pkt.spi)
        except Exception:
            pass

        if not identifier:
            if not self.three_tuple_only:
                try:
                    identifier = (
                        pkt.proto,
                        pkt["IP"].src,
                        pkt["IP"].dst,
                        pkt.sport,
                        pkt.dport,
                    )
                except Exception:
                    pass

        if not identifier:
            try:
                identifier = (pkt.proto, pkt["IP"].src, pkt["IP"].dst)
            except Exception:
                identifier = "none"

        return identifier

    def get_dpkt_packet_identifier(self, ip):
        identifier = None

        # ipsec
        if ip.p == 50:
            return (ip.p, "{}.{}.{}.{}".format(*ip.src), "{}.{}.{}.{}".format(*ip.dst))

        if self.three_tuple_only:
            return (ip.p, "{}.{}.{}.{}".format(*ip.src), "{}.{}.{}.{}".format(*ip.dst))

        # udp
        if ip.p == 6 or ip.p == 17:
            udp_tcp = ip.data
            return (
                ip.p,
                "{}.{}.{}.{}".format(*ip.src),
                "{}.{}.{}.{}".format(*ip.dst),
                udp_tcp.sport,
                udp_tcp.dport,
            )

        return (ip.p, "{}.{}.{}.{}".format(*ip.src), "{}.{}.{}.{}".format(*ip.dst))

    def analyze_packet(
        self,
        timestamp,
        pkt,
        window_length: int = 0,
        dig_for_gold: bool = True,
    ) -> None:
        """Analyzes a packet to update the internal model about
        whether its potentially a golden egg and should be prioritized."""

        if self.skip_packets > 0:
            self.skip_packets -= 1
            return

        # get the  headers
        eth = dpkt.ethernet.Ethernet(pkt)
        ip = eth.data
        if not isinstance(ip, dpkt.ip.IP):
            return

        # count the number of packets per SPI
        identifier = self.get_dpkt_packet_identifier(ip)

        # get a unique integer of this index
        if identifier not in self.identifier_indexes:
            self.identifier_indexes[identifier] = len(self.identifier_indexes)
        identifier_index = self.identifier_indexes[identifier]

        pkt_len = len(ip)

        # TODO: this sparse storage is inefficient
        if self.support_windowing:
            self.size_array[
                identifier_index, pkt_len, self.tunnel_packets[identifier]
            ] = True

        # count the total number of packets seen for this identifier
        self.tunnel_packets[identifier] += 1

        # if isinstance(spi, tuple):
        #     spi = "/".join(spi)

        if pkt_len not in self.tunnels[identifier]:
            self.tunnels[identifier][pkt_len] = {
                "length": 0,
                "max_length": self.starting_length,
                "times": np.empty(self.starting_length),
            }

        if self.support_windowing:
            tunnel_size_data = self.tunnels[identifier][pkt_len]
            # spi, length, 'times' is an array of times up to its length 'length' index
            if tunnel_size_data["length"] >= tunnel_size_data["max_length"]:
                warning(
                    f"extending {identifier} array size to {tunnel_size_data['max_length']*2}"
                )
                tunnel_size_data["times"] = np.hstack(
                    [
                        tunnel_size_data["times"],
                        np.empty(tunnel_size_data["max_length"]),
                    ]
                )
                tunnel_size_data["max_length"] *= 2

            # record the required information for this packet
            tunnel_size_data["times"][tunnel_size_data["length"]] = timestamp
            tunnel_size_data["length"] += 1

        # memorize the last time we see a packet for a given identifier
        last_packet_time[identifier] = timestamp

        # and count the total number of packets
        self.packet_count += 1

        # pass to the main search engine
        if dig_for_gold:
            if (
                self.report_every_n
                and self.tunnel_packets[identifier] % self.report_every_n != 0
            ):
                return
            self.dig_4it(timestamp, window_length, identifier)

    def window_analysis(self):
        # array is:  identifier_number, pkt_size, pkt_sequence_number
        import sys

        oh = pyfsdb.Fsdb(out_file_handle=sys.stdout)
        oh.out_column_names = [
            "label",
            "identifier_num",
            "identifier",
            "window_size",
            "confidence",
        ]

        for mine in self.gold_mines:
            training_percents = self.gold_mines[mine]
            for identifier in self.identifier_indexes:
                identifier_num = self.identifier_indexes[identifier]
                tunnel_pkts = self.tunnel_packets[identifier]

                window_sizes = range(10, max(10000, tunnel_pkts), 10)
                for size in window_sizes:
                    difference = 0.0
                    windows_considered = 0

                    # start rolling the window every 5 packets until the end
                    for offset in range(0, tunnel_pkts - size, 5):

                        # calculate the confidence per packet size
                        for pkt_size in range(1, 1540):
                            if pkt_size not in training_percents:
                                continue
                            windows_considered += (
                                1  # deal with pkt sizes with no training data
                            )

                            (
                                dirty_min,
                                gold_value,
                                dirty_max,
                                dirty_range_max,
                                dirty_range_min,
                            ) = training_percents[pkt_size]

                            # XXX: slide the window
                            window_count = self.size_array[
                                identifier_num, pkt_size, offset : size + offset
                            ].sum()
                            pkt_size_fraction = window_count / size

                            difference += self.calculate_distance(
                                pkt_size_fraction,
                                dirty_min,
                                gold_value,
                                dirty_max,
                                dirty_range_max,
                                dirty_range_min,
                            )

                    debug(f"{windows_considered} for {identifier}")
                    if windows_considered == 0:
                        continue
                    difference = difference / windows_considered

                    oh.append([mine, identifier_num, identifier, size, difference])

                # for size in window_sizes:

    def close(self):
        self.output.close()

    def swallow_output(self):
        pass
