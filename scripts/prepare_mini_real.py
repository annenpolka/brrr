#!/usr/bin/env python3
"""Prepare two PENDING views from the bounded deno PR example; never approves or exports."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from brrr_corpus.boundary import seal
from brrr_corpus.cases import reprocess, save_case, save_claim
from brrr_corpus.catalog import review_package, show_source, sources
from brrr_corpus.mini import add_prompt, recipe_file
from brrr_corpus.selection import build_selection
from brrr_corpus.store import Corpus, CorpusError, canonical, no_symlink_components, publish_tree, require


def prepare(root, output):
    require((Path(root) / 'corpus.sqlite').is_file(), 'Collect recipes/collection/mini-reuse-sources-v1.json first')
    dest = no_symlink_components(output)
    c = Corpus(root)
    try:
        matches = sources(c, repository='denoland/deno', kind='pull_request', origin='real')['matches']
        matches = [s for s in matches if s['url'] == 'https://github.com/denoland/deno/pull/30998']
        require(len(matches) == 1, 'Expected exactly one consumer PR revision; select a revision explicitly if refreshed')
        source = show_source(c, matches[0]['revision'])
        raw = source['body'].encode('utf-8')
        start = raw.find(b'```')
        end = raw.find(b'```', start + 3)
        require(start >= 0 and end > start and b'> deno i' in raw[start:end]
                and b'Failed reading lockfile' in raw[start:end], 'Original report changed; review quote ranges manually')
        end += 3
        all_sources = sources(c, origin='real', limit=10000)
        require(not all_sources['truncated'], 'Too many sources for this small example')
        refs = []
        # Only the two collected roots are admitted. Issue copies and comments remain review context.
        for item in all_sources['matches']:
            data = show_source(c, item['revision'])
            url = item['url']
            allowed_url = any(url.startswith(prefix) for prefix in (
                'https://github.com/denoland/deno/pull/30998',
                'https://github.com/denoland/deno/issues/30998',
                'https://github.com/denoland/deno_lockfile/pull/62',
                'https://github.com/denoland/deno_lockfile/issues/62'))
            if not allowed_url and not (item['kind'] == 'pr_file' and any(
                    url in ('https://github.com/denoland/deno/pull/30998',
                            'https://github.com/denoland/deno_lockfile/pull/62')
                    for url in item['related_pull_urls'])):
                continue
            classification = 'restricted_solution' if item['kind'] in ('pr_file','pr_review','pr_review_comment') else 'unreviewed'
            refs.append({'revision': item['revision'], 'classification': classification})
        require(sum(c.get(s['revision'], 'source_revision')['resource_kind'] == 'pr_file' for s in refs) >= 2,
                'Missing collected patch context for the two PRs')
        require(matches[0]['revision'] in {s['revision'] for s in refs}, 'Missing original symptom source')
        spec = {'key': 'mini-real/deno-lockfile-reading', 'title': 'Reported lockfile reading failure',
                'repository': 'denoland/deno', 'origin': 'real', 'sources': refs,
                'primary_mechanism': 'unknown', 'exposure': 'unknown', 'legacy_revisions': [],
                'forbidden_identifiers': ['https://github.com/denoland/deno/pull/30998',
                                          'https://github.com/denoland/deno_lockfile/pull/62']}
        case = save_case(c, spec)
        quote_spec = {'case_revision': case['case_revision'], 'classification': 'candidate_public',
                      'segment': {'kind': 'reporter_observation', 'source_revision': matches[0]['revision'],
                                  'start': start, 'end': end},
                      'rationale': 'Exact error block reported in original PR body; excludes solution link and efficacy claim. Pending human review.'}
        observation = save_claim(c, quote_spec)
        commands = add_prompt(c, case['case_revision'], 'The report names a command; it has not been executed here. What inputs and environment would be needed to repeat it?\n')
        views, selections, files = {}, {}, {'case.json': canonical(spec), 'observation-claim.json': canonical(quote_spec)}
        questions = {
            'v1': 'A lockfile could not be read in the supplied report. What evidence would narrow the invalid dependency entry?\n',
            'v2': 'What should be compared before and after the reported command to localize this failure, without assuming its cause?\n',
        }
        for variant, question in questions.items():
            recipe = recipe_file('recipes/selection/mini-real-' + variant + '.json')
            prompt = add_prompt(c, case['case_revision'], question)
            config = {'case_revision': case['case_revision'], 'pipeline_id': recipe['pipeline_id'], 'split': 'discovery',
                      'sections': {'TASK.md': [prompt], 'OBSERVED.md': [observation], 'COMMANDS.md': [commands]}}
            vid = reprocess(c, config, recipe['view_recipe'])['view_id']
            views[variant] = vid
            review_package(c, vid, dest / ('review-' + variant))
            selected = build_selection(c, recipe)
            selections[variant] = selected['selection_id']
            files['reprocess-' + variant + '.json'] = canonical(config)
            files['view-recipe-' + variant + '.json'] = canonical(recipe['view_recipe'])
            files['selection-' + variant + '.json'] = canonical(selected)
        pending = all(c.get(sid, 'selection_run')['status'] == 'HOLD' for sid in selections.values())
        blocked = None
        if pending:
            try:
                seal(c, c.get(selections['v1'], 'selection_run')['selected'], selections['v1'])
            except CorpusError as error:
                blocked = str(error)
            require(blocked is not None, 'Unreviewed real view escaped seal gate')
        report = {'case': case, 'source_count': len(refs), 'original_revision': matches[0]['revision'],
                  'quote_byte_range': [start, end], 'views': views, 'selections': selections,
                  'human_reviews_created': 0, 'all_selections_pending': pending, 'pending_seal_block': blocked,
                  'audit': c.audit(), 'private_output': str(dest)}
        files['report.json'] = canonical(report)
        files['README.txt'] = (
            'PRIVATE REAL-DATA PILOT: two variants of ONE incident, not two independent cases.\n'
            'Each review directory contains full original sources and restricted solution context.\n'
            'Review one or both variants. Copy and edit the PENDING review templates as a human.\n'
            'After record-review, run select with recipes/selection/mini-real-v1.json or mini-real-v2.json.\n'
            'Then seal-selection <new-selection-id> and export <snapshot-id> --output <new-directory>.\n'
            'Reprocess inputs are in inputs/. No local reproduction or human PASS is claimed.\n'
        ).encode('utf-8')
        publish_tree(dest / 'inputs', files)
        return report
    finally:
        c.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default='.brrr-corpus/mini-real')
    p.add_argument('--output', required=True)
    args = p.parse_args()
    try:
        print(json.dumps(prepare(args.root, args.output), ensure_ascii=False, indent=2))
    except (CorpusError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}), file=sys.stderr)
        sys.exit(1)
