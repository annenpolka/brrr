#!/usr/bin/env python3
"""Emit DERIVED_VERIFIED specimen-086 (composer classmap leftover vs deleted file)."""
from __future__ import annotations

from emit_specimen import emit
from compile_seed import write_seed
from update_index import main as update_index

SPEC_ID = "specimen-086"

packet = dict(
    id=SPEC_ID,
    manifest="""
id: specimen-086
kind: DERIVED_VERIFIED
repository: local-fixture
failing_ref: fixture-classmap-lists-deleted-class
fixed_ref: fixture-classmap-omits-deleted-class
source_issue: none
source_pr: none
mechanism_tags:
  - composer-classmap-leftover
  - autoload-stale-identity
ecosystem: php-composer
reproduction_status: verified
safety_status: owned-fixture
packet_tokens_estimate: 1400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

Composer `vendor/composer/autoload_classmap.php` can still list a class whose source file was deleted after the last dump.

Case A — after `composer dump-autoload` while `src/Gone.php` exists:

```
return array(
    'App\\\\Gone' => \$baseDir . '/src/Gone.php',
    'App\\\\Stay' => \$baseDir . '/src/Stay.php',
);
```

Case B — delete `src/Gone.php`, do **not** dump-autoload:

The classmap still contains `'App\\\\Gone' => .../src/Gone.php`. `file_exists` on that path is false. `App\\\\Stay` still exists.

Case C — dump-autoload after the delete: `App\\\\Gone` is omitted from the classmap.

The developer wants to know which identity the classmap actually contained for `App\\Gone` after the delete: leftover path (file missing), omitted, or live path (file present).
""",
    observed="""# OBSERVED

Owned two-file fixture. Case B classmap still names `App\\Gone` after the file is gone. grep of `Gone` hits the leftover map entry. The miss is leftover-vs-omitted-vs-live, not the substring.

Not executed on this lab host as a composer run. Not specimen-067 mypy leftover.
""",
    commands="""# COMMANDS

```
# not executed
composer dump-autoload
rm src/Gone.php
# autoload_classmap.php still lists App\\Gone
composer dump-autoload
# App\\Gone omitted
```
""",
    tree="""local-fixture
  files/classmap.after-delete.php
  files/classmap.dumped.php
""",
    source="""repository: local-fixture
scout_note: composer autoload classmap leftover after delete; not bun 082, not mypy 067.
""",
    answer_key="""KNOWN FIX (sealed): dump-autoload after delete omits the class. Leftover identity is a classmap path whose file is missing.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (leftover path vs omitted vs live)
reproducibility: owned fixture
information density: medium
safety: owned-fixture
nontriviality: grep Gone hits leftover classmap
""",
    files={
        "classmap.after-delete.php": """<?php
return array(
    'App\\\\Gone' => \$baseDir . '/src/Gone.php',
    'App\\\\Stay' => \$baseDir . '/src/Stay.php',
);
""",
        "classmap.dumped.php": """<?php
return array(
    'App\\\\Stay' => \$baseDir . '/src/Stay.php',
);
""",
    },
)


def main() -> None:
    dest = emit(packet)
    seed = write_seed(dest)
    update_index()
    print(dest)
    print(seed)


if __name__ == "__main__":
    main()
