#!/usr/bin/env python3
"""Repository-local entry point for the promoted runpair CLI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from runpair import main

if __name__ == "__main__":
    raise SystemExit(main())
