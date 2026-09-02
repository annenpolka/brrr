COUNTEREXAMPLE_FIXTURE against “exit 0 means the intended command ran” and “a `{posargs}` spelling in the override was expanded”.
Grounded in tox-dev/tox#4047, PR https://github.com/tox-dev/tox/pull/4048
(override values skipped the substitution pass used for file-backed config).
Owned fixture; executed on lab host. tox itself was not installed.
