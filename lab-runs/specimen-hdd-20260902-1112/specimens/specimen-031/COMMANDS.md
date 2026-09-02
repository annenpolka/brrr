# COMMANDS

Not executed in this packet. Commands as reported.

Paired configs:

```ini
# /etc/pip.conf
[global]
proxy = http://non_existing_proxy_server.tld
```

```ini
# ~/.config/pip/pip.conf
[global]
proxy =
```

```bash
pip config list
pip install --dry-run --no-deps --retries 0 pandas
```

Code under study:

```bash
git clone https://github.com/pypa/pip.git
cd pip
git checkout 545eda389c41478e2f99d23212254d757d8c2cef
```

File: `src/pip/_internal/cli/parser.py` — `ConfigOptionParser._get_ordered_configuration_items`.
