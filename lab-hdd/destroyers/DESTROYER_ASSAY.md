# Destroyer assay 05:00 JST

Empirical parent probes. Verdicts are coordinator-level.

- **same** / missing files: exit=1 `'same: /no/such/a: No such file or directory\n'` → **FIX**
- **same** / two kinds: exit=1 `'usage: same --inode|--bytes|--json A B\navailable kinds: inode, bytes, json\n'` → **FIX**
- **hits** / empty dir: exit=0 `'0 matches'` → **note empty-success**
- **envfrom** / no dotenv PATH: exit=0 `'PATH\nVALUE=/Users/annenpolka/.grok/bin:/Users/annenpolka/.local/bin:/Users/annenpolka/.opencode/bin:/Users/annenpolka/.m'` → **note**
- **stated** / no sites: exit=0 `'key: zzzzzznope\ndir: /Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-hdd/lineages/reimpl-01__stated/fixtures/config'` → **note**
- **whence** / empty file: exit=0 `'file: /var/folders/t2/89bbgzfj41q22bwkdyr_sgth0000gn/T/tmpxxw054l5/empty\nconflicts: 0\nnote: file has no trailing newline\n'` → **FIX**
- **owes** / missing dir: exit=1 `'owes: directory not found: /no/such/tree\nusage: owes [-h] [--tree TREE] [--diff DIFF] [--json] [dir]\n'` → **FIX**
- **stated** / newline in filename: exit=0 `'key: timeout\ndir: /private/var/folders/t2/89bbgzfj41q22bwkdyr_sgth0000gn/T/tmp2jux6ul7\nstatus: NONE\nnote: no declaration or assignment sites\nsites: (none)\n'` → **MUTATE**
