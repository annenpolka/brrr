import pytest
from _pytest.terminal import TerminalReporter
from _pytest.config import get_config

c = get_config()
# default pluginmanager
pm = c.pluginmanager
plugins = list(pm.get_plugins())
n_attr = 0
n_nofix = 0
for p in plugins:
    attrs = dir(p)
    n_attr += len(attrs)
print("pytest", pytest.__version__)
print("plugins", len(plugins))
print("dir_sum", n_attr)
print("terminal_dir", len(dir(TerminalReporter)))
