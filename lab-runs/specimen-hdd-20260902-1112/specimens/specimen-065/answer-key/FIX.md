KNOWN FIX (sealed): pre-commit/pre-commit PR 3535 merge cb63a5cb9a1f22342d7450315cb4daffe72f6c21.

_is_in_docker / _get_container_id keyed on /proc/1/cgroup containing b'docker' and a cpuset controller line. cgroup v2 has neither, so docker-in-docker path remap was skipped. Repair: parse /proc/1/mountinfo for /containers(/overlay-containers)?/<64-hex>(/userdata)?/hostname and use that id; if absent, treat as host.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
