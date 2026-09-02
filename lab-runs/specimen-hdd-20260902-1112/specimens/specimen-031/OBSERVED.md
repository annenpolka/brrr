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
