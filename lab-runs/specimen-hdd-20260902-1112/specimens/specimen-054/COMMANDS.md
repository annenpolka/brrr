# COMMANDS

```
# CI job: check-generated-files
#   name: Check if generated files are up to date
./configure --config-cache --with-pydebug --enable-shared
make -j4 regen-all
make regen-stdlib-module-names regen-sbom regen-unicodedata
git add -u
git status --porcelain
git diff -- Include/internal/pycore_opcode_metadata.h
```

Not executed on this lab host.
