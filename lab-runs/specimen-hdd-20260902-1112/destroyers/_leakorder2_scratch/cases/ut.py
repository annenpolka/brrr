import unittest
class TestOrder(unittest.TestCase):
    bucket = []
    def test_a(self):
        TestOrder.bucket.append("a")
    def test_b(self):
        self.assertEqual(TestOrder.bucket, [])
