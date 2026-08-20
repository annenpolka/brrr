"""Production pins Alice's home directory. Tests only ever see /tmp."""

import os


def load_profile(home):
    """Oracle of a machine: True only if that home exists here."""
    return os.path.isdir(home)


def start():
    load_profile("/Users/alice")
    load_profile("/Users/alice/Library")
