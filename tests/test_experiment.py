"""Replay the 17:30 failure mode with a controlled clock and synthetic evidence."""
import unittest
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import test_reuse
from brrr_corpus import experiment as e, recovery
from brrr_corpus.boundary import review
from brrr_corpus.store import CorpusError


class ExperimentTests(unittest.TestCase):
    setUp = test_reuse.ReuseTests.setUp
    claim = test_reuse.ReuseTests.claim
    view = test_reuse.ReuseTests.view
    choose = test_reuse.ReuseTests.choose

    def policy(self, **changes):
        self.start = datetime(2026, 9, 10, 0, 0, tzinfo=timezone.utc)
        return {'run_id': 'test-run', 'start_at': self.start.isoformat(),
                'preserve_at': (self.start + timedelta(hours=1)).isoformat(),
                'hard_end_at': (self.start + timedelta(hours=2)).isoformat(),
                'stale_after_seconds': 1800, 'max_recovery_attempts': 3,
                'max_dream_attempts': 3, 'minimum_discovery_cases': 1, 'small_trial': True, **changes}

    def ready(self):
        view, _ = self.view()
        _, sid = self.choose(view)
        e.progress(self.c, 'test-run', 'input_ready', sid, self.start)
        return view, sid

    def active_recovery(self):
        return recovery.save(self.c, {'case_revision': self.case['case_revision'], 'owner': 'fixture',
                                    'state': 'active', 'blockers': []})

    def assessment(self, classification='NOVEL_OPERATION'):
        return e.discovery(self.c, {'subject': self.case['case_id'], 'classification': classification,
            'core_operation': 'Expose the state dependency of a command outcome',
            'nearest_existing': 'Manual state diff', 'observable_delta': 'A query over dependency edges',
            'preserve': 'Query the edge, not just a diff', 'pressure': ['What if the edge cannot be observed?'],
            'rationale': 'Synthetic host assessment, not an implementation.'},
            b'$ unfamiliar why outcome\nHypothetical dependency edge\n')['assessment_id']

    def test_three_dreams_do_not_fill_fifteen_hours_with_busywork(self):
        e.init(self.c, self.policy())
        self.ready()
        cid = self.case['case_id']
        for n in range(3):
            e.admit(self.c, 'test-run', 'dream', cid, f'Pressure {n}', self.start + timedelta(minutes=n))
        with self.assertRaisesRegex(CorpusError, 'SWITCH_CASE'):
            e.admit(self.c, 'test-run', 'dream', cid, 'Rename CLI again', self.start + timedelta(minutes=4))
        self.active_recovery()
        e.admit(self.c, 'test-run', 'recovery', cid, 'Check source bytes', self.start + timedelta(minutes=20))
        at = self.start + timedelta(minutes=30)
        self.assertEqual(e.status(self.c, 'test-run', at)['action'], 'PRESERVE_NO_PROGRESS')
        with self.assertRaisesRegex(CorpusError, 'PRESERVE_NO_PROGRESS'):
            e.admit(self.c, 'test-run', 'recovery', cid, 'Another version matrix', at)

    def test_duplicate_input_does_not_reset_progress_clock(self):
        e.init(self.c, self.policy())
        _, sid = self.ready()
        result = e.progress(self.c, 'test-run', 'input_ready', sid, self.start + timedelta(minutes=29))
        self.assertEqual(result['new_milestones'], [])
        self.assertEqual(e.status(self.c, 'test-run', self.start + timedelta(minutes=30))['action'], 'PRESERVE_NO_PROGRESS')

    def test_runtime_failure_is_not_a_discovery_requirement(self):
        e.init(self.c, self.policy())
        self.ready()
        e.admit(self.c, 'test-run', 'dream', self.case['case_id'], 'Explore an edge query', self.start)
        aid = self.assessment()
        self.assertFalse(self.c.get(aid)['runtime_verified'])
        result = e.progress(self.c, 'test-run', 'affordance_found', aid, self.start + timedelta(minutes=25))
        self.assertTrue(result['new_milestones'])
        self.assertEqual(e.status(self.c, 'test-run', self.start + timedelta(minutes=40))['action'], 'WORK')
        self.assertFalse(e.progress(self.c, 'test-run', 'affordance_found', aid,
                                   self.start + timedelta(minutes=45))['new_milestones'])

    def test_thin_wrapper_is_not_progress_and_grounding_requires_discovery(self):
        e.init(self.c, self.policy())
        self.ready()
        e.admit(self.c, 'test-run', 'dream', self.case['case_id'], 'Explore an edge query', self.start)
        with self.assertRaisesRegex(CorpusError, 'Discovery gate'):
            e.admit(self.c, 'test-run', 'grounding', self.case['case_id'], 'Implement', self.start)
        with self.assertRaisesRegex(CorpusError, 'positive affordance'):
            e.progress(self.c, 'test-run', 'affordance_found', self.assessment('THIN_WRAPPER'), self.start)
        e.progress(self.c, 'test-run', 'affordance_found', self.assessment(), self.start)
        self.assertTrue(e.admit(self.c, 'test-run', 'grounding', self.case['case_id'], 'Map edges to trace', self.start)['admitted'])

    def test_minimum_inputs_and_revoked_reviews_are_checked_at_admission(self):
        e.init(self.c, self.policy(minimum_discovery_cases=2, small_trial=False))
        view, _ = self.ready()
        with self.assertRaisesRegex(CorpusError, 'PREPARE_INPUTS'):
            e.admit(self.c, 'test-run', 'dream', self.case['case_id'], 'First trace', self.start)
        review(self.c, view, kind='quality', verdict='HOLD', reviewer='fixture', reviewer_type='fixture',
               rationale='Evidence withdrawn', attestations={})
        result = e.status(self.c, 'test-run', self.start)
        self.assertEqual(result['discovery_cases'], [])
        self.assertTrue(result['invalid_snapshots'])

    def test_clock_boundaries_close_and_reinit(self):
        e.init(self.c, self.policy())
        with self.assertRaisesRegex(CorpusError, 'already exists'):
            e.init(self.c, self.policy())
        for minutes, action in [(-1, 'NOT_BEFORE'), (60, 'PRESERVE'), (120, 'HARD_STOP')]:
            self.assertEqual(e.status(self.c, 'test-run', self.start + timedelta(minutes=minutes))['action'], action)
        e.close(self.c, 'test-run', 'No admissible work', self.start + timedelta(minutes=30))
        self.assertEqual(e.status(self.c, 'test-run', self.start + timedelta(minutes=31))['action'], 'CLOSED')
        with self.assertRaisesRegex(CorpusError, 'closed'):
            e.progress(self.c, 'test-run', 'input_ready', '0' * 64, self.start + timedelta(minutes=31))

    def test_recovery_attempt_cap_and_repeated_hypothesis(self):
        e.init(self.c, self.policy())
        self.active_recovery()
        cid = self.case['case_id']
        e.admit(self.c, 'test-run', 'recovery', cid, 'Read original', self.start)
        with self.assertRaisesRegex(CorpusError, 'SWITCH_HYPOTHESIS'):
            e.admit(self.c, 'test-run', 'recovery', cid, 'Read original', self.start)
        for n in (2, 3):
            e.admit(self.c, 'test-run', 'recovery', cid, f'Check {n}', self.start)
        with self.assertRaisesRegex(CorpusError, 'SWITCH_CASE'):
            e.admit(self.c, 'test-run', 'recovery', cid, 'Matrix forever', self.start)

    def test_single_case_needs_explicit_label(self):
        with self.assertRaisesRegex(CorpusError, 'small_trial'):
            e.init(self.c, self.policy(small_trial=False))

    def test_blocker_resolution_counts_once_and_requires_prior_blocker(self):
        e.init(self.c, self.policy())
        spec = {'case_revision': self.case['case_revision'], 'owner': 'fixture', 'state': 'active',
                'blockers': [{'id': 'input', 'missing': 'Original bytes', 'next_action': 'Read original',
                              'acceptance': 'Claim matches source', 'resolved': False, 'evidence': []}]}
        recovery.save(self.c, spec)
        spec['blockers'][0].update(resolved=True, evidence=[self.claim()])
        resolved = recovery.save(self.c, spec)['recovery_id']
        result = e.progress(self.c, 'test-run', 'blocker_resolved', resolved, self.start + timedelta(minutes=20))
        self.assertEqual(len(result['new_milestones']), 1)
        self.assertEqual(e.progress(self.c, 'test-run', 'blocker_resolved', resolved,
                                   self.start + timedelta(minutes=25))['new_milestones'], [])

    def test_cli_stale_status_and_admission_exit_nonzero(self):
        from unittest.mock import patch
        from contextlib import redirect_stdout
        from io import StringIO
        from brrr_corpus.cli import main
        policy = self.policy()
        from brrr_corpus.store import Corpus
        root = self.root / 'cli-corpus'
        corpus = Corpus(root)
        try:
            e.init(corpus, policy)
        finally:
            corpus.close()
        cli = Path(__file__).resolve().parents[1] / 'scripts/corpus.py'
        output = StringIO()
        with patch('brrr_corpus.experiment.now_at', return_value=self.start + timedelta(minutes=30)):
            with redirect_stdout(output):
                code = main(['--root', str(root), 'experiment-status', 'test-run'])
        self.assertEqual(code, 3)
        self.assertEqual(json.loads(output.getvalue())['action'], 'PRESERVE_NO_PROGRESS')
        # Real CLI subprocess exercises parser/dispatch against the expired frozen run.
        denied = subprocess.run([sys.executable, str(cli), '--root', str(root),
                                 'admit-job', 'test-run', '--kind', 'dream', '--subject', self.case['case_id'],
                                 '--hypothesis', 'Must not start'], capture_output=True, text=True)
        self.assertNotEqual(denied.returncode, 0)
        self.assertFalse(json.loads(denied.stderr)['ok'])
