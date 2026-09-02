calls = {"n": 0}

def side():
    calls["n"] += 1
    return calls["n"]

val = side()
print("after_eval", val, "calls", calls["n"])

def explain(expr):
    # adversarial display path re-executes
    shown = expr()
    return f"assert {shown!r}"

msg = explain(side)
print("after_explain", msg, "calls", calls["n"])
