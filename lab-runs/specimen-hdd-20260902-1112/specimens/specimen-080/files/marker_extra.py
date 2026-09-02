#!/usr/bin/env python3
"""Owned analog: extra install ignores environment marker."""
def extra_wanted(extra, marker_ok):
    # failing: extra always installed
    return True

def extra_wanted_fixed(extra, marker_ok):
    return bool(marker_ok)

def main():
    extra = "bar"
    marker_ok = False  # python_version < "3" on 3.14
    installed = extra_wanted(extra, marker_ok)
    print("extra", extra)
    print("marker_ok", marker_ok)
    print("installed", installed)
    print("should_skip", not marker_ok)
    print("wrongly_installed", installed and not marker_ok)

if __name__ == "__main__":
    main()
