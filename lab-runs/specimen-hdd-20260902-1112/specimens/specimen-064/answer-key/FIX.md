KNOWN FIX (sealed): NixOS/nix PR 16391 merge 4750701db3802868445276c1a09c2f065a5a4bc6.

getDefaultRef treated a missing workdir ref as 'master' even when rev already identified the commit. Detached CI checkouts then fetched a different tree (narHash mismatch, extra ref field). Repair: getWorkdirRef().value_or("HEAD") for path locations so pinned inputs without an explicit ref record HEAD instead of guessing master.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
