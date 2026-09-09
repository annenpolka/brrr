"""Offline, explicitly synthetic vertical slice. No fabricated human review."""
import json
import os
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .boundary import export_snapshot, review, seal
from .cases import reprocess, relate, save_case, save_claim
from .catalog import review_package, sources
from .collection import run_collection, start_collection
from .collection_plan import make_plan
from .github_http import Response
from .selection import build_selection
from .store import Corpus, canonical, digest, no_symlink_components, require, restore_backup

REPO = Path(__file__).resolve().parents[2]


def recipe_file(relative):
    return json.loads((REPO / relative).read_bytes())


class FixtureClock:
    value = 1788912000.0

    def __call__(self):
        return self.value

    def sleep(self, seconds):
        self.value += seconds


class FixtureHTTP:
    """Only this in-memory fixture transport is used by mini-demo."""
    calls = 0

    @staticmethod
    def issue(number):
        reports = {
            1: 'SYNTHETIC REPORT A\n$ sample sync\nFirst invocation exits 0; the second exits 1.\n',
            2: 'SYNTHETIC REPORT B\n$ sample inspect\nThe command prints a missing-object error.\n',
            3: 'SYNTHETIC REPORT C\n$ sample inspect\nAnother report of the missing-object error.\n',
        }
        return {'id': 9000 + number, 'number': number, 'body': reports[number],
                'title': f'Synthetic fixture {number}',
                'html_url': f'https://github.com/synthetic/repo/issues/{number}',
                'created_at': '2026-01-01T00:00:00Z', 'updated_at': '2026-01-01T00:00:00Z'}

    def get(self, url, **kwargs):
        self.calls += 1
        parsed = urlsplit(url)
        if parsed.path == '/versions':
            data = ['2026-03-10']
        elif parsed.path == '/repos/synthetic/repo':
            data = {'id': 900, 'private': False, 'full_name': 'synthetic/repo'}
        elif parsed.path == '/search/issues':
            items = [] if 'is:pr' in parse_qs(parsed.query)['q'][0] else [self.issue(i) for i in range(1, 4)]
            data = {'items': items, 'total_count': len(items), 'incomplete_results': False}
        elif parsed.path.endswith(('/comments', '/timeline')):
            data = []
        elif parsed.path.startswith('/repos/synthetic/repo/issues/'):
            data = self.issue(int(parsed.path.rsplit('/', 1)[1]))
        else:
            raise AssertionError(f'Unexpected fixture request: {url}')
        return Response(200, {}, canonical(data), origin='synthetic')


def approve_fixture(c, vid):
    for kind in ('quality', 'leakage'):
        review(c, vid, kind=kind, verdict='PASS', reviewer='mini-demo-fixture',
               reviewer_type='fixture', rationale='Synthetic pipeline exercise only; no human approval claimed.',
               attestations={'full_bundle_read': True, 'provenance_checked': True, 'solution_context_checked': True})


def add_prompt(c, case_revision, text):
    return save_claim(c, {'case_revision': case_revision, 'classification': 'candidate_public',
                         'segment': {'kind': 'generated_prompt', 'text': text},
                         'rationale': 'Explicit investigation question; not an observed fact.'})


def demo_fingerprint():
    paths = [*Path(__file__).parent.glob('*.py'), REPO / 'recipes/collection/mini-offline-v1.json',
             REPO / 'recipes/selection/mini-one-v1.json', REPO / 'recipes/selection/mini-two-v1.json']
    return digest(canonical({str(p.relative_to(REPO)): digest(p.read_bytes()) for p in sorted(paths)}))


def verify_demo(root):
    report = json.loads((root / 'report.json').read_bytes())
    require(report['fingerprint'] == demo_fingerprint(), 'Demo code changed; use a new output directory')
    for corpus_dir, suffix in [('corpus', ''), ('restored', '-restored')]:
        c = Corpus(root / corpus_dir)
        try:
            require(c.audit()['ok'], 'Demo audit failed')
            for name, snapshot in report['snapshots'].items():
                result = export_snapshot(c, snapshot, root / ('export-' + name + suffix))
                require(result['files'] == report['files'][name], 'Re-export differs')
        finally:
            c.close()
    return {**report, 'output': str(root), 'reused': True}


def run_demo(output):
    dest = no_symlink_components(output)
    if dest.exists():
        require((dest / 'report.json').is_file(), 'Existing output is not a completed mini-demo; use a new directory')
        return verify_demo(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.mini-demo-', dir=dest.parent) as temporary:
        work = Path(temporary).resolve()
        c = Corpus(work / 'corpus')
        try:
            http, clock = FixtureHTTP(), FixtureClock()
            plan = make_plan(c, recipe_file('recipes/collection/mini-offline-v1.json'))
            cid = start_collection(c, plan, now=clock())
            partial = run_collection(c, cid, transport=http, clock=clock, sleep=clock.sleep, max_requests=2)
            require(partial['state'] == 'INCOMPLETE', 'Expected resumable invocation limit')
            collected = run_collection(c, cid, transport=http, clock=clock, sleep=clock.sleep)
            require(collected['state'] == 'COMPLETE_FOR_POLICY', 'Fixture collection did not complete')
            repeated = run_collection(c, cid, transport=http, clock=clock, sleep=clock.sleep)
            require(repeated['requests_this_invocation'] == 0, 'Repeated collection made extra requests')
            found = sources(c, query='SYNTHETIC REPORT', kind='issue', origin='synthetic')
            require(found['total'] == 3, 'Expected three searchable fixture reports')
            first_recipe = recipe_file('recipes/selection/mini-two-v1.json')
            cases, configs, views = [], [], []
            for i, source in enumerate(sorted(found['matches'], key=lambda s: s['url']), 1):
                case = save_case(c, {'key': f'mini/{i}', 'title': f'Synthetic case {i}',
                                 'repository': 'synthetic/repo', 'origin': 'synthetic',
                                 'sources': [{'revision': source['revision'], 'classification': 'candidate_public'}],
                                 'primary_mechanism': 'unknown', 'exposure': 'unexposed',
                                 'legacy_revisions': [], 'forbidden_identifiers': []})
                observation = save_claim(c, {'case_revision': case['case_revision'], 'classification': 'candidate_public',
                            'segment': {'kind': 'reporter_observation', 'source_revision': source['revision'],
                                        'start': 0, 'end': source['body_bytes']}, 'rationale': 'Complete synthetic report.'})
                question = add_prompt(c, case['case_revision'], 'Which observations would distinguish the failing invocation?\n')
                commands = add_prompt(c, case['case_revision'], 'The command in the report was not executed by this collector.\n')
                config = {'case_revision': case['case_revision'], 'pipeline_id': 'mini-v1',
                          'split': 'discovery' if i == 1 else 'holdout',
                          'sections': {'TASK.md': [question], 'OBSERVED.md': [observation], 'COMMANDS.md': [commands]}}
                view = reprocess(c, config, first_recipe['view_recipe'])['view_id']
                require(reprocess(c, config, first_recipe['view_recipe'])['view_id'] == view, 'Non-idempotent rendering')
                cases.append(case)
                configs.append(config)
                views.append(view)
                review_package(c, view, work / f'review-{i}')
            relate(c, {'left': cases[1]['case_id'], 'right': cases[2]['case_id'], 'kind': 'same_incident',
                       'active': True, 'reviewer': 'synthetic-fixture', 'rationale': 'Fixture B/C are duplicate reports.'})
            relate(c, {'left': cases[0]['case_id'], 'right': cases[1]['case_id'], 'kind': 'same_mechanism',
                       'active': True, 'reviewer': 'synthetic-fixture', 'rationale': 'Fixture label; not same incident.'})
            pending = build_selection(c, first_recipe)
            require(pending['status'] == 'HOLD' and len(pending['candidates']) == 3, 'Pending views escaped review gate')
            for vid in views:
                approve_fixture(c, vid)
            selections, snapshots, files = {}, {}, {}
            for name, recipe_path in [('two', 'recipes/selection/mini-two-v1.json'), ('one', 'recipes/selection/mini-one-v1.json')]:
                recipe = recipe_file(recipe_path)
                chosen = build_selection(c, recipe)
                require(chosen['status'] == 'READY', 'Fixture selection failed')
                selections[name] = chosen['selection_id']
                snapshots[name] = seal(c, chosen['selected'], chosen['selection_id'])
                files[name] = export_snapshot(c, snapshots[name], work / ('export-' + name))['files']
                (work / ('selection-' + name + '.json')).write_bytes(canonical(chosen))
            changed_question = add_prompt(c, cases[0]['case_revision'], 'Which before/after evidence would narrow this report?\n')
            changed_config = {**configs[0], 'pipeline_id': 'mini-v2',
                              'sections': {**configs[0]['sections'], 'TASK.md': [changed_question]}}
            changed = reprocess(c, changed_config, first_recipe['view_recipe'])['view_id']
            changed_selection = build_selection(c, {**first_recipe, 'pipeline_id': 'mini-v2', 'target_cases': 1})
            require(changed != views[0] and changed_selection['status'] == 'HOLD', 'Reprocessed view reused prior PASS')
            c.backup(work / 'backup')
            audit = c.audit()
        finally:
            c.close()
        restore_backup(work / 'backup', work / 'restored')
        report = {'schema_version': 1, 'fixture_only': True, 'human_reviews': 0,
                  'fingerprint': demo_fingerprint(), 'collection_id': cid,
                  'collection_state': collected['state'], 'fixture_http_requests': http.calls,
                  'searchable_sources': found['total'], 'cases': cases, 'views': views,
                  'pending_selection': pending['selection_id'], 'selections': selections,
                  'snapshots': snapshots, 'files': files, 'reprocessed_pending_view': changed,
                  'audit': audit, 'offline_restore_and_export_verified': True}
        (work / 'report.json').write_bytes(canonical(report))
        verify_demo(work)
        require(not dest.exists(), 'Output appeared during demo; refusing overwrite')
        os.rename(work, dest)
    return {**report, 'output': str(dest), 'reused': False}
