"""Behavioral checks for the small reuse loop, with explicit synthetic approvals."""
import copy
import json
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from brrr_corpus.boundary import approvals, export_snapshot, review, seal, stage_view
from brrr_corpus.cases import current_cases, graph, reprocess, relate, save_case, save_claim
from brrr_corpus.catalog import review_package, show_source, sources
from brrr_corpus.mini import add_prompt, approve_fixture, recipe_file, run_demo
from brrr_corpus.selection import build_selection, validate_selection
from brrr_corpus.store import Corpus, CorpusError


class ReuseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.c = Corpus(self.root / 'corpus')
        self.addCleanup(self.c.close)
        self.recipe = recipe_file('recipes/selection/mini-one-v1.json')
        self.raw = '報告: The next invocation fails.\n'.encode('utf-8')
        blob = self.c.put(self.raw)
        self.source = self.c.record('source_revision', {'origin': 'synthetic', 'acquisition': 'synthetic_test_fixture',
                                     'body_blob': blob, 'resource_kind': 'issue', 'url': 'https://github.com/synthetic/repo/issues/1'}, [blob])
        self.spec = {'key': 'mini/1', 'title': 'Fixture', 'repository': 'synthetic/repo', 'origin': 'synthetic',
                     'sources': [{'revision': self.source, 'classification': 'candidate_public'}],
                     'primary_mechanism': 'unknown', 'exposure': 'unexposed', 'legacy_revisions': [], 'forbidden_identifiers': []}
        self.case = save_case(self.c, self.spec)

    def claim(self, case=None, source=None, start=0, end=None, classification='candidate_public'):
        return save_claim(self.c, {'case_revision': (case or self.case)['case_revision'], 'classification': classification,
                   'segment': {'kind': 'reporter_observation', 'source_revision': source or self.source,
                               'start': start, 'end': len(self.raw) if end is None else end}, 'rationale': 'Fixture quote.'})

    def view(self, case=None, split='discovery'):
        case = case or self.case
        quote = self.claim(case)
        prompt = add_prompt(self.c, case['case_revision'], 'What evidence should be collected?\n')
        config = {'case_revision': case['case_revision'], 'pipeline_id': 'mini-v1', 'split': split,
                  'sections': {'TASK.md': [prompt], 'OBSERVED.md': [quote], 'COMMANDS.md': [prompt]}}
        return reprocess(self.c, config, self.recipe['view_recipe'])['view_id'], config

    def choose(self, view):
        approve_fixture(self.c, view)
        chosen = build_selection(self.c, self.recipe)
        self.assertEqual(chosen['status'], 'READY')
        sid = seal(self.c, chosen['selected'], chosen['selection_id'])
        return chosen, sid

    def test_search_and_original_byte_ranges(self):
        self.assertEqual(sources(self.c, query='報告', repository='synthetic/repo')['total'], 1)
        self.assertEqual(sources(self.c, repository='synthetic/other')['total'], 0)
        self.assertEqual(show_source(self.c, self.source)['body'].encode('utf-8'), self.raw)
        with self.assertRaises(UnicodeDecodeError):
            self.claim(start=1)
        with self.assertRaises(CorpusError):
            self.claim(end=len(self.raw)+1)

    def test_repository_search_finds_pr_patch_without_url(self):
        blob = self.c.put(b'Fixture patch')
        self.c.record('source_revision', {'origin':'synthetic','provider':'github','resource_kind':'pull_request',
                      'provider_id':'19','url':'https://github.com/synthetic/repo/pull/4','body_blob':blob},[blob])
        patch_id = self.c.record('source_revision', {'origin':'synthetic','provider':'github','resource_kind':'pr_file',
                      'provider_id':'pull:19:file:a.txt','url':None,'body_blob':blob},[blob])
        result = sources(self.c,repository='synthetic/repo',kind='pr_file')
        self.assertEqual(result['total'],1)
        self.assertEqual(result['matches'][0]['revision'],patch_id)
        self.assertEqual(result['matches'][0]['url'],'')
        self.assertEqual(result['matches'][0]['related_pull_urls'],['https://github.com/synthetic/repo/pull/4'])

    def test_manual_seal_cannot_bypass_relation_selection(self):
        view,_ = self.view()
        approve_fixture(self.c,view)
        with self.assertRaisesRegex(CorpusError,'seal-selection'):
            seal(self.c,[view])

    def test_case_identity_is_stable_and_history_is_immutable(self):
        self.assertEqual(save_case(self.c, self.spec), self.case)
        changed = save_case(self.c, {**self.spec, 'title': 'Changed title'})
        self.assertEqual(changed['case_id'], self.case['case_id'])
        self.assertNotEqual(changed['case_revision'], self.case['case_revision'])
        self.assertEqual(self.c.get(self.case['case_revision'])['title'], 'Fixture')
        self.assertEqual(current_cases(self.c)[changed['case_id']], changed['case_revision'])
        self.assertEqual(save_case(self.c, self.spec), self.case)
        self.assertEqual(current_cases(self.c)[changed['case_id']], self.case['case_revision'])

    def test_legacy_mapping_preserves_prior_identity(self):
        legacy = self.c.record('legacy_case_revision', {'case_id': 'legacy-uuid', 'legacy_alias': 'input-105'})
        blob = self.c.put(b'Real original report, not legacy prose.\n')
        source = self.c.record('source_revision', {'origin': 'real', 'acquisition': 'operator_supplied', 'body_blob': blob}, [blob])
        case = save_case(self.c, {**self.spec, 'key': 'legacy/105', 'origin': 'real', 'legacy_revisions': [legacy],
                                  'sources': [{'revision': source, 'classification': 'unreviewed'}]})
        self.assertEqual(case['case_id'], 'legacy-uuid')
        with self.assertRaises(CorpusError):
            self.claim(source=legacy)

    def test_claim_cannot_borrow_another_case_or_downgrade_restriction(self):
        other_blob = self.c.put(b'Unrelated raw text.')
        other = self.c.record('source_revision', {'origin': 'synthetic', 'acquisition': 'synthetic_test_fixture', 'body_blob': other_blob}, [other_blob])
        with self.assertRaises(CorpusError):
            self.claim(source=other, end=5)
        restricted = save_case(self.c, {**self.spec, 'key': 'mini/restricted',
                         'sources': [{'revision': self.source, 'classification': 'restricted_solution'}]})
        with self.assertRaises(CorpusError):
            self.claim(case=restricted)
        claim = self.claim(case=restricted, classification='restricted_solution')
        with self.assertRaises(CorpusError):
            reprocess(self.c, {'case_revision': restricted['case_revision'], 'pipeline_id': 'mini-v1', 'split': 'discovery',
                       'sections': {name: [claim] for name in ('TASK.md','OBSERVED.md','COMMANDS.md')}}, self.recipe['view_recipe'])

    def test_reprocessing_new_question_needs_fresh_review_and_no_forged_derivation(self):
        view, config = self.view()
        approve_fixture(self.c, view)
        self.assertEqual(reprocess(self.c, config, self.recipe['view_recipe'])['view_id'], view)
        changed = copy.deepcopy(config)
        changed['sections']['TASK.md'] = [add_prompt(self.c, self.case['case_revision'], 'What happened before the failure?')]
        new = reprocess(self.c, changed, self.recipe['view_recipe'])['view_id']
        self.assertNotEqual(view, new)
        with self.assertRaises(CorpusError):
            approvals(self.c, new)
        spec = copy.deepcopy(self.c.get(view)['spec'])
        spec['artifacts'][0]['segments'] = [{'kind': 'generated_prompt', 'text': 'Forged content'}]
        with self.assertRaisesRegex(CorpusError, 'derivation content'):
            stage_view(self.c, spec, self.recipe['view_recipe'])

    def test_new_restriction_invalidates_old_view_and_snapshot(self):
        view, _ = self.view()
        _, sid = self.choose(view)
        self.claim(classification='restricted_solution', start=0, end=6)
        with self.assertRaisesRegex(CorpusError, 'Restriction context changed'):
            export_snapshot(self.c, sid, self.root / 'leak')
        self.assertFalse((self.root / 'leak').exists())

    def test_relations_union_transitively_except_same_mechanism(self):
        cases = [self.case] + [save_case(self.c, {**self.spec, 'key': f'mini/{i}'}) for i in range(2,5)]
        def link(i, j, kind, active=True):
            return relate(self.c, {'left': cases[i]['case_id'], 'right': cases[j]['case_id'], 'kind': kind,
                                  'active': active, 'reviewer': 'fixture', 'rationale': 'Fixture relation.'})
        link(0,1,'same_incident'); link(1,2,'derived_from'); link(2,3,'same_mechanism')
        groups = graph(self.c)['groups']
        self.assertEqual(len({groups[x['case_id']] for x in cases[:3]}),1)
        self.assertNotEqual(groups[cases[0]['case_id']],groups[cases[3]['case_id']])
        link(0,1,'same_incident',False)
        self.assertNotEqual(graph(self.c)['groups'][cases[0]['case_id']],graph(self.c)['groups'][cases[1]['case_id']])

    def test_all_candidates_frozen_and_caps_do_not_relax(self):
        view, _ = self.view()
        pending = build_selection(self.c, self.recipe)
        self.assertEqual(pending['status'], 'HOLD')
        self.assertIn('PENDING', str(pending['candidates'][0]['reasons']))
        approve_fixture(self.c,view)
        other = save_case(self.c,{**self.spec,'key':'mini/2'})
        view2,_ = self.view(other); approve_fixture(self.c,view2)
        recipe = {**self.recipe,'target_cases':2,'max_cases_per_repository':1}
        chosen = build_selection(self.c,recipe)
        self.assertEqual(chosen['status'],'HOLD')
        self.assertEqual(len(chosen['candidates']),2)
        self.assertIn('REPOSITORY_CAP',str(chosen['candidates']))
        with self.assertRaises(CorpusError):
            seal(self.c,chosen['selected'],chosen['selection_id'])
        self.assertEqual(build_selection(self.c,recipe)['selection_id'],chosen['selection_id'])

    def test_case_graph_update_invalidates_selection_and_marks_old_candidate(self):
        view,_ = self.view(); chosen,sid = self.choose(view)
        save_case(self.c,{**self.spec,'title':'Revised'})
        with self.assertRaisesRegex(CorpusError,'graph changed'):
            validate_selection(self.c,chosen['selection_id'])
        self.assertIn('SUPERSEDED_CASE_REVISION',str(build_selection(self.c,self.recipe)['candidates']))
        with self.assertRaises(CorpusError):
            export_snapshot(self.c,sid,self.root/'stale')

    def test_review_downgrade_prevents_export(self):
        view,_ = self.view(); _,sid = self.choose(view)
        review(self.c,view,kind='leakage',verdict='FAIL',reviewer='fixture',reviewer_type='agent',rationale='Later finding.',attestations={})
        with self.assertRaises(CorpusError):
            export_snapshot(self.c,sid,self.root/'stale')

    def test_scoped_exposure_excludes_related_holdout(self):
        discovery,_=self.view(); _,discovery_sid=self.choose(discovery)
        held,_=self.view(split='holdout'); approve_fixture(self.c,held)
        chosen=build_selection(self.c,{**self.recipe,'pipeline_id':'mini-v1'})
        self.c.record('exposure',{'snapshot_id':discovery_sid,'scope':'another-experiment','split':'discovery'},records=[discovery_sid])
        from brrr_corpus.selection import check_exposure
        check_exposure(self.c,self.c.get(held)['spec'],'mini-experiment',graph(self.c)['groups'])
        self.c.record('exposure',{'snapshot_id':discovery_sid,'scope':'mini-experiment','split':'discovery'},records=[discovery_sid])
        with self.assertRaisesRegex(CorpusError,'KNOWN_DISCOVERY_EXPOSURE'):
            check_exposure(self.c,self.c.get(held)['spec'],'mini-experiment',graph(self.c)['groups'])
        self.assertIn('KNOWN_DISCOVERY_EXPOSURE',str(build_selection(self.c,self.recipe)['candidates']))

    def test_fixture_approval_never_passes_real_view(self):
        blob=self.c.put(b'Real reported observation.\n')
        source=self.c.record('source_revision',{'origin':'real','acquisition':'operator_supplied','body_blob':blob},[blob])
        case=save_case(self.c,{**self.spec,'key':'real/1','origin':'real','sources':[{'revision':source,'classification':'unreviewed'}]})
        quote=save_claim(self.c,{'case_revision':case['case_revision'],'classification':'candidate_public','segment':{'kind':'reporter_observation','source_revision':source,'start':0,'end':len(self.c.read(blob))},'rationale':'Mixed original, exact reported range.'})
        config={'case_revision':case['case_revision'],'pipeline_id':'mini-v1','split':'discovery','sections':{n:[quote] for n in ('TASK.md','OBSERVED.md','COMMANDS.md')}}
        view=reprocess(self.c,config,self.recipe['view_recipe'])['view_id']
        with self.assertRaisesRegex(CorpusError,'human content review'):
            approve_fixture(self.c,view)
        review_package(self.c,view,self.root/'private')
        pending=json.loads((self.root/'private/review-quality.PENDING.json').read_bytes())
        self.assertEqual(pending['verdict'],'PENDING')
        self.assertFalse(any(pending['attestations'].values()))
        with self.assertRaises(CorpusError):
            seal(self.c,[view])

    def test_demo_completes_and_repeats_without_network(self):
        with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
            report=run_demo(self.root/'demo')
            self.assertTrue(report['offline_restore_and_export_verified'])
            self.assertEqual(report['searchable_sources'],3)
            self.assertEqual(report['human_reviews'],0)
            self.assertEqual(len(report['files']['two']),8)
            again=run_demo(self.root/'demo')
            self.assertTrue(again['reused'])
            self.assertEqual(report['snapshots'],again['snapshots'])


if __name__ == '__main__':
    unittest.main()
