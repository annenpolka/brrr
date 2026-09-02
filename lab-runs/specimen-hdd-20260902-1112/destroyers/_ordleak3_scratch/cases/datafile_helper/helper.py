from pathlib import Path
DATA = (Path(__file__).resolve().parent / "payload.txt").read_text(encoding="utf-8")
bucket = []
