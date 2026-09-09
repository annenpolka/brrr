"""Drive shipped collection/selection functions for the other-ecosystems small recipe."""
import json
import tempfile
import unittest
from pathlib import Path

from brrr_corpus.boundary import validate_recipe as validate_view_recipe
from brrr_corpus.collection_plan import make_plan, validate_collection_recipe
from brrr_corpus.selection import build_selection, validate_recipe as validate_selection_recipe
from brrr_corpus.store import Corpus, CorpusError

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = json.loads((ROOT / 'recipes/collection/github-other-ecosystems-v1.json').read_text())
SELECTION = json.loads((ROOT / 'recipes/selection/github-other-ecosystems-v1.json').read_text())


class OtherEcosystemsRecipeTests(unittest.TestCase):
    def test_collection_recipe_caps_and_excludes_pytest(self):
        validate_collection_recipe(COLLECTION)
        self.assertEqual(COLLECTION['recipe_id'], 'github-other-ecosystems-v1')
        repos = COLLECTION['repositories']
        self.assertEqual(repos, ['rust-lang/cargo', 'astral-sh/uv', 'npm/cli', 'microsoft/TypeScript'])
        self.assertNotIn('pytest-dev/pytest', repos)
        self.assertLessEqual(COLLECTION['limits']['total_requests'], 400)
        self.assertEqual(COLLECTION['limits']['resources'], 16)
        self.assertFalse(COLLECTION['include_legacy'])
        for lane in COLLECTION['lanes']:
            self.assertLessEqual(lane['max_resources'], 4)

    def test_make_plan_queries_only_listed_repositories(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = Corpus(Path(tmp).resolve() / 'corpus')
            self.addCleanup(c.close)
            pid = make_plan(c, COLLECTION)
            plan = c.get(pid)
            repos = {q['repository'] for q in plan['queries']}
            self.assertEqual(repos, set(COLLECTION['repositories']))
            self.assertNotIn('pytest-dev/pytest', repos)
            self.assertLessEqual(len(plan['queries']), COLLECTION['limits']['search_partitions'])

    def test_selection_delegation_counts_and_shortfall_on_empty_corpus(self):
        validate_selection_recipe(SELECTION)
        view = SELECTION['view_recipe']
        validate_view_recipe(view)
        self.assertEqual(view['delegated_review']['reviewer'], 'Codex')
        self.assertTrue(view['delegated_review']['authorization'])
        self.assertEqual(SELECTION['target_cases'], 3)
        self.assertEqual(SELECTION['max_cases_per_repository'], 1)
        self.assertEqual(SELECTION['max_cases_per_primary_mechanism'], 1)
        self.assertTrue(SELECTION['allow_shortfall'])
        self.assertTrue(view['allow_shortfall'])
        with tempfile.TemporaryDirectory() as tmp:
            c = Corpus(Path(tmp).resolve() / 'corpus')
            self.addCleanup(c.close)
            result = build_selection(c, SELECTION)
            self.assertEqual(result['shortfall'], 3)
            self.assertEqual(result['selected'], [])
            self.assertEqual(result['status'], 'HOLD')

    def test_selection_cannot_relax_view_shortfall(self):
        bad = json.loads(json.dumps(SELECTION))
        bad['view_recipe']['allow_shortfall'] = False
        bad['allow_shortfall'] = True
        with self.assertRaises(CorpusError):
            validate_selection_recipe(bad)


if __name__ == '__main__':
    unittest.main()
