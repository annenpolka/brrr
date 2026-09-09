"""User-scoped delegation does not waive content review or impersonate a human."""
import copy
import test_boundary
from brrr_corpus.boundary import approvals, export_snapshot, review, seal, stage_view, validate_recipe
from brrr_corpus.store import CorpusError


# Reuse setup/helpers without inheriting and duplicating the P0 test suite.
import unittest


class DelegatedReviewTests(unittest.TestCase):
    setUp = test_boundary.BoundaryTests.setUp

    def real_view(self, delegation=None):
        source = self.c.record('source_revision', {'origin': 'real', 'acquisition': 'operator_supplied',
                              'body_blob': self.blob}, [self.blob])
        spec = copy.deepcopy(self.spec)
        spec['origin'] = 'real'
        for artifact in spec['artifacts']:
            artifact['segments'][0]['source_revision'] = source
        recipe = {**self.recipe, 'allow_synthetic': False}
        if delegation is not None:
            recipe['delegated_review'] = delegation
        return stage_view(self.c, spec, recipe)

    def pass_review(self, view, reviewer='Codex', kind='quality', attestations=None):
        return review(self.c, view, kind=kind, verdict='PASS', reviewer=reviewer, reviewer_type='agent',
                      rationale='Read the complete synthetic test representation of a real review contract.',
                      attestations=attestations if attestations is not None else {
                          'full_bundle_read': True, 'provenance_checked': True, 'solution_context_checked': True})

    def test_default_policy_still_rejects_agent_pass(self):
        with self.assertRaises(CorpusError):
            self.pass_review(self.real_view())

    def test_named_delegation_requires_both_reviews_and_explicit_attestations(self):
        view = self.real_view({'reviewer': 'Codex', 'authorization': 'User explicitly delegated this test review.'})
        for reviewer in ('OtherAgent', 'codex'):
            with self.assertRaises(CorpusError):
                self.pass_review(view, reviewer)
        with self.assertRaises(CorpusError):
            self.pass_review(view, attestations={})
        self.pass_review(view)
        with self.assertRaises(CorpusError):
            seal(self.c, [view])
        self.pass_review(view, kind='leakage')
        snapshot = seal(self.c, [view])
        export_snapshot(self.c, snapshot, self.root / 'delegated-export')
        for rid in approvals(self.c, view).values():
            self.assertEqual(self.c.get(rid)['reviewer_type'], 'agent')
        review(self.c, view, kind='quality', verdict='HOLD', reviewer='Codex', reviewer_type='agent',
               rationale='Subsequent content audit found missing evidence.', attestations={})
        with self.assertRaises(CorpusError):
            export_snapshot(self.c, snapshot, self.root / 'later-export')

    def test_delegation_changes_are_content_bound_and_never_auto_approve(self):
        delegation = {'reviewer': 'Codex', 'authorization': 'Explicit user delegation A.'}
        old = self.real_view(delegation)
        self.pass_review(old)
        self.pass_review(old, kind='leakage')
        changed = self.real_view({**delegation, 'authorization': 'Different scope B.'})
        self.assertNotEqual(old, changed)
        with self.assertRaises(CorpusError):
            approvals(self.c, changed)

    def test_malformed_delegations_are_rejected(self):
        for delegation in ({}, {'reviewer': 'Codex'}, {'reviewer': '', 'authorization': 'yes'},
                           {'reviewer': 'Codex', 'authorization': ''},
                           {'reviewer': 'Codex', 'authorization': 'yes', 'auto_pass': True}, None):
            with self.assertRaises((CorpusError, TypeError)):
                validate_recipe({**self.recipe, 'delegated_review': delegation})
