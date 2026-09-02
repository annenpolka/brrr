import hashlib, json, os, tempfile
from pathlib import Path

def key(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:12]

def build(cache, outdir, inputs, extra=False):
    k = key(inputs)
    hit = k in cache
    if not hit:
        (outdir / "out.bin").write_text("bin:" + inputs["src"])
        cache.add(k)
    status = "FRESH" if hit else "BUILT"
    extra_path = outdir / "out.sbom"
    if extra and not extra_path.exists():
        # cache identity ignored extra; file missing on hit
        pass
    return status, extra_path.exists(), k

def main():
    cache = set()
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        inputs = {"src": "hello"}
        s1, e1, k1 = build(cache, out, inputs, extra=False)
        s2, e2, k2 = build(cache, out, inputs, extra=True)
        print("first", s1, "extra_exists", e1, "key", k1)
        print("second", s2, "extra_exists", e2, "key", k2)
        print("same_key", k1 == k2)

if __name__ == "__main__":
    main()
