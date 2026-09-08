import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CLI = Path(__file__).resolve().parents[1] / 'scripts/corpus.py'


class CliTests(unittest.TestCase):
    def test_synthetic_cli_roundtrip(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            corpus = root / 'corpus'

            def call(*args, expected=0):
                result = subprocess.run([sys.executable, str(CLI), '--root', str(corpus), *map(str, args)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stderr)
                return json.loads(result.stdout or result.stderr)

            def save(name, data):
                p = root / name
                p.write_text(json.dumps(data))
                return p

            original = root / 'source.txt'
            original.write_text('Synthetic CLI fixture reports exit status 1.\n')
            meta = save('metadata.json', {
                'schema_version': 1, 'origin': 'synthetic', 'provider': 'synthetic',
                'resource_kind': 'issue', 'provider_id': '1', 'url': 'https://example.invalid/1',
                'observed_at': '2026-09-09T00:00:00Z', 'provider_created_at': None,
                'provider_updated_at': None, 'content_available_at': None,
            })
            source = call('import-source', '--file', original, '--metadata', meta)
            recipe = save('recipe.json', {
                'schema_version': 1, 'recipe_id': 'synthetic', 'view_mode': 'blind_problem',
                'target_cases': 1, 'max_cases_per_repository': 1, 'max_cases_per_primary_mechanism': 1,
                'allow_synthetic': True, 'allow_shortfall': False, 'prior_ideas_access': 'denied',
                'isolation_level': 'static_bundle_only',
            })
            spec = save('view.json', {
                'schema_version': 1, 'origin': 'synthetic', 'mode': 'blind_problem',
                'case_id': 'synthetic-case', 'lineage_group': 'synthetic-group', 'repository': 'synthetic/repo',
                'primary_mechanism': 'unknown', 'split': 'discovery', 'exposure': 'unknown',
                'restricted_blobs': [], 'forbidden_identifiers': [],
                'artifacts': [{'path': name, 'segments': [{
                    'kind': 'reporter_observation', 'source_revision': source['source_revision'],
                    'start': 0, 'end': len(original.read_bytes()),
                }]} for name in ('TASK.md', 'OBSERVED.md', 'COMMANDS.md')],
            })
            view = call('stage-view', '--spec', spec, '--recipe', recipe)['view_id']
            call('seal', '--view', view, expected=1)
            call('inspect-view', view, '--output', root / 'review-package')
            self.assertTrue((root / 'review-package/PRIVATE-review-target.json').is_file())
            for kind in ('quality', 'leakage'):
                record = save(f'{kind}.json', {
                    'view_id': view, 'kind': kind, 'verdict': 'PASS', 'reviewer': 'test-human',
                    'reviewer_type': 'human', 'rationale': 'Synthetic fixture only.',
                    'attestations': {'full_bundle_read': True, 'provenance_checked': True,
                                     'solution_context_checked': True},
                })
                call('record-review', '--file', record)
            self.assertEqual(call('stage-view', '--spec', spec, '--recipe', recipe)['quality'], 'PASS')
            snapshot = call('seal', '--view', view)['snapshot_id']
            call('export', snapshot, '--output', root / 'public')
            self.assertTrue(call('export', snapshot, '--output', root / 'public')['reused'])
            self.assertFalse(any(p.name.startswith('PRIVATE') for p in (root / 'public').rglob('*')))
            call('record-exposure', snapshot, '--consumer', 'synthetic-test', '--scope', 'synthetic-test')
            self.assertTrue(call('audit')['ok'])
            call('revoke', snapshot, '--reason', 'Synthetic revocation test')
            call('export', snapshot, '--output', root / 'public', expected=1)

    def test_dry_run_creates_no_corpus(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            packet = root / 'synthetic-run/specimens/specimen-001'
            packet.mkdir(parents=True)
            (packet / 'packet.json').write_text(json.dumps({
                'id': 'specimen-001', 'manifest': 'kind: SYNTHETIC_GROUNDED\nrepository: synthetic/repo\n',
            }))
            corpus = root / 'must-not-exist'
            result = subprocess.run([sys.executable, str(CLI), '--root', str(corpus), 'import-legacy',
                                     '--run', str(root / 'synthetic-run'), '--dry-run'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)['dry_run'])
            self.assertFalse(corpus.exists())


if __name__ == '__main__':
    unittest.main()
