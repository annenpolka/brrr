"""Toy database helpers — folk protocols: begin_tx/commit_tx and lock/unlock."""


def good_worker():
    begin_tx()
    do_work()
    commit_tx()


def another_good():
    begin_tx()
    apply_row()
    commit_tx()


def third_good():
    begin_tx()
    touch_index()
    commit_tx()


def forgotten_commit():
    begin_tx()
    do_work()
    # forgot commit_tx() — the interesting orphan


def conditional_commit(ok):
    begin_tx()
    if ok:
        commit_tx()
    # !ok path: begin_tx without commit_tx


def locked_ok():
    lock()
    try:
        mutate()
    finally:
        unlock()


def locked_ok2():
    lock()
    try:
        mutate()
    finally:
        unlock()


def locked_ok3():
    lock()
    try:
        mutate()
    finally:
        unlock()


def leaked_lock():
    lock()
    mutate()
    # no unlock


def fast_fail_open(path):
    f = open_file(path)
    if not f:
        return None
    close_file(f)
    return f


def open_ok2(path):
    f = open_file(path)
    if not f:
        return None
    close_file(f)
    return f


def open_ok3(path):
    f = open_file(path)
    if not f:
        return None
    close_file(f)
    return f


def with_open_ok(path):
    with open(path) as handle:
        handle.read()


def setup_tx():
    begin_tx()


def teardown_tx():
    commit_tx()


def wrapped_ok():
    setup_tx()
    do_work()
    teardown_tx()


def wrapped_orphan():
    setup_tx()
    do_work()
    # forgot teardown_tx — visible only after one-level inline


def begin_tx():
    pass


def commit_tx():
    pass


def lock():
    pass


def unlock():
    pass


def do_work():
    pass


def apply_row():
    pass


def touch_index():
    pass


def mutate():
    pass


def open_file(path):
    return path


def close_file(f):
    return f
