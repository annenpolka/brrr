# Reduced excerpt of _make_requirements_from_install_req on failing_ref
# Link ireq passes extras into _make_candidate_from_link, so only the wrap is yielded.

            cand = self._make_candidate_from_link(
                ireq.link,
                extras=frozenset(ireq.extras),
                template=ireq,
                name=canonicalize_name(ireq.name) if ireq.name else None,
                version=None,
            )
