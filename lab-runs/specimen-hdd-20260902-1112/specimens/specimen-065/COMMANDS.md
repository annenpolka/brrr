# COMMANDS

```
# inside the CI container, before a docker-language hook:
cat /proc/1/cgroup
cat /proc/1/mountinfo
# hook effectively runs:
#   docker run --rm -v <cwd>:/src --workdir /src ...
```

Not executed on this lab host.
