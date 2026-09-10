"""Actionable HOLD records and the missing handoff to a private review package.

Recovery evidence is host-only. It neither creates source claims nor grants PASS.
"""
from .store import keys, nonempty, require


def setup(c):
    c.db.execute('''CREATE TABLE IF NOT EXISTS recovery_events (
        seq INTEGER PRIMARY KEY, case_id TEXT NOT NULL,
        record_id TEXT NOT NULL REFERENCES records(id))''')


def latest(c, case_id):
    setup(c)
    row = c.db.execute('SELECT record_id FROM recovery_events WHERE case_id=? ORDER BY seq DESC LIMIT 1',
                       (case_id,)).fetchone()
    return row[0] if row else None


def save(c, spec):
    from .cases import current_cases
    keys(spec, ['case_revision', 'owner', 'state', 'blockers'])
    case = c.get(spec['case_revision'], 'case_revision')
    require(current_cases(c)[case['case_id']] == spec['case_revision'], 'Case revision superseded')
    nonempty(spec['owner'], 'owner')
    require(spec['state'] in ('active', 'parked'), 'Invalid recovery state')
    require(isinstance(spec['blockers'], list), 'blockers must be a list')
    refs, ids = [spec['case_revision']], set()
    for b in spec['blockers']:
        keys(b, ['id', 'missing', 'next_action', 'acceptance', 'resolved', 'evidence'])
        for field in ('id', 'missing', 'next_action', 'acceptance'):
            nonempty(b[field], field)
        require(b['id'] not in ids, 'Duplicate blocker id')
        ids.add(b['id'])
        require(type(b['resolved']) is bool and isinstance(b['evidence'], list), 'Invalid blocker evidence')
        require(not b['resolved'] or b['evidence'], 'Resolved blocker needs immutable evidence records')
        for rid in b['evidence']:
            c.get(rid)
            refs.append(rid)
    previous = latest(c, case['case_id'])
    if previous:
        old = c.get(previous, 'recovery')
        require({b['id'] for b in old['blockers']} <= ids,
                'Do not delete blockers; resolve with evidence or park the case')
        refs.append(previous)
    with c.transaction():
        rid = c.record('recovery', {**spec, 'case_id': case['case_id'], 'previous': previous}, records=refs)
        c.db.execute('INSERT INTO recovery_events(case_id,record_id) VALUES (?,?)', (case['case_id'], rid))
    return {'recovery_id': rid, 'case_id': case['case_id'], 'next_action': next_action(spec)}


def next_action(spec):
    if spec['state'] == 'parked':
        return 'PARKED'
    if any(not b['resolved'] for b in spec['blockers']):
        return 'RESOLVE_BLOCKER'
    return 'PREPARE_REVIEW'


def status(c, case_id):
    rid = latest(c, case_id)
    require(rid is not None, 'No recovery record; register missing evidence and acceptance conditions')
    record = c.get(rid, 'recovery')
    return {'recovery_id': rid, **record, 'next_action': next_action(record),
            'publication_approved': False}


def prepare(c, recovery_id, config, recipe, output):
    from .cases import current_cases, reprocess
    from .catalog import review_package
    record = c.get(recovery_id, 'recovery')
    require(latest(c, record['case_id']) == recovery_id, 'Recovery record superseded')
    require(current_cases(c)[record['case_id']] == record['case_revision'], 'Case revision superseded')
    require(next_action(record) == 'PREPARE_REVIEW', 'Resolve blockers or select another case before staging')
    require(config['case_revision'] == record['case_revision'], 'Recovery/config Case revision differs')
    result = reprocess(c, config, recipe)
    package = review_package(c, result['view_id'], output)
    return {**result, **package, 'recovery_id': recovery_id,
            'next_action': 'READ_PACKAGE_AND_RECORD_QUALITY_AND_LEAKAGE_REVIEWS',
            'publication_approved': False}
