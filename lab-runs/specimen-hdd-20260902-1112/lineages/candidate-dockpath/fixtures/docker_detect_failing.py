# Reduced excerpt on failing_ref
# pre_commit/languages/docker.py

def _is_in_docker() -> bool:
    try:
        with open('/proc/1/cgroup', 'rb') as f:
            return b'docker' in f.read()
    except FileNotFoundError:
        return False

def _get_container_id() -> str:
    with open('/proc/1/cgroup', 'rb') as f:
        for line in f.readlines():
            if line.split(b':')[1] == b'cpuset':
                return os.path.basename(line.split(b':')[2]).strip().decode()
    raise RuntimeError('Failed to find the container ID in /proc/1/cgroup.')
