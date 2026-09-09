"""Small, explicit Case/Claim ledger and deterministic source-range rendering."""
from pathlib import Path
import uuid

from .store import canonical, digest, keys, nonempty, require

CLASSES = ('candidate_public', 'unreviewed', 'restricted_solution',
           'restricted_evaluation', 'restricted_prior_ideas')
RELATIONS = ('same_incident', 'derived_from', 'possible_duplicate', 'same_mechanism')


def setup(c):
    c.db.executescript('''
        CREATE TABLE IF NOT EXISTS case_keys (
            key TEXT PRIMARY KEY, case_id TEXT UNIQUE NOT NULL);
        CREATE TABLE IF NOT EXISTS case_events (
            seq INTEGER PRIMARY KEY, case_id TEXT NOT NULL,
            record_id TEXT NOT NULL REFERENCES records(id));
        CREATE TABLE IF NOT EXISTS relation_events (
            seq INTEGER PRIMARY KEY, record_id TEXT NOT NULL REFERENCES records(id));
    ''')


def current_cases(c):
    setup(c)
    return {r['case_id']: r['record_id'] for r in c.db.execute('''
        SELECT case_id, record_id FROM case_events WHERE seq IN
        (SELECT max(seq) FROM case_events GROUP BY case_id)''')}


def save_case(c, spec):
    setup(c)
    keys(spec, ['key', 'title', 'repository', 'origin', 'sources', 'primary_mechanism',
                'exposure', 'legacy_revisions', 'forbidden_identifiers'])
    for field in ('key', 'title', 'repository', 'primary_mechanism'):
        nonempty(spec[field], field)
    require(spec['origin'] in ('real', 'synthetic'), 'Invalid case origin')
    require(spec['exposure'] in ('unknown', 'unexposed', 'discovery'), 'Invalid exposure')
    require(isinstance(spec['sources'], list) and spec['sources'], 'Case needs sources')
    require(isinstance(spec['legacy_revisions'], list), 'Invalid legacy references')
    require(isinstance(spec['forbidden_identifiers'], list), 'Invalid identifiers')
    for identifier in spec['forbidden_identifiers']:
        nonempty(identifier, 'identifier')
    refs = []
    for item in spec['sources']:
        keys(item, ['revision', 'classification'])
        require(item['classification'] in CLASSES, 'Invalid source classification')
        source = c.get(item['revision'], 'source_revision')
        require(source['origin'] == spec['origin'], 'Mixed case/source origins')
        refs.append(item['revision'])
    require(len(refs) == len(set(refs)), 'Duplicate case source')
    legacy_ids = {c.get(rid, 'legacy_case_revision')['case_id'] for rid in spec['legacy_revisions']}
    require(len(legacy_ids) <= 1, 'Multiple legacy identities: register separately and relate Cases')
    require(not legacy_ids or spec['origin'] == 'real', 'Legacy identity cannot become synthetic')
    with c.transaction():
        row = c.db.execute('SELECT case_id FROM case_keys WHERE key=?', (spec['key'],)).fetchone()
        case_id = row[0] if row else (next(iter(legacy_ids)) if legacy_ids else str(uuid.uuid4()))
        require(not legacy_ids or legacy_ids == {case_id}, 'Legacy mapping would change Case identity')
        previous = c.db.execute('SELECT record_id FROM case_events WHERE case_id=? ORDER BY seq DESC LIMIT 1', (case_id,)).fetchone()
        if previous:
            require(c.get(previous[0], 'case_revision')['origin'] == spec['origin'], 'Case origin cannot change')
        if row is None:
            c.db.execute('INSERT INTO case_keys VALUES (?, ?)', (spec['key'], case_id))
        normalized = {**spec, 'repository': spec['repository'].lower(),
                      'sources': sorted(spec['sources'], key=lambda s: s['revision']),
                      'legacy_revisions': sorted(set(spec['legacy_revisions'])),
                      'forbidden_identifiers': sorted(set(spec['forbidden_identifiers']))}
        rid = c.record('case_revision', {'schema_version': 1, 'case_id': case_id, **normalized},
                       records=[*refs, *normalized['legacy_revisions']])
        latest = c.db.execute('SELECT record_id FROM case_events WHERE case_id=? ORDER BY seq DESC LIMIT 1', (case_id,)).fetchone()
        if latest is None or latest[0] != rid:
            c.db.execute('INSERT INTO case_events(case_id,record_id) VALUES (?,?)', (case_id, rid))
    return {'case_id': case_id, 'case_revision': rid}


def relate(c, spec):
    setup(c)
    keys(spec, ['left', 'right', 'kind', 'active', 'rationale', 'reviewer'])
    for field in ('rationale', 'reviewer'):
        nonempty(spec[field], field)
    require(spec['kind'] in RELATIONS and type(spec['active']) is bool, 'Invalid relation')
    current = current_cases(c)
    require(spec['left'] != spec['right'] and {spec['left'], spec['right']} <= current.keys(), 'Unknown or self relation')
    # Direction matters for derived_from; other relations are symmetric.
    left, right = (spec['left'], spec['right']) if spec['kind'] == 'derived_from' else sorted((spec['left'], spec['right']))
    with c.transaction():
        rid = c.record('case_relation', {**spec, 'left': left, 'right': right},
                       records=[current[left], current[right]])
        c.db.execute('INSERT INTO relation_events(record_id) VALUES (?)', (rid,))
    return rid


def graph(c):
    current = current_cases(c)
    latest = {}
    for row in c.db.execute('SELECT record_id FROM relation_events ORDER BY seq'):
        r = c.get(row[0], 'case_relation')
        latest[(r['left'], r['right'], r['kind'])] = (row[0], r)
    parent = {cid: cid for cid in current}
    def find(cid):
        while parent[cid] != cid:
            cid = parent[cid]
        return cid
    for _, r in latest.values():
        if r['active'] and r['kind'] != 'same_mechanism':
            a, b = find(r['left']), find(r['right'])
            parent[max(a, b)] = min(a, b)
    return {'current_cases': current, 'relations': sorted(rid for rid, _ in latest.values()),
            'groups': {cid: find(cid) for cid in current}}


def save_claim(c, spec):
    keys(spec, ['case_revision', 'classification', 'segment', 'rationale'])
    case = c.get(spec['case_revision'], 'case_revision')
    require(spec['classification'] in CLASSES, 'Invalid claim classification')
    nonempty(spec['rationale'], 'rationale')
    segment = spec['segment']
    from .boundary import build_artifact
    _, refs = build_artifact(c, {'path': 'TASK.md', 'segments': [segment]}, case['origin'])
    allowed = {s['revision']: s['classification'] for s in case['sources']}
    for rid in refs:
        require(rid in allowed, 'Source does not belong to Case revision')
        require(not allowed[rid].startswith('restricted_') or spec['classification'] == allowed[rid],
                'Restricted source cannot be downgraded to public Claim')
    if not refs:
        require(spec['classification'] == 'candidate_public', 'Generated prompts must be explicitly public questions')
    with c.transaction():
        return c.record('claim', {'schema_version': 1, **spec}, records=[spec['case_revision'], *refs])


def pipeline_hash():
    return digest(Path(__file__).read_bytes())


def reprocess(c, config, recipe):
    keys(config, ['case_revision', 'pipeline_id', 'split', 'sections'])
    case = c.get(config['case_revision'], 'case_revision')
    nonempty(config['pipeline_id'], 'pipeline_id')
    require(config['split'] in ('discovery', 'holdout'), 'Invalid split')
    require(isinstance(config['sections'], dict), 'Invalid sections')
    artifacts, claims = [], []
    for path, ids in sorted(config['sections'].items()):
        require(isinstance(ids, list) and ids, 'Missing claims for section')
        segments = []
        for rid in ids:
            claim = c.get(rid, 'claim')
            require(claim['case_revision'] == config['case_revision'], 'Claim belongs to different Case revision')
            require(claim['classification'] == 'candidate_public', 'Restricted or unreviewed Claim cannot enter view')
            segments.append(claim['segment'])
            claims.append(rid)
        artifacts.append({'path': path, 'segments': segments})
    restricted = [c.get(s['revision'], 'source_revision')['body_blob'] for s in case['sources']
                  if s['classification'].startswith('restricted_')]
    # Include restricted spans from mixed sources, even when not selected for a section.
    restriction_claims = []
    for row in c.db.execute("SELECT id FROM records WHERE kind='claim' ORDER BY id"):
        claim = c.get(row[0], 'claim')
        if claim['case_revision'] == config['case_revision'] and claim['classification'].startswith('restricted_'):
            from .boundary import build_artifact
            data, _ = build_artifact(c, {'path': 'TASK.md', 'segments': [claim['segment']]}, case['origin'])
            restricted.append(c.put(data))
            restriction_claims.append(row[0])
    with c.transaction():
        derivation = c.record('derivation', {'schema_version': 1, 'config': config,
                             'pipeline_hash': pipeline_hash(), 'restriction_claims': restriction_claims},
                             records=[config['case_revision'], *claims, *restriction_claims])
    from .boundary import stage_view
    vid = stage_view(c, {'schema_version': 1, 'origin': case['origin'], 'case_id': case['case_id'],
                        'lineage_group': case['case_id'], 'repository': case['repository'],
                        'primary_mechanism': case['primary_mechanism'], 'split': config['split'],
                        'exposure': case['exposure'], 'mode': 'blind_problem', 'artifacts': artifacts,
                        'restricted_blobs': sorted(set(restricted)),
                        'forbidden_identifiers': case['forbidden_identifiers'], 'derivation': derivation}, recipe)
    return {'view_id': vid, 'derivation': derivation, 'quality': 'PENDING_UNLESS_ALREADY_REVIEWED',
            'leakage': 'PENDING_UNLESS_ALREADY_REVIEWED'}


def validate_derivation(c, spec):
    """Do not let a manually staged view borrow another derivation's identity."""
    d = c.get(spec['derivation'], 'derivation')
    require(d['pipeline_hash'] == pipeline_hash(), 'Pipeline changed: reprocess and review required')
    config = d['config']
    case = c.get(config['case_revision'], 'case_revision')
    for field in ('case_id', 'origin', 'repository', 'primary_mechanism', 'exposure', 'forbidden_identifiers'):
        require(spec[field] == case[field], 'View differs from derivation Case')
    require(spec['split'] == config['split'] and spec['lineage_group'] == case['case_id'], 'View differs from derivation split/identity')
    artifacts = []
    for path, ids in sorted(config['sections'].items()):
        segments = []
        for rid in ids:
            claim = c.get(rid, 'claim')
            require(claim['case_revision'] == config['case_revision'] and claim['classification'] == 'candidate_public', 'Invalid derivation claim')
            segments.append(claim['segment'])
        artifacts.append({'path': path, 'segments': segments})
    require(spec['artifacts'] == artifacts, 'View differs from derivation content')
    restricted = {c.get(s['revision'], 'source_revision')['body_blob'] for s in case['sources']
                  if s['classification'].startswith('restricted_')}
    restriction_claims = []
    from .boundary import build_artifact
    for row in c.db.execute("SELECT id FROM records WHERE kind='claim' ORDER BY id"):
        claim = c.get(row[0], 'claim')
        if claim['case_revision'] == config['case_revision'] and claim['classification'].startswith('restricted_'):
            data, _ = build_artifact(c, {'path': 'TASK.md', 'segments': [claim['segment']]}, case['origin'])
            restricted.add(digest(data))
            restriction_claims.append(row[0])
    require(d['restriction_claims'] == restriction_claims and set(spec['restricted_blobs']) == restricted,
            'Restriction context changed: reprocess and review required')
    return d
