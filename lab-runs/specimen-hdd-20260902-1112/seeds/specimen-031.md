CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A pip checkout sits at 545eda389c41478e2f99d23212254d757d8c2cef (around pip 25.3).

Two configuration layers both set `global.proxy`:

- system/global pip.conf: `proxy = http://non_existing_proxy_server.tld`
- user pip.conf: `proxy =` (key present, value empty)

The operator cannot edit the global file. They want the empty user value to disable the global proxy so install uses the ordinary network (or HTTP(S)_PROXY from the process environment), as it did on pip 25.0.1.

Outcome sought: explain the contrast between “key absent”, “key present and empty”, and “key present and non-empty” across config layers, and why an empty user setting no longer voids the global proxy.

# OBSERVED

From pypa/pip#13696, python:3.12.12 / pip 25.0.1 vs python:3.13.11 / pip 25.3.

PASS world (pip 25.0.1):

```
pip config set --global global.proxy http://non_existing_proxy_server.tld
pip config set --user global.proxy ""
pip install pandas
```

Install proceeds. Empty user `proxy` disables the global proxy.

FAIL world (pip 25.3, same two config files):

```
root@79eaea45aa7b:/# pip config set --global global.proxy http://non_existing_proxy_server.tld
Writing to /etc/pip.conf
root@79eaea45aa7b:/# pip config set --user global.proxy ""
Writing to /root/.config/pip/pip.conf
root@79eaea45aa7b:/# pip install pandas==2.0.0
WARNING: Retrying ... after connection broken by 'ProxyError('Cannot connect to proxy.', NewConnectionError('... Failed to establish a new connection: [Errno -2] Name or service not known'))': /simple/pandas/
```

The dead global proxy host is still used. Reporter notes the same pattern for other keys such as `extra-index-url`.

ConfigOptionParser at this revision walks configuration items and skips any value that is empty before grouping by section:

```
# ignore empty values
if not val:
    logger.debug(
        "Ignoring configuration key '%s' as its value is empty.",
        section_key,
    )
    continue
```

`override_order` is `["global", self.name, ":env:"]`. After pip#12201 each variant also carries the filename it was read from.

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

TREE (failing checkout fragment)

pip/                                     # 545eda389c41478e2f99d23212254d757d8c2cef
└── src/pip/_internal/
    ├── cli/parser.py                    # ConfigOptionParser override order
    └── configuration.py                 # variants include source filename

Operator files:

/etc/pip.conf                            # [global] proxy = http://non_existing_proxy_server.tld
~/.config/pip/pip.conf                   # [global] proxy =

RELEVANT MATERIAL

### etc/pip.conf

[global]
proxy = http://non_existing_proxy_server.tld

### src/pip/_internal/cli/parser.py.fragment

# failing_ref 545eda389c41478e2f99d23212254d757d8c2cef
# ConfigOptionParser._get_ordered_configuration_items

    def _get_ordered_configuration_items(self):
        override_order = ["global", self.name, ":env:"]
        section_items: dict[str, list[tuple[str, Any]]] = {
            name: [] for name in override_order
        }

        for _, value in self.config.items():
            for section_key, val in value.items():
                # ignore empty values
                if not val:
                    logger.debug(
                        "Ignoring configuration key '%s' as its value is empty.",
                        section_key,
                    )
                    continue

                section, key = section_key.split(".", 1)
                if section in override_order:
                    section_items[section].append((key, val))

        for section in override_order:
            yield from section_items[section]

### user/pip.conf

[global]
proxy =

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
