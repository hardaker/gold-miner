import logging


class GoldOutput:
    def __init__(self, **kwargs):
        self.trained_parameters = {}

        if "parameter_file" in kwargs and kwargs["parameter_file"]:
            import pyfsdb

            f = pyfsdb.Fsdb(
                kwargs["parameter_file"],
                return_type=pyfsdb.RETURN_AS_DICTIONARY,
                converters={"low_val": float, "high_val": float},
            )
            for row in f:
                self.trained_parameters[row["key"]] = [row["low_val"], row["high_val"]]
                logging.debug(self.trained_parameters)
        else:
            # logging.warning(f"No parameter file passed to {self}")
            pass

    def calculate_confidence(self, label, value):
        try:
            (specific_low, specific_high) = self.trained_parameters.get(
                label, [0.0, 1.0]
            )
            fraction = max(
                min((value - specific_low) / (specific_high - specific_low), 1.0), 0.0
            )
        except Exception as e:
            logging.error(f"failed confidence gathering: {e}")
            return -1

        return fraction

    def close(self):
        pass

    def end_section(self):
        pass

    def append(self, data):
        pass
