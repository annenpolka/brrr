"""Host-side HDD admission and append-only progress, separate from model transport.

These gates validate records, budgets of attempts and clocks, not semantic novelty.
They never call a model, execute a candidate, kill a process or manufacture approval.
"""
from datetime import datetime, timezone

from .boundary import validate_snapshot
from .store import keys, nonempty, require


def instant(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(parsed.tzinfo is not None, 'Timestamp requires a timezone')
    return parsed


def now_at(now=None):
    now = now or datetime.now(timezone.utc)
    require(now.tzinfo is not None, 'Clock requires a timezone')
    return now


def setup(c):
    c.db.executescript('''
        CREATE TABLE IF NOT EXISTS experiment_runs (
            run_id TEXT PRIMARY KEY, policy_id TEXT NOT NULL REFERENCES records(id));
        CREATE TABLE IF NOT EXISTS experiment_events (
            seq INTEGER PRIMARY KEY, run_id TEXT NOT NULL REFERENCES experiment_runs(run_id),
            record_id TEXT NOT NULL REFERENCES records(id));
    ''')


def init(c, policy):
    keys(policy, ['run_id', 'start_at', 'preserve_at', 'hard_end_at',
                  'stale_after_seconds', 'max_recovery_attempts', 'max_dream_attempts',
                  'minimum_discovery_cases', 'small_trial'])
    nonempty(policy['run_id'], 'run_id')
    require(instant(policy['start_at']) < instant(policy['preserve_at']) <= instant(policy['hard_end_at']),
            'Require start < preservation <= hard end')
    for field in ('stale_after_seconds', 'max_recovery_attempts', 'max_dream_attempts', 'minimum_discovery_cases'):
        require(type(policy[field]) is int and policy[field] > 0, f'Invalid {field}')
    require(type(policy['small_trial']) is bool, 'small_trial must be boolean')
    require(policy['minimum_discovery_cases'] >= 2 or policy['small_trial'],
            'One-input runs require the explicit small_trial label')
    setup(c)
    require(c.db.execute('SELECT 1 FROM experiment_runs WHERE run_id=?', (policy['run_id'],)).fetchone() is None,
            'Run already exists; do not re-init or reset its clock')
    with c.transaction():
        rid = c.record('experiment_policy', policy)
        c.db.execute('INSERT INTO experiment_runs VALUES (?,?)', (policy['run_id'], rid))
    return {'run_id': policy['run_id'], 'policy_id': rid, 'started_model': False}


def load(c, run_id):
    setup(c)
    row = c.db.execute('SELECT policy_id FROM experiment_runs WHERE run_id=?', (run_id,)).fetchone()
    require(row is not None, 'Unknown run')
    policy = c.get(row[0], 'experiment_policy')
    events = [c.get(r[0], 'experiment_event') for r in c.db.execute(
        'SELECT record_id FROM experiment_events WHERE run_id=? ORDER BY seq', (run_id,))]
    return policy, events


def append(c, run_id, kind, subject, evidence, progress_keys, now, detail=''):
    _, previous = load(c, run_id)
    require(not previous or now >= instant(previous[-1]['at']), 'Clock moved backwards; stop and inspect')
    with c.transaction():
        rid = c.record('experiment_event', {'run_id': run_id, 'kind': kind, 'subject': subject,
                       'evidence': evidence, 'progress_keys': sorted(progress_keys),
                       'at': now.isoformat(), 'detail': detail}, records=evidence)
        c.db.execute('INSERT INTO experiment_events(run_id,record_id) VALUES (?,?)', (run_id, rid))
    return rid


def discovery(c, spec, trace):
    keys(spec, ['subject', 'classification', 'core_operation', 'nearest_existing',
                'observable_delta', 'preserve', 'pressure', 'rationale'])
    for field in ('subject', 'core_operation', 'nearest_existing', 'observable_delta', 'preserve', 'rationale'):
        nonempty(spec[field], field)
    require(spec['classification'] in ('NOVEL_OPERATION', 'THIN_WRAPPER', 'INCOHERENT', 'NEEDS_PRESSURE'),
            'Invalid discovery classification')
    require(isinstance(spec['pressure'], list) and 1 <= len(spec['pressure']) <= 3,
            'Provide one to three focused pressures')
    for pressure in spec['pressure']:
        nonempty(pressure, 'pressure')
    require(isinstance(trace, bytes) and trace.strip(), 'Discovery needs its original usage trace')
    trace.decode('utf-8')
    blob = c.put(trace)
    with c.transaction():
        rid = c.record('discovery_assessment', {**spec, 'trace_blob': blob,
                       'evidence_class': 'speculative_design', 'runtime_verified': False,
                       'reviewer_type': 'agent'}, [blob])
    return {'assessment_id': rid, 'runtime_verified': False}


def snapshot_cases(c, sid):
    from .cases import graph
    snapshot = validate_snapshot(c, sid)
    groups = graph(c)['groups']
    result = {}
    for vid in snapshot['views']:
        spec = c.get(vid, 'view')['spec']
        if spec['split'] == 'discovery':
            result[spec['case_id']] = groups.get(spec['case_id'], spec['lineage_group'])
    return result


def status(c, run_id, now=None):
    now = now_at(now)
    policy, events = load(c, run_id)
    seen, ready, invalid = set(), {}, []
    last_progress = instant(policy['start_at'])
    attempts = {}
    for event in events:
        if event['kind'] == 'input_ready':
            try:
                ready.update(snapshot_cases(c, event['evidence'][0]))
            except ValueError as error:
                invalid.append({'snapshot_id': event['evidence'][0], 'reason': str(error)})
        fresh = set(event['progress_keys']) - seen
        if fresh:
            last_progress = max(last_progress, instant(event['at']))
            seen.update(fresh)
        if event['kind'].startswith('admit_'):
            key = (event['kind'][6:], event['subject'])
            attempts[key] = attempts.get(key, 0) + 1
    closed = any(e['kind'] == 'closed' for e in events)
    clock_backwards = bool(events and now < instant(events[-1]['at']))
    if closed:
        action = 'CLOSED'
    elif clock_backwards:
        action = 'CLOCK_ERROR'
    elif now >= instant(policy['hard_end_at']):
        action = 'HARD_STOP'
    elif now >= instant(policy['preserve_at']):
        action = 'PRESERVE'
    elif now < instant(policy['start_at']):
        action = 'NOT_BEFORE'
    elif (now - last_progress).total_seconds() >= policy['stale_after_seconds']:
        action = 'PRESERVE_NO_PROGRESS'
    else:
        action = 'WORK'
    return {'run_id': run_id, 'action': action, 'at': now.isoformat(),
            'last_progress_at': last_progress.isoformat(),
            'discovery_cases': sorted(ready), 'invalid_snapshots': invalid,
            'discovery_groups': sorted(set(ready.values())),
            'ready_for_dream': len(set(ready.values())) >= policy['minimum_discovery_cases'],
            'small_trial': policy['small_trial'], 'unique_milestones': len(seen),
            'attempts': [{'kind': k, 'subject': s, 'count': n} for (k, s), n in sorted(attempts.items())],
            'hard_end_at': policy['hard_end_at'], 'processes_stopped': False}


def progress(c, run_id, kind, evidence_id, now=None):
    now = now_at(now)
    policy, events = load(c, run_id)
    require(not any(e['kind'] == 'closed' for e in events), 'Run is closed')
    require(instant(policy['start_at']) <= now < instant(policy['preserve_at']),
            'No new exploration milestones outside the work window')
    if kind == 'input_ready':
        cases = snapshot_cases(c, evidence_id)
        require(cases, 'Holdout-only snapshot is not discovery input')
        subject, milestones = evidence_id, {'input:' + group for group in cases.values()}
    elif kind == 'blocker_resolved':
        from .recovery import latest
        record = c.get(evidence_id, 'recovery')
        require(latest(c, record['case_id']) == evidence_id, 'Recovery record superseded')
        require(record['previous'] is not None, 'Resolution needs a previously recorded blocker')
        previous = c.get(record['previous'], 'recovery')
        unresolved = {b['id'] for b in previous['blockers'] if not b['resolved']}
        resolved = {b['id'] for b in record['blockers'] if b['resolved'] and b['evidence']}
        milestones = {'blocker:' + record['case_id'] + ':' + bid for bid in unresolved & resolved}
        require(milestones, 'No previously unresolved blocker was resolved')
        subject = record['case_id']
    elif kind == 'affordance_found':
        record = c.get(evidence_id, 'discovery_assessment')
        require(record['classification'] == 'NOVEL_OPERATION', 'Only a positive affordance assessment is progress')
        require(record['subject'] in status(c, run_id, now)['discovery_cases'], 'Assessment needs an approved discovery case')
        require(any(e['kind'] == 'admit_dream' and e['subject'] == record['subject'] for e in events),
                'Assessment needs a previously admitted Dream for this case')
        subject, milestones = record['subject'], {'affordance:' + record['subject']}
    else:
        raise ValueError('Only input_ready, blocker_resolved or affordance_found count as progress')
    seen = {key for e in events for key in e['progress_keys']}
    fresh = milestones - seen
    # A renamed/re-exported packet or repeated assessment cannot keep the run alive.
    rid = append(c, run_id, kind, subject, [evidence_id], fresh, now)
    return {'event_id': rid, 'new_milestones': sorted(fresh), **status(c, run_id, now)}


def admit(c, run_id, kind, subject, hypothesis, now=None):
    now = now_at(now)
    nonempty(subject, 'subject')
    nonempty(hypothesis, 'hypothesis and expected decision')
    policy, events = load(c, run_id)
    current = status(c, run_id, now)
    require(current['action'] == 'WORK', current['action'])
    require(kind in ('recovery', 'dream', 'grounding'), 'Invalid job kind')
    if kind == 'recovery':
        from .recovery import status as recovery_status
        require(recovery_status(c, subject)['state'] == 'active', 'Case parked; switch case')
        cap = policy['max_recovery_attempts']
    else:
        require(current['ready_for_dream'] and subject in current['discovery_cases'],
                'PREPARE_INPUTS: requires enough currently approved discovery cases')
        if kind == 'grounding':
            require(any(e['kind'] == 'affordance_found' and e['subject'] == subject for e in events),
                    'Discovery gate first: record a surviving affordance before grounding')
        cap = policy['max_dream_attempts'] if kind == 'dream' else 1
    attempts = [e for e in events if e['kind'] == 'admit_' + kind and e['subject'] == subject]
    require(len(attempts) < cap, 'SWITCH_CASE: per-case attempt limit reached')
    require(hypothesis.strip() not in {e['detail'] for e in attempts}, 'SWITCH_HYPOTHESIS: repeated job')
    rid = append(c, run_id, 'admit_' + kind, subject, [], [], now, hypothesis.strip())
    return {'admitted': True, 'event_id': rid, 'attempt': len(attempts) + 1,
            'model_started': False, 'progress_recorded': False}


def close(c, run_id, reason, now=None):
    now = now_at(now)
    nonempty(reason, 'close reason')
    _, events = load(c, run_id)
    require(not any(e['kind'] == 'closed' for e in events), 'Run is already closed')
    append(c, run_id, 'closed', run_id, [], [], now, reason)
    return status(c, run_id, now)
