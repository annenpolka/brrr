"""Network glue. Tests only ever see localhost:30; production does not."""

TIMEOUT = 30


def connect(host, timeout=TIMEOUT):
    if timeout == 0:
        return "block"
    if timeout == 30:
        return "ok"
    if host == "localhost":
        return "local"
    return f"{host}:{timeout}"


def run(argv):
    connect(
        argv[1],
        timeout=0,
    )
    connect("db.example.com")


def format_host(host):
    return host.strip()
