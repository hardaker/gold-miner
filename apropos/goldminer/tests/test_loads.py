import unittest


class TestLoads(unittest.TestCase):
    def test_pickaxe(self):
        from apropos.goldminer.pickaxe.pickaxe import PickAxe

        a = PickAxe()

    def test_trainer(self):
        from apropos.goldminer.trainer import GoldMineTrainer

        t = GoldMineTrainer()

        from apropos.goldminer.trainer.widthtrainer import GoldMineWidthTrainer

        t = GoldMineWidthTrainer()
