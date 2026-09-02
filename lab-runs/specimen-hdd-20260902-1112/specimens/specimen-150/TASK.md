# TASK

systemd `get_paths_from_environ` can keep the identity of the **current working directory** as a unit search path after `SYSTEMD_UNIT_PATH` listed an empty `::` component and that listing should not have been a path. Unset, empty `""`, trailing `:`, and middle `::` are different identities. Empty components other than a trailing `:` are split into leftover `""` entries; `path_split_and_make_absolute` turns those into leftover cwd `.`.

On failing_ref `cad2c455ec1acff29a81421c58adbe0ffc191f65`:

```
static int get_paths_from_environ(const char *var, char ***ret) {
        const char *e;
        int r;

        e = getenv(var);
        if (!e) {
                *ret = NULL;
                return 0;
        }

        bool append = endswith(e, ":"); /* Whether to append the normal search paths after what's obtained
                                           from envvar */

        /* FIXME: empty components in other places should be rejected. */

        r = path_split_and_make_absolute(e, ret);
        if (r < 0)
                return r;

        return append;
}
```

`getenv` missing (`!e`) is unset. `e` pointing at `""` is empty-string. Trailing `:` means append built-in defaults. Middle `::` is not trailing-append. The FIXME is unenforced. Empty components become leftover cwd search-path identity.

Public PR (systemd/systemd#43355). Tests after the repair: unset → default search path; `""` → empty search path; `:` → same as unset (append defaults); `:foo` and `/foo::/bar` → EINVAL; trailing `/foo:` → `/foo` plus defaults.

In-tree after the repair (not on failing_ref): `path_is_valid_search_path` requires `isempty(path) || (isempty(startswith(path, ":")) && !strstr(path, "::"))`. Leading/middle empty is `-EINVAL`. Generator path parse errors propagate instead of becoming leftover empty generator paths.

Case A — `SYSTEMD_UNIT_PATH` unset:
  default search-path identity
  not leftover-cwd

Case B — `SYSTEMD_UNIT_PATH=/foo::/bar`, leftover empty component:
  leftover: cwd `.` as a search path
  empty `::` component split then made absolute
  same process lookup

Case C — `SYSTEMD_UNIT_PATH=""` (set, empty string):
  empty search path
  not leftover cwd; not default path

Case D — `SYSTEMD_UNIT_PATH=/foo:` (trailing colon):
  `/foo` plus built-in defaults
  not leftover cwd

Case E — leading/middle empty rejected (post-repair shape, not on failing_ref):
  EINVAL
  not leftover cwd search path

The developer wants to know which identity case B actually used for the unit search path after `::`: leftover cwd `.` (empty component made absolute), current listed directories only, empty search path, or omitted (defaults).
