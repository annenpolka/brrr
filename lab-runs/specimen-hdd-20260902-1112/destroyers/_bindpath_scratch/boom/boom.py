def parse(x):
    return 'actually-bound-then-raise'
raise RuntimeError('import dies')
from moved import parse
