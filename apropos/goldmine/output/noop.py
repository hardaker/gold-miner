from logging import debug, warning
import collections
import pyfsdb

from apropos.goldmine.output.goldOutput import GoldOutput


class GoldNoOp(GoldOutput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def output(self, analysis_results, packet_number, tunnel_count, subscriptions):
        pass
