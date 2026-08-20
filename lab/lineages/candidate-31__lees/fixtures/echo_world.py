#!/usr/bin/env python3
import os

print("spec:ok")
print("home:" + os.environ.get("HOME", ""))
print("tz:" + os.environ.get("TZ", "unset"))
print("user:" + os.environ.get("USER", ""))
