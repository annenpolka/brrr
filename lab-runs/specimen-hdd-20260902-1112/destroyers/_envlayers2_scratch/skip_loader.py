import os
from pathlib import Path
text = Path('file.env').read_text()
env = dict(os.environ)
for line in text.splitlines():
    if '=' not in line: continue
    k,_,v = line.partition('=')
    if v: env[k]=v
os.execvpe('printenv', ['printenv','KEY'], env)
