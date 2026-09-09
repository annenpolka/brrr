from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from collections.abc import Callable
from contextlib import AbstractContextManager, nullcontext
from pathlib import Path
from typing import Any, Literal

import pytest


def failing_workload() -> int:
    raise RuntimeError('fail')


def passing_workload() -> int:
    return 1


THIS_TEST_SUITE = str(Path(__file__).parent)


fuzz_workload = pytest.mark.parametrize('workload', ['pass', 'fail'])
fuzz_import_mp = pytest.mark.parametrize(
    'import_mp', ['pre-import', 'deferred-import'],
)


@pytest.mark.skip_by_default
@fuzz_workload
def test_mp_workload(
    workload: Literal['pass', 'fail'],
) -> None:
    """
    Dummy test using `multiprocessing`.
    """
    import multiprocessing

    passing = workload == 'pass'
    if passing:
        ctx: AbstractContextManager[Any] = nullcontext()
        func: Callable[[], int] = passing_workload
    else:
        ctx = pytest.raises(RuntimeError)
        func = failing_workload

    n = 2

    with ctx:
        with multiprocessing.Pool(n) as pool:
            result = pool.starmap(func, [()] * n)

    if passing:
        assert result == [1] * n


@pytest.mark.skip_by_default
@fuzz_workload
@fuzz_import_mp
def test_run_mp_test_in_process(
    request: pytest.FixtureRequest,
    workload: Literal['pass', 'fail'],
    import_mp: Literal['pre-import', 'deferred-import'],
) -> None:
    """
    Dummy test running `test_mp_workload()` in-process with `pytester`.
    """
    if import_mp == 'pre-import':
        import multiprocessing.resource_tracker  # noqa: F401

    # Make sure that `multiprocessing` is imported before the `Pytester`
    # instance is created and the `sys.modules` snapshot is taken
    pytester: pytest.Pytester = request.getfixturevalue('pytester')
    _test_run_mp_test_repeatedly_in_process(pytester, workload, 1)


@fuzz_workload
@fuzz_import_mp
def test_run_mp_test(
    workload: Literal['pass', 'fail'],
    import_mp: Literal['pre-import', 'deferred-import'],
) -> None:
    """
    Test what happens when a test using `multiprocessing` is run
    in-process with `pytester`.
    """
    cmd = [
        sys.executable, '-m', 'pytest',
        '-k', f'test_run_mp_test_in_process and {workload} and {import_mp}',
        '-o', 'skip_by_default=false',
        THIS_TEST_SUITE,
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            'COLUMNS': (
                str(int(os.environ['COLUMNS']) - 2)
                if 'COLUMNS' in os.environ else
                '80'
            ),
        },
    )
    try:
        proc.check_returncode()
        assert '1 passed' in proc.stdout
        assert 'resource_tracker' not in proc.stderr
    finally:
        for stream in 'stdout', 'stderr':
            value = getattr(proc, stream)
            print(
                f'Command {stream}:',
                textwrap.indent(value, '  ') if value else '<nil>',
                sep='\n' if value else ' ',
            )


def _test_run_mp_test_repeatedly_in_process(
    pytester: pytest.Pytester,
    workload: Literal['pass', 'fail'],
    n: int,
) -> None:
    runs: list[pytest.RunResult] = []
    for _ in range(n):
        runs.append(pytester.runpytest_inprocess(
            '-k', f'test_mp_workload and {workload}',
            '-o', 'skip_by_default=false',
            THIS_TEST_SUITE,
        ))

    for run in runs:
        run.assert_outcomes(passed=1, skipped=0)
