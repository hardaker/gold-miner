from logging import warning, debug, info

from apropos.goldmine.output.goldOutput import GoldOutput


class GoldHighLowWatermark(GoldOutput):
    """Truncates an output generator to just when values pass a high/low
    watermark.  When an incoming value goes beyond the *high* mark, a
    (single) report is made.  When the value drops below the *low*
    mark afterward, another report is made indicating it dropped below
    again.  All other reports are suppressed, indicating the last
    reported state is still current.

    The *output* option is required and must point to a GoldOutput instance
    of some kind.

    Note that outputs with more than one result will be tracked one at
    a time, with each identifier indicating a separate reporting
    system.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.high = kwargs.get("high", 0.0)
        self.low = kwargs.get("low", 1.0)
        self._output = kwargs.get("output")
        self.reported = {}

        if not self._output:
            raise ValueError("the output option is required for GoldHighLowWatermark")

    def output(self, analysis_results, packet_number, tunnel_count, subscriptions):
        for row in analysis_results:
            identifier = row[1]
            value = row[3]
            if identifier not in self.reported:
                self.reported[identifier] = False
            if not self.reported[identifier] and value >= self.high:
                self._output.output([row], packet_number, tunnel_count, subscriptions)
                self.reported[identifier] = True
            elif self.reported[identifier] and value < self.low:
                self._output.output([row], packet_number, tunnel_count, subscriptions)
                self.reported[identifier] = False

    def close(self):
        self._output.close()

    def end_section(self):
        self._output.end_section()

    def append(self, data):
        self._output.append(data)

    def calculate_confidence(self, label, value):
        return self._output.calculate_confidence(label, value)
