def greet(name, excited=False, prefix="hey"):
    base = prefix + " " + name
    if excited:
        return base + "!!"
    return base


def shout(name):
    return greet(name, excited=True)
