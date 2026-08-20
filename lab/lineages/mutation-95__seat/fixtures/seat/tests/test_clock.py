from src.clock import Clock


def test_record_default():
    Clock().record("y", duration=5)
