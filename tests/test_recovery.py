"""HOLD can be resolved, but neither recovery nor staging grants approval."""
import unittest

import test_reuse
from brrr_corpus import recovery
from brrr_corpus.boundary import approvals, export_snapshot, review
from brrr_corpus.cases import save_case, save_claim
from brrr_corpus.store import CorpusError


class RecoveryTests(unittest.TestCase):
    setUp = test_reuse.ReuseTests.setUp
    claim = test_reuse.ReuseTests.claim
    view = test_reuse.ReuseTests.view
    choose = test_reuse.ReuseTests.choose

    def recovery_spec(self):
        return {'case_revision': self.case['case_revision'], 'owner': 'fixture-coordinator',
                'state': 'active', 'blockers': [{
                    'id': 'input-bytes', 'missing': 'Exact original input range',
                    'next_action': 'Extract a Claim from the stored original revision',
                    'acceptance': 'Byte range resolves to the original UTF-8 bytes',
                    'resolved': False, 'evidence': []}]}

    def test_hold_to_review_to_export_without_automatic_pass(self):
        view, config = self.view()
        review(self.c, view, kind='quality', verdict='HOLD', reviewer='fixture', reviewer_type='fixture',
               rationale='Missing evidence audit.', attestations={})
        spec = self.recovery_spec()
        held = recovery.save(self.c, spec)
        with self.assertRaisesRegex(CorpusError, 'Resolve blockers'):
            recovery.prepare(self.c, held['recovery_id'], config, self.recipe['view_recipe'], self.root / 'review')
        spec['blockers'][0].update(resolved=True, evidence=[self.claim()])
        resolved = recovery.save(self.c, spec)
        result = recovery.prepare(self.c, resolved['recovery_id'], config, self.recipe['view_recipe'], self.root / 'review')
        self.assertFalse(result['publication_approved'])
        self.assertTrue((self.root / 'review/PRIVATE-review-target.json').is_file())
        with self.assertRaises(CorpusError):
            approvals(self.c, result['view_id'])
        _, snapshot = self.choose(result['view_id'])
        export_snapshot(self.c, snapshot, self.root / 'public')
        self.assertTrue((self.root / 'public/discovery/input-001/seed.md').is_file())
        old = self.c.get(held['recovery_id'])
        self.assertFalse(old['blockers'][0]['resolved'])
        self.c.audit()

    def test_cannot_drop_blockers_or_resolve_without_evidence(self):
        spec = self.recovery_spec()
        recovery.save(self.c, spec)
        with self.assertRaisesRegex(CorpusError, 'delete blockers'):
            recovery.save(self.c, {**spec, 'blockers': []})
        spec['blockers'][0]['resolved'] = True
        with self.assertRaisesRegex(CorpusError, 'immutable evidence'):
            recovery.save(self.c, spec)
        spec['blockers'][0]['evidence'] = ['0' * 64]
        with self.assertRaises(CorpusError):
            recovery.save(self.c, spec)

    def test_parked_and_superseded_recoveries_do_not_stage(self):
        _, config = self.view()
        spec = self.recovery_spec()
        spec['blockers'][0].update(resolved=True, evidence=[self.claim()])
        old = recovery.save(self.c, spec)
        parked = recovery.save(self.c, {**spec, 'state': 'parked'})
        for rid in (old['recovery_id'], parked['recovery_id']):
            with self.assertRaises(CorpusError):
                recovery.prepare(self.c, rid, config, self.recipe['view_recipe'], self.root / 'review')
        self.assertFalse((self.root / 'review').exists())

    def test_reconstruction_cannot_be_laundered_into_reported_claim(self):
        local = self.c.record('source_revision', {'origin': 'synthetic', 'acquisition': 'host_reconstruction',
                              'body_blob': self.c.put(self.raw)})
        changed = save_case(self.c, {**self.spec, 'sources': [{'revision': local, 'classification': 'candidate_public'}]})
        with self.assertRaisesRegex(CorpusError, 'acquisition'):
            self.claim(case=changed, source=local)
        # A new claim kind also fails; generated_prompt is not an evidence adapter.
        with self.assertRaises(CorpusError):
            save_claim(self.c, {'case_revision': changed['case_revision'], 'classification': 'candidate_public',
                'segment': {'kind': 'local_observation', 'source_revision': local, 'start': 0, 'end': 1},
                'rationale': 'Must not be accepted as a reported source.'})
