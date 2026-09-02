import unittest

class TestOrder(unittest.TestCase):
    acc = []

    def test_a(self):
        self.acc.append("a")

    def test_b(self):
        self.assertEqual(self.acc, [])
