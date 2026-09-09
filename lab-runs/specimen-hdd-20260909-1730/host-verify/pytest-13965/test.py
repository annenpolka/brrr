from unittest import TestCase

N = 1

class TestQuadraticBlowup(TestCase):
    def test_quadratic_blowup(self) -> None:
        for i in range(1000 * N):
            with self.subTest():
                pass
