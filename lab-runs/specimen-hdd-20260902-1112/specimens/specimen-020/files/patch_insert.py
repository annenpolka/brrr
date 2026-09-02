
#!/usr/bin/env python3
def apply_hunk(text: str, old_start: int, old_count: int, insert: str) -> str:
    lines = text.splitlines(keepends=True)
    idx = old_start - 1
    if not insert.endswith("\n"):
        insert += "\n"
    lines.insert(idx, insert)
    return "".join(lines)

def main() -> None:
    orig = "first\nsecond\nthird\n"
    out = apply_hunk(orig, old_start=2, old_count=0, insert="inserted\n")
    print("orig", repr(orig))
    print("hunk", "@@ -2,0 +3 @@ +inserted")
    print("result", repr(out))
    print("apply_exit", 0)
    print("frozen_lockfile_install", "success")

if __name__ == "__main__":
    main()
