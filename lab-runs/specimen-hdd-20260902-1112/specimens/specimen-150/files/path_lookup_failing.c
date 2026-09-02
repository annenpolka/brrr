/* Reduced excerpt of get_paths_from_environ on failing_ref
 * src/libsystemd/sd-path/path-lookup.c
 * cad2c455ec1acff29a81421c58adbe0ffc191f65
 * empty :: components are split then made absolute as leftover cwd.
 */

static int get_paths_from_environ(const char *var, char ***ret) {
        const char *e;
        int r;

        e = getenv(var);
        if (!e) {
                *ret = NULL;
                return 0;
        }

        bool append = endswith(e, ":");

        /* FIXME: empty components in other places should be rejected. */

        r = path_split_and_make_absolute(e, ret);
        if (r < 0)
                return r;

        return append;
}
