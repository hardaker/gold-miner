from logging import debug, warning
import collections
import pyfsdb

from apropos.goldmine.output.goldOutput import GoldOutput


class GoldFsdb(GoldOutput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.as_percentage = kwargs.get("as_percentage", False)
        self.raw_values = kwargs.get("raw_values", False)
        self._save_values = kwargs.get("save_values", None)

        # delete keys we can't pass onward to FSDB
        for key in ["as_percentage", "save_values", "raw_values", "parameter_file"]:
            if key in kwargs:
                del kwargs[key]

        self.outh = pyfsdb.Fsdb(**kwargs)
        self.outh.out_column_names = [
            "timestamp",
            "identifier",
            "token",
            "confidence",
            "total",
        ]

        if self._save_values:
            self._save_values_storage = collections.defaultdict(dict)

    def output(self, analysis_results, packet_number, tunnel_count, subscriptions):
        for row in analysis_results:
            (timestamp, identifier, label, value, packets) = row
            if not self.raw_values:
                value = self.calculate_confidence(label, value)
            self.outh.append([timestamp, identifier, label, value, packets])

            # save the last label seen
            # TODO: save min/max/avg/binned/etc?
            if self._save_values:
                self._save_values_storage[identifier][label] = value

    @property
    def save_values(self):
        return self._save_values_storage

    def close(self):
        self.outh.close()
