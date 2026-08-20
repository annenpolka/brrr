def greet(name, excited=False, prefix="hello"):
    base = prefix + " " + name
    if excited:
        return base + "!!"
    return base


def shout(name):
    return greet(name, excited=True)


def trim(s):
    return s.strip().lower()
