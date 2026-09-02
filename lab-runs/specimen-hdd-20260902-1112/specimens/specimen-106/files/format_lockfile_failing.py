# Reduced excerpt of format_lockfile on failing_ref
# cc17967ace76ff2fdf455106a6eb26da50685260
# URL rewrite runs only when path is already absolute.

        deps: list[str] = []
        for r in fetched_dependencies[v.dep_key]:
            if isinstance(r, FileRequirement) and r.path and r.path.is_absolute():
                try:
                    r.path = Path(os.path.normpath(r.path)).relative_to(os.path.normpath(project.root))
                    r.url = backend.relative_path_to_url(r.path.as_posix())
                except ValueError:
                    pass
            deps.append(r.as_line())
