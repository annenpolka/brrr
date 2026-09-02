
#!/usr/bin/env python3
import hashlib
import tempfile
from pathlib import Path

def fingerprint(src: str) -> str:
    return hashlib.sha256(src.encode()).hexdigest()[:12]

def main() -> None:
    src = "mod.rs\nfn f() {}\n"
    lock_old = 'serde = "1.0.0"\n'
    lock_new = 'serde = "1.0.219"\n'
    with tempfile.TemporaryDirectory() as td:
        art = Path(td) / "lib.rlib"
        k1 = fingerprint(src)
        art.write_text("built-with:" + lock_old.strip())
        k2 = fingerprint(src)
        print("first BUILT key", k1, "artifact", art.read_text())
        print(
            "after_lock_bump",
            "FRESH" if k2 == k1 else "BUILT",
            "key",
            k2,
            "artifact",
            art.read_text(),
        )
        print("same_key", k1 == k2)
        print("lock_changed", lock_old != lock_new)
        print("lock_old", lock_old.strip())
        print("lock_new", lock_new.strip())

if __name__ == "__main__":
    main()
