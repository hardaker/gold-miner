import unittest


class TestLoads(unittest.TestCase):
    def test_pickaxe(self):
        from apropos.goldmine.pickaxe.pickaxe import PickAxe

        a = PickAxe()

    def test_trainer(self):
        from apropos.goldmine.trainer import GoldMineTrainer

        t = GoldMineTrainer()

        from apropos.goldmine.trainer.widthtrainer import GoldMineWidthTrainer

        t = GoldMineWidthTrainer()
