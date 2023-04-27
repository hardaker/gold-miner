import sys
import json

from apropos.goldmine.output.goldOutput import GoldOutput


class GoldJson(GoldOutput):
    "Outputs results in a list of json dictionaries."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.as_percentage = kwargs.get("as_percentage", False)
        self.raw_values = kwargs.get("raw_values", False)
        self.out_file = kwargs.get("output_file")
        self.as_list = kwargs.get("as_list")
        self.flatten = kwargs.get("flatten", False)
        self.notfirst = False

        self.out_file_handle = sys.stdout
        if self.out_file:
            self.out_file_handle = open(self.out_file, "w")

        if self.as_list:
            self.out_file_handle.write("[")

    def maybe_comma(self):
        if self.as_list and self.notfirst:
            self.out_file_handle.write(",")
        else:
            self.notfirst = True
        self.out_file_handle.write("\n")

    def output(self, analysis_results, packet_number, tunnel_count, subscriptions):
        out_row = []
        for row in analysis_results:
            (timestamp, spi, label, value, packets) = row
            if not self.raw_values:
                value = self.calculate_confidence(label, value)

            output_struct = {
                "timestamp": float(timestamp),
                "identifiers": spi,
                "label": label,
                "value": float(value),
                "packets": int(packets),
            }

            if self.flatten:
                self.maybe_comma()
                json.dump(output_struct, self.out_file_handle)
            else:
                out_row.append(output_struct)

        if not self.flatten:
            self.maybe_comma()
            json.dump(out_row, self.out_file_handle)

    def close(self):
        if self.as_list:
            self.out_file_handle.write("\n]\n")
        self.out_file_handle.close()
