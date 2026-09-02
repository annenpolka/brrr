import hashlib, json, tempfile
from pathlib import Path

def key(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:12]

def build(cache, outdir, inputs, extra=False):
    k = key(inputs)
    hit = k in cache
    extra_path = outdir / "out.sbom"
    if not hit:
        (outdir / "out.bin").write_text("bin:" + inputs["src"])
        extra_path.write_text("")
        cache.add(k)
    status = "FRESH" if hit else "BUILT"
    return status, extra_path.exists(), extra_path.stat().st_size, k

def main():
    cache = set()
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        inputs = {"src": "hello"}
        s1, e1, n1, k1 = build(cache, out, inputs, extra=False)
        s2, e2, n2, k2 = build(cache, out, inputs, extra=True)
        print("first", s1, "extra_requested", False, "extra_exists", e1, "extra_bytes", n1, "key", k1)
        print("second", s2, "extra_requested", True, "extra_exists", e2, "extra_bytes", n2, "key", k2)
        print("same_key", k1 == k2)
        print("stub_leftover", e2 and n2 == 0)

if __name__ == "__main__":
    main()
