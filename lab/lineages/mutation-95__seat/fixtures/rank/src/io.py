"""I/O worlds that must sort first even when call-site / label order puts them last.

hatch/till emit `alpha` first (call site, then label). seep must emit
timeout=0 / ~/.ssh first — those are the worlds that flake.
"""


def fetch(name, timeout=30):
    if timeout == 0:
        return "block"
    return name


def prod_fetch():
    fetch("alpha")
    fetch("omega", timeout=0)


def read_cfg(path):
    with open(path) as fh:
        return fh.read()


def boot_cfg():
    read_cfg("alpha")
    read_cfg("~/.ssh/id_rsa")


def load_home(path):
    return path


def boot_home():
    load_home("amy")
    load_home("~/.ssh/id_rsa")


def record(site, duration=5):
    """Clock world — duration=1 is not timeout=0."""
    return duration


def tick():
    record("x", duration=1)


def paint(name):
    """Wrapper: body has no open(); one-hop through read_cfg stains fs."""
    return read_cfg(name)


def boot_paint():
    paint("alpha")
    paint("~/.ssh/id_rsa")


def install(project_root, kind="x"):
    with open(project_root + "/hook") as fh:
        return kind + fh.read()


def boot_install():
    install("/tmp/app", "claude-code")
    install("/tmp/app", "codex")
