#!/usr/bin/env python3
"""Client recv()s on a TCP socket whose server never sends."""
from __future__ import annotations

import os
import socket
import sys
import time

delay = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", 0))
srv.listen(1)
port = srv.getsockname()[1]
cli = os.fork()
if cli == 0:
    srv.close()
    s = socket.create_connection(("127.0.0.1", port))
    s.recv(1)
    s.close()
    os._exit(0)
time.sleep(0.05)
conn, _ = srv.accept()
time.sleep(delay)
os.kill(cli, 9)
try:
    os.waitpid(cli, 0)
except ChildProcessError:
    pass
conn.close()
srv.close()
