import unittest


class TestPickAxeMath(unittest.TestCase):
    def test_difference_function(self):
        from apropos.goldminer.pickaxe.pickaxe import PickAxe

        a = PickAxe()

        # measured, dirty_min, gold_value, dirty_max, expected
        test_cases = [
            [0.2, 0.4, 0.3, 0.8, 0.0],  # measured < gold < min < max
            [0.8, 0.1, 0.7, 0.6, 0.0],  # min < max < gold < measured
            # gold(.4) < measured(.5) < min(.8) < max(.9) = (.8-.5)/(.8-.4) = .75
            [0.5, 0.8, 0.4, 0.9, 0.25],
            # gold(.6) > measured(.5) > max(.2) > min(.1) = (.8-.5)/(.8-.4) = .75
            [0.5, 0.1, 0.6, 0.2, 0.25],
            #
            # measured is above max and gold is below
            # min(.1) < gold(.4) < max(.8) < measured(.9)
            [0.9, 0.1, 0.4, 0.8, 1.0],
            # gold(.1) < min(.2) <  < max(.8) < measured(.9)
            [0.9, 0.2, 0.1, 0.8, 1.0],
            #
            # measured is below min and gold above
            # measured(.1) < min(.2) < gold(.4) < max(.8)
            [0.1, 0.2, 0.4, 0.8, 1.0],
            # measured(.1) < min(.2) < max(.8) < gold(.9)
            [0.1, 0.2, 0.9, 0.8, 1.0],
            #
            # measured between min and gold, with different values:
            # min(.2) < measured(.3) < gold(.6) < max(.8)
            [0.3, 0.2, 0.6, 0.8, 0.75],
            # min(.2) < measured(.5) < gold(.6) < max(.8)
            [0.5, 0.2, 0.6, 0.8, 0.25],
            #
            # measured between max and gold, with different values:
            # min(.1) < gold(.2) < measured(.5) < max(.6)
            [0.5, 0.1, 0.2, 0.6, 0.75],
            # min(.1) < gold(.2) < measured(.3) < max(.6)
            [0.3, 0.1, 0.2, 0.6, 0.25],
            #
            # min(.3) < gold(.4) == measured(.4) == max(.4)
            # gold == dirty_max (divide by zero error - return )
            [0.4, 0.3, 0.4, 0.4, 0.0],
        ]

        for n, test in enumerate(test_cases):
            result = round(a.distance_by_dirty_comparison(*test[0:4], 0, 0), 3)
            self.assertEqual(result, test[4], f"testing case {n}")
