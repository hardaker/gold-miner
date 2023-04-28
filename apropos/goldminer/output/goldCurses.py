import curses

from apropos.goldminer.output.goldOutput import GoldOutput


class GoldCurses(GoldOutput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.win = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_WHITE)

        self.win.move(0, 1)
        self.win.addstr("spi")

        self.win.move(0, 12)
        self.win.addstr("pkts")

        self.win.move(0, 20)
        self.win.addstr("label")

        self.win.move(0, 30)
        self.win.addstr("confidence")

        # XXX hard coded
        self.bar_length = 20
        self.as_percentage = kwargs.get("as_percentage")

    def close(self):
        import time

        time.sleep(1)
        curses.endwin()

    def output(self, analysis_results, packet_number, tunnel_count, subscriptions):
        lastspi = ""
        for n0, output in enumerate(analysis_results):
            (timestamp, spi, label, value, packets) = output

            n = n0 + 1
            g = n0 + 23

            # plot the label
            # XXX: only need to do this once really
            if spi != lastspi:
                lastspi = spi
                try:
                    spi = hex(spi)
                except Exception:
                    spi = "None"

                self.win.move(n, 1)
                self.win.addstr(spi)

                self.win.move(n, 12)
                self.win.addstr(str(packets))

            self.win.move(n, 20)
            self.win.addstr(label[-9:])

            # calculate the fraction of traffic
            # import sys
            # sys.stderr.write(label + "\n")
            if label not in self.trained_parameters:
                self.win.move(g, 1)
                self.win.addstr("Failed to find parameters for {}".format(label))
            else:
                self.win.move(g, 1)
                self.win.addstr(
                    "Gold: {} : {} - {}".format(label, *self.trained_parameters[label])
                )

            # turn the result value into a confidence score
            fraction = self.calculate_confidence(label, value)

            # plot the raw value
            self.win.move(n, 30)
            if self.as_percentage:
                self.win.addstr(str(int(100.0 * fraction)) + "   ")
            else:
                self.win.addstr(str(value)[0:23])

            # plot the bar
            self.win.move(n, 55)

            color = 2
            if fraction < 0.25:
                color = 1
            elif fraction > 0.75:
                color = 3

            left_count = int(self.bar_length * fraction)
            right_count = self.bar_length - left_count

            self.win.addstr(
                ("=" * left_count) + ("_" * right_count), curses.color_pair(color)
            )

            # self.win.addstr(str(left_count))

        self.win.move(20, 1)
        self.win.addstr(f"Packets seen: {packet_number}")
        self.win.move(21, 1)
        self.win.addstr(f"Tunnels seen: {tunnel_count}")
        self.win.move(22, 1)
        self.win.addstr("Outputs seen: {}".format(len(analysis_results)))

        self.win.refresh()
