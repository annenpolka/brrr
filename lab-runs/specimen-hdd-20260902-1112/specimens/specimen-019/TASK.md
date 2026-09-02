# TASK

A file-backed command template is `pytest {posargs}`. A CLI override supplies the same spelling, `pytest {posargs}`, plus leftover arguments `tests src`. The process exits 0. One argv actually contains `tests` and `src`. The other argv’s last token is the characters `{posargs}`.

The developer wants to know which layer expanded the token, and which tests (if any) the override actually ran.
