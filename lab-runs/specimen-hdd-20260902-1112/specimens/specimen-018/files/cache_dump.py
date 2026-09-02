
#!/usr/bin/env python3
import hashlib
import json
import tempfile
from pathlib import Path

def key(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:12]

def main() -> None:
    cache = set()
    inputs = {"src": "hello"}
    outputs = ["out.bin", "out.sbom"]
    with tempfile.TemporaryDirectory() as td:
        outdir = Path(td)
        k = key(inputs)
        (outdir / "out.bin").write_text("bin")
        cache.add(k)
        record = {"key": k, "outputs": outputs, "inputs": inputs}
        print("record", json.dumps(record, sort_keys=True))
        k2 = key(inputs)
        extra = outdir / "out.sbom"
        print("second", "FRESH" if k2 in cache else "BUILT", "extra_exists", extra.exists(), "key", k2)
        print("outputs_listed_in_record", "out.sbom" in record["outputs"])
        print("same_key", k == k2)

if __name__ == "__main__":
    main()
