_store = {"n": 0}

def __getattr__(name):
    return _store[name]
