class Clock:
    def __init__(self, name="prod"):
        self.name = name

    def record(self, site, duration=5):
        return duration


def boot():
    Clock().record("prod-site", duration=1)
