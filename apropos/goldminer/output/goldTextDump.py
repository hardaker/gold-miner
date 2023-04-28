from apropos.goldminer.output.goldOutput import GoldOutput


class GoldTextDump(GoldOutput):
    def __init__(self, seperator="\n"):
        self.seperator = seperator

    def output(self, analysis_results, packet_number, tunnel_count, subscriptions):
        outputs = []
        strformat = "n={}\tt={}\tspi={}\ttoken={}:\t{}"
        outputs = [
            strformat.format(z, v, w, x, y) for (v, w, x, y, z) in analysis_results
        ]
        output = self.seperator.join(outputs)
        print(output, end=self.seperator)
