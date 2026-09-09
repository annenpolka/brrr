"""Offline discovery of immutable source revisions; searches never imply approval."""
import json
import re
from .store import require


def show_source(c, revision):
    source = c.get(revision, 'source_revision')
    observations = []
    for row in c.db.execute("SELECT id FROM records WHERE kind='source_observation' ORDER BY id"):
        item = c.get(row[0], 'source_observation')
        if item.get('source_revision') == revision:
            observations.append({'id': row[0], **item})
    return {'revision': revision, 'source': source,
            'body': c.read(source['body_blob']).decode('utf-8'),
            'resource': json.loads(c.read(source['resource_blob'])) if source.get('resource_blob') else None,
            'observations': observations, 'quality': 'PENDING_UNLESS_VIEW_REVIEWED'}


def sources(c, *, query='', repository='', kind='', origin='', limit=50):
    require(type(limit) is int and 1 <= limit <= 10000, 'limit must be between 1 and 10000')
    matches = []
    revisions = [(r[0], c.get(r[0], 'source_revision')) for r in c.db.execute("SELECT id FROM records WHERE kind='source_revision' ORDER BY id")]
    pull_urls = {}
    for _, source in revisions:
        if source.get('provider') == 'github' and source.get('resource_kind') == 'pull_request' and source.get('url'):
            pull_urls.setdefault((source['origin'], str(source['provider_id'])), set()).add(source['url'])
    for rid, source in revisions:
        body = c.read(source['body_blob']).decode('utf-8')
        resource = json.loads(c.read(source['resource_blob'])) if source.get('resource_blob') else {}
        url = source.get('url') or resource.get('html_url') or ''
        identity = re.fullmatch(r'pull:(\d+):file:.+', str(source.get('provider_id', '')))
        related = sorted(pull_urls.get((source['origin'], identity[1]), [])) if identity and source.get('provider') == 'github' else []
        if kind and source.get('resource_kind') != kind:
            continue
        if origin and source.get('origin') != origin:
            continue
        if repository and not any(f'/{repository.casefold().strip("/")}/' in value.casefold() + '/' for value in [url, *related]):
            continue
        searchable = body + '\n' + json.dumps(resource, ensure_ascii=False) + '\n' + url + '\n' + '\n'.join(related)
        if query.casefold() not in searchable.casefold():
            continue
        matches.append({'revision': rid, 'source_id': source.get('source_id'),
                        'kind': source.get('resource_kind'), 'origin': source.get('origin'),
                        'url': url, 'related_pull_urls': related, 'title': resource.get('title', resource.get('filename')),
                        'body_bytes': len(body.encode('utf-8')), 'preview': body[:240]})
    return {'matches': matches[:limit], 'total': len(matches), 'truncated': len(matches) > limit,
            'revision_policy': 'all stored revisions; no newest-version inference'}


def review_package(c, view_id, output):
    from .boundary import validate_view
    from .store import canonical, publish_tree
    view = validate_view(c, view_id)
    files = {f'public/{name}': c.read(blob) for name, blob in view['files'].items()}
    files['PRIVATE-review-target.json'] = canonical({'view_id': view_id, **view})
    sources_to_show = set(view['source_revisions'])
    if view['spec'].get('derivation'):
        d = c.get(view['spec']['derivation'], 'derivation')
        files['PRIVATE-derivation.json'] = canonical(d)
        case = c.get(d['config']['case_revision'], 'case_revision')
        files['PRIVATE-case.json'] = canonical(case)
        sources_to_show.update(s['revision'] for s in case['sources'])
        claims = set(d['restriction_claims'])
        for ids in d['config']['sections'].values():
            claims.update(ids)
        for rid in claims:
            files[f'PRIVATE-claims/{rid}.json'] = canonical(c.get(rid, 'claim'))
    for blob in view['spec']['restricted_blobs']:
        files[f'PRIVATE-solution-context/{blob}.txt'] = c.read(blob)
    for rid in sources_to_show:
        source = show_source(c, rid)
        files[f'PRIVATE-sources/{rid}.json'] = canonical(source)
        files[f'PRIVATE-sources/{rid}.txt'] = source['body'].encode('utf-8')
    for kind in ('quality', 'leakage'):
        files[f'review-{kind}.PENDING.json'] = canonical({
            'view_id': view_id, 'kind': kind, 'verdict': 'PENDING', 'reviewer': 'REPLACE_WITH_YOUR_NAME',
            'reviewer_type': 'human', 'rationale': 'REPLACE_AFTER_READING_THE_FULL_PACKAGE',
            'attestations': {'full_bundle_read': False, 'provenance_checked': False,
                             'solution_context_checked': False}})
    files['README.txt'] = (
        'PRIVATE REVIEW PACKAGE. The public/ directory is a pending preview, not a sealed consumer input.\n'
        'Read the entire preview, original sources, quote ranges and restricted solution context.\n'
        'Copy review-*.PENDING.json outside this immutable package; record your own verdict and rationale.\n'
        'PASS requires human review and all three attestations true. Do not automate human approval.\n'
        'record-review --file <copy.json>, then select --recipe <selection.json>, then seal-selection <id>.\n'
    ).encode('utf-8')
    return {'view_id': view_id, 'private_review_package': str(output), 'reused': publish_tree(output, files)}
