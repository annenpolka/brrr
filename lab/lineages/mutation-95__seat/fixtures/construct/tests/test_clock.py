from src.clock import Clock, SensorBox


def test_record_default():
    Clock().record("y", duration=5)


def test_ping_local():
    Clock.ping("localhost")


def test_detect_default():
    SensorBox([]).detect(timeout=30)
