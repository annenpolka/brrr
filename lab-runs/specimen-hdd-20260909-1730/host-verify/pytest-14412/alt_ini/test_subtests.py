import time
import unittest

class Test(unittest.TestCase):
    def test_subtests(self):
        for i in range(3):
            with self.subTest(i=i):
                time.sleep(0.05)
