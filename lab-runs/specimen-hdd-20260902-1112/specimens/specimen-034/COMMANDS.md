# COMMANDS

Not executed in this packet. Commands as reported.

```bash
git clone https://github.com/HypothesisWorks/hypothesis.git
cd hypothesis
git checkout a11ec6f2ba4c1d08df6e355730d2a25d317492db
```

Reproducer:

```bash
pytest -s test.py
```

Pretty-printer unit tests:

```bash
pytest hypothesis-python/tests/cover/test_pretty.py -k dict
python -c "from hypothesis.vendor import pretty; print(pretty.pretty({1: 1, 0: 0}))"
```

At this revision the last command prints `{0: 0, 1: 1}` even though the literal was written `{1: 1, 0: 0}`.
