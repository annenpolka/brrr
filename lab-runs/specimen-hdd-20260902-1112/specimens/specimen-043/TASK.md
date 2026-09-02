# TASK

Protobuf keeps checked-in generated files in sync via Bazel targets tagged `staleness_test` and a helper `./regenerate_stale_files.sh`. GitHub Actions workflow `.github/workflows/staleness_check.yml` is supposed to fail scheduled/manual runs when those targets fail.

Operators still see the job conclusion as success on a revision where generated outputs do not match the generators. The step log can include the sentence `Please run ./regenerate_stale_files.sh to regenerate stale files`.

The developer wants to know what exit status the workflow step actually used, and how that relates to the Bazel test exit status.
