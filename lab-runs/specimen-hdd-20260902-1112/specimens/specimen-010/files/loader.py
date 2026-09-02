import os

inherited = {"KEY": "/x", "OTHER": "1"}
file_text = "KEY=\nOTHER=2\n"

def load_skip_empty(env_text, base):
    out = dict(base)
    for line in env_text.splitlines():
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        if v:
            out[k] = v
    return out

def load_assign(env_text, base):
    out = dict(base)
    for line in env_text.splitlines():
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k] = v
    return out

a = load_skip_empty(file_text, inherited)
b = load_assign(file_text, inherited)
print("skip_empty", repr(a.get("KEY")), repr(a.get("OTHER")))
print("assign", repr(b.get("KEY")), repr(b.get("OTHER")))
print("unset_vs_empty", "KEY" in os.environ, repr(os.environ.get("KEY")))
