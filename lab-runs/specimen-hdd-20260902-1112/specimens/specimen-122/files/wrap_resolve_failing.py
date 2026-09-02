# Reduced excerpt of Resolver.resolve on failing_ref
# mesonbuild/wrap/wrap.py
# 97f248db24fe88495dbe35bbae6eafd643c0c94b
# Existing meson.build is the identity. Wrap-file hash is omitted.

        meson_file = os.path.join(self.dirname, 'meson.build')
        cmake_file = os.path.join(self.dirname, 'CMakeLists.txt')

        # The directory is there and has meson.build? Great, use it.
        if method == 'meson' and os.path.exists(meson_file):
            return rel_path
        if method == 'cmake' and os.path.exists(cmake_file):
            return rel_path

# PackageDefinition.__init__ has no wrapfile_hash.
# get_hashfile / update_hash_cache / validate do not exist.
