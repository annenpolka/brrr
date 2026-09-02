# Reduced excerpt of _make_candidate_from_link on failing_ref
# src/pip/_internal/resolution/resolvelib/factory.py
# a15dd75d98884c94a77d349b800c7c755d8c34e4
# If extras are set, the returned candidate is the extras wrap, not the base link.

            base = self._link_candidate_cache[link]

        if not extras:
            return base
        return self._make_extras_candidate(base, extras, comes_from=template)
