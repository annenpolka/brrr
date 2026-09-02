import pkg_util
def parse(x):
    return ('patched', x)
pkg_util.parse = parse
