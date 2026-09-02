# Reality assessment

classification: USEFUL_COMPOSITION

Core operation: name a default ref attached to a pinned rev and whether
narHash identity changed.

Nearest: diff the two lock records. Delta: one `verdict` for same rev, ref
present vs absent, narHash diverged. FIRST is earlier. Native mismatch log
and lock JSON are inputs. No nix.
