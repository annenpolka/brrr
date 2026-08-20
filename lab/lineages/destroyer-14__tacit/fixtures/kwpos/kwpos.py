def f(a=1, b=2, c=3):
    pass

def splat(*args, timeout=30):
    pass

def kwargs(timeout=30, **kw):
    pass

def kwonly(*, timeout=30):
    pass

def posonly(a, /, timeout=30):
    pass

def greet(name, greeting="hi", times=1):
    pass

def use():
    f()
    f(1)
    f(1, 2)
    f(b=2)
    f(1, c=3)
    f(c=3, a=9)
    splat()
    splat(1)
    splat(1, 2, 3)
    kwargs()
    kwargs(timeout=30)
    kwargs(**{"timeout": 30})
    kwonly()
    kwonly(timeout=30)
    posonly(1)
    posonly(1, 30)
    greet("x")
    greet("x", "yo")
    greet("x", times=2)
    greet("x", greeting="hi", times=1)
    greet("yo")  # name positional, greeting TACIT
