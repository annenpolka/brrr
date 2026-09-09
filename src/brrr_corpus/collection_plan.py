"""Compile explicit recipes and legacy references into immutable offline plans."""
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode

from .store import canonical, digest, keys, nonempty, require


def implementation_hash():
    return digest(canonical({name: digest(Path(__file__).with_name(name).read_bytes())
                             for name in ('collection.py', 'collection_plan.py', 'github_http.py')}))


def validate_collection_recipe(r):
    keys(r, ['schema_version', 'recipe_id', 'api_version', 'repositories', 'window', 'lanes',
             'include_legacy', 'legacy_seed_limit', 'selection_seed', 'limits', 'http', 'acquisition'], ['seed_urls'])
    require(type(r['schema_version']) is int and r['schema_version'] == 1, 'Unsupported collection recipe')
    nonempty(r['recipe_id'], 'recipe_id')
    require(bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', r['api_version'])), 'API version must be pinned')
    require(isinstance(r['repositories'], list) and r['repositories'], 'Fixed repositories required')
    for repo in r['repositories']:
        require(isinstance(repo, str) and re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo), 'Invalid repository')
    require(len(set(x.lower() for x in r['repositories'])) == len(r['repositories']), 'Duplicate repository')
    keys(r['window'], ['start', 'end_exclusive'])
    require(date.fromisoformat(r['window']['start']) < date.fromisoformat(r['window']['end_exclusive']), 'Empty search window')
    require(type(r['include_legacy']) is bool, 'include_legacy must be boolean')
    require(type(r['legacy_seed_limit']) is int and r['legacy_seed_limit'] >= 0, 'Invalid seed limit')
    require(type(r['selection_seed']) is int, 'Invalid selection seed')
    require(isinstance(r.get('seed_urls', []), list), 'seed_urls must be a list')
    for url in r.get('seed_urls', []):
        require(isinstance(url, str) and re.fullmatch(r'https://github\.com/[\w.-]+/[\w.-]+/(issues|pull)/\d+', url), 'Invalid explicit seed URL')
    require(isinstance(r['lanes'], list) and r['lanes'], 'Missing search lanes')
    ids = []
    for lane in r['lanes']:
        keys(lane, ['id', 'terms', 'max_resources'])
        require(lane['id'] in ('mechanism', 'symptom', 'control'), 'Invalid lane')
        ids.append(lane['id'])
        require(isinstance(lane['terms'], list) and lane['terms'], 'Missing lexical terms')
        for term in lane['terms']:
            require(isinstance(term, str) and re.fullmatch(r'[A-Za-z0-9 _-]{1,80}', term), 'Only literal lexical terms supported')
        require(type(lane['max_resources']) is int and lane['max_resources'] > 0, 'Invalid lane budget')
    require(len(ids) == len(set(ids)), 'Duplicate lane')
    keys(r['limits'], ['total_requests', 'total_bytes', 'response_bytes', 'search_pages',
                       'resource_pages', 'search_partitions', 'min_partition_days', 'resources'])
    for name, value in r['limits'].items():
        require(type(value) is int and value > 0, f'Invalid limit: {name}')
    require(r['limits']['total_bytes'] >= r['limits']['response_bytes'], 'Byte budget below response reservation')
    keys(r['http'], ['concurrency', 'timeout_seconds', 'lease_seconds', 'retry_attempts',
                    'min_interval_seconds', 'search_interval_seconds'])
    require(r['http']['concurrency'] == 1, 'Only serialized HTTP is supported')
    for name, value in r['http'].items():
        require(type(value) in (int, float) and value > 0, f'Invalid HTTP setting: {name}')
    require(type(r['http']['retry_attempts']) is int, 'retry_attempts must be integer')
    require(r['http']['lease_seconds'] > r['http']['timeout_seconds'] + 5, 'Lease must exceed HTTP timeout')
    keys(r['acquisition'], ['issue_comments', 'pr_reviews', 'pr_files', 'timeline', 'related_depth', 'attachments'])
    for name in ('issue_comments', 'pr_reviews', 'pr_files', 'timeline'):
        require(type(r['acquisition'][name]) is bool, f'Invalid acquisition setting: {name}')
    require(type(r['acquisition']['related_depth']) is int and r['acquisition']['related_depth'] in (0, 1), 'Related depth is 0 or 1')
    require(r['acquisition']['attachments'] == 'record_only', 'Attachments are recorded, never fetched')


def search_url(spec):
    # Days form a half-open interval; GitHub created dates are inclusive.
    end = (date.fromisoformat(spec['end']) - timedelta(days=1)).isoformat()
    term = f'"{spec["term"]}"' if ' ' in spec['term'] else spec['term']
    query = f'repo:{spec["repository"]} is:{spec["resource_kind"]} is:public created:{spec["start"]}..{end} {term}'
    return 'https://api.github.com/search/issues?' + urlencode({'q': query, 'sort': 'created', 'order': 'asc', 'per_page': 100})


def make_plan(c, recipe):
    validate_collection_recipe(recipe)
    all_seeds = set()
    if recipe['include_legacy']:
        for row in c.db.execute("SELECT id FROM records WHERE kind='legacy_case_revision'"):
            all_seeds.update(c.get(row[0])['source_candidates'])
    # Deterministic round-robin by repository prevents the legacy lane monopolizing one ecosystem.
    buckets = defaultdict(list)
    for url in sorted(all_seeds):
        match = re.fullmatch(r'https://github\.com/([\w.-]+/[\w.-]+)/(issues|pull)/(\d+)', url)
        if match:
            repo, kind, number = match.groups()
            buckets[repo].append({'repository': repo, 'number': int(number), 'kind': kind, 'url': url})
    seeds = []
    while buckets and len(seeds) < recipe['legacy_seed_limit']:
        for repo in sorted(list(buckets)):
            if len(seeds) >= recipe['legacy_seed_limit']:
                break
            seeds.append(buckets[repo].pop(0))
            if not buckets[repo]:
                del buckets[repo]
    legacy_selected = len(seeds)
    for url in recipe.get('seed_urls', []):
        match = re.fullmatch(r'https://github\.com/([\w.-]+/[\w.-]+)/(issues|pull)/(\d+)', url)
        repo, kind, number = match.groups()
        if not any(s['repository'].lower() == repo.lower() and s['number'] == int(number) for s in seeds):
            seeds.append({'repository': repo, 'number': int(number), 'kind': kind, 'url': url})
    require(len(seeds) <= recipe['limits']['resources'], 'Seed count exceeds resource budget')
    queries = []
    # Interleave lanes so a bounded first invocation can reach every lane.
    for repo in recipe['repositories']:
        for lane in recipe['lanes']:
            for term in lane['terms']:
                for kind in ('issue', 'pr'):
                    queries.append({'repository': repo, 'lane': lane['id'], 'term': term,
                                    'resource_kind': kind, 'start': recipe['window']['start'],
                                    'end': recipe['window']['end_exclusive'], 'round': 0})
    require(len(queries) <= recipe['limits']['search_partitions'], 'Initial plan exceeds partition budget')
    payload = {'schema_version': 1, 'recipe': recipe, 'recipe_hash': digest(canonical(recipe)),
               'implementation_hash': implementation_hash(), 'seeds': seeds, 'queries': queries,
               'legacy_candidates': len(all_seeds), 'legacy_deferred_by_policy': len(all_seeds) - legacy_selected,
               'repositories': sorted(set(recipe['repositories']) | {s['repository'] for s in seeds}),
               'coverage_claim': 'bounded_public_search_results; not a census',
               'selection_method': 'fixed legacy round-robin; lane caps; seeded ordering within each search page',
               'refresh_policy': 'full fixed-window rescan plus all previously discovered resources'}
    with c.transaction():
        pid = c.record('collection_plan', payload)
    return pid
