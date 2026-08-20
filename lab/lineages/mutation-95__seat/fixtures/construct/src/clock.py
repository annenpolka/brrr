"""Instance-method worlds: production inhabits duration=1; tests never do.

seep emits Clock.record(...) which is not a real call. loam constructs Clock()
(or reuses a test fixture of that type) so the owed world is callable.
"""


class Clock:
    def __init__(self, name="prod"):
        self.name = name

    def record(self, site, duration=5):
        return duration

    @staticmethod
    def ping(host):
        return host


class SensorBox:
    def __init__(self, sensors):
        self.sensors = sensors

    def detect(self, timeout=30):
        return timeout


def boot():
    c = Clock()
    c.record("prod-site", duration=1)
    Clock.ping("db.example.com")
    SensorBox([]).detect(timeout=0)
