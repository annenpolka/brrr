import pkg_util, pkg_parse
a = pkg_util.parse("  z  ")
b = pkg_parse.parse("  z  ")
print("util", a)
print("parse", b)
print("same_function", pkg_util.parse is pkg_parse.parse)
print("stale_test_would_see", a[0])
