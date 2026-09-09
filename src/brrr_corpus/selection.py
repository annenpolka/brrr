"""Frozen candidate populations and explainable, deterministic small selections."""
from collections import Counter
from pathlib import Path
from .store import CorpusError, canonical, digest, keys, nonempty, require
from .cases import graph


def validate_recipe(recipe):
    keys(recipe, ['schema_version', 'recipe_id', 'view_recipe', 'pipeline_id', 'case_key_prefix',
                  'target_cases', 'max_cases_per_repository', 'max_cases_per_primary_mechanism',
                  'seed', 'exposure_scope', 'allow_shortfall'])
    from .boundary import validate_recipe as validate_view_recipe
    validate_view_recipe(recipe['view_recipe'])
    require(type(recipe['schema_version']) is int and recipe['schema_version'] == 1, 'Invalid selection schema')
    for field in ('recipe_id', 'pipeline_id', 'exposure_scope'):
        nonempty(recipe[field], field)
    require(isinstance(recipe['case_key_prefix'], str), 'Invalid case prefix')
    for field in ('target_cases', 'max_cases_per_repository', 'max_cases_per_primary_mechanism'):
        require(type(recipe[field]) is int and recipe[field] > 0, f'Invalid {field}')
        require(recipe[field] <= recipe['view_recipe'][field], 'Selection exceeds reviewed publication policy')
    require(type(recipe['allow_shortfall']) is bool and type(recipe['seed']) is int, 'Invalid selection options')
    require(not recipe['allow_shortfall'] or recipe['view_recipe']['allow_shortfall'], 'Selection cannot relax shortfall policy')


def check_exposure(c, spec, scope, groups):
    if spec['split'] != 'holdout':
        return
    require(spec['exposure'] == 'unexposed', 'EXPOSURE_UNKNOWN_OR_DISCOVERY')
    group = groups[spec['case_id']]
    for row in c.db.execute("SELECT id FROM records WHERE kind='exposure' ORDER BY id"):
        event = c.get(row[0], 'exposure')
        if event['scope'] != scope or event.get('split', 'all') == 'holdout':
            continue
        snapshot = c.get(event['snapshot_id'], 'snapshot')
        for vid in snapshot['views']:
            previous = c.get(vid, 'view')['spec']
            if previous['split'] == 'discovery':
                require(groups.get(previous['case_id'], previous['case_id']) != group
                        and previous['lineage_group'] != spec['lineage_group'], 'KNOWN_DISCOVERY_EXPOSURE')


def build_selection(c, recipe):
    validate_recipe(recipe)
    from .boundary import approvals, validate_view
    state = graph(c)
    exposure_ids = [row[0] for row in c.db.execute("SELECT id FROM records WHERE kind='exposure' ORDER BY id")
                    if c.get(row[0], 'exposure')['scope'] == recipe['exposure_scope']]
    candidates = []
    # Freeze every matching stored View, including superseded and pending ones.
    for row in c.db.execute("SELECT id FROM records WHERE kind='view' ORDER BY id"):
        vid = row[0]
        view = c.get(vid, 'view')
        if view['recipe'] != recipe['view_recipe'] or not view['spec'].get('derivation'):
            continue
        d = c.get(view['spec']['derivation'], 'derivation')
        case = c.get(d['config']['case_revision'], 'case_revision')
        if d['config']['pipeline_id'] != recipe['pipeline_id'] or not case['key'].startswith(recipe['case_key_prefix']):
            continue
        reasons, approved, review_ids, review_states = [], {}, {}, {}
        for kind in ('quality', 'leakage'):
            latest = c.db.execute('SELECT record_id FROM review_events WHERE view_id=? AND kind=? ORDER BY seq DESC LIMIT 1', (vid, kind)).fetchone()
            review_states[kind] = c.get(latest[0], 'review')['verdict'] if latest else 'PENDING'
            if latest:
                review_ids[kind] = latest[0]
        if state['current_cases'].get(case['case_id']) != d['config']['case_revision']:
            reasons.append('SUPERSEDED_CASE_REVISION')
        try:
            validate_view(c, vid)
        except CorpusError as error:
            reasons.append(str(error))
        try:
            approved = approvals(c, vid)
        except CorpusError as error:
            reasons.append(str(error))
        try:
            check_exposure(c, view['spec'], recipe['exposure_scope'], state['groups'])
        except CorpusError as error:
            reasons.append(str(error))
        candidates.append({'view_id': vid, 'case_revision': d['config']['case_revision'],
                           'case_id': case['case_id'], 'group': state['groups'][case['case_id']],
                           'split': view['spec']['split'], 'repository': case['repository'],
                           'primary_mechanism': case['primary_mechanism'], 'approvals': approved,
                           'review_states': review_states, 'review_ids': review_ids,
                           'reasons': reasons,
                           'rank': digest(canonical([recipe['seed'], case['key'], vid]))})
    selected, used_groups, repos, mechanisms = [], set(), Counter(), Counter()
    for item in sorted(candidates, key=lambda item: (item['rank'], item['view_id'])):
        if not item['reasons']:
            if item['group'] in used_groups:
                item['reasons'].append('SAME_INCIDENT_GROUP_ALREADY_SELECTED')
            elif repos[item['repository']] >= recipe['max_cases_per_repository']:
                item['reasons'].append('REPOSITORY_CAP')
            elif mechanisms[item['primary_mechanism']] >= recipe['max_cases_per_primary_mechanism']:
                item['reasons'].append('MECHANISM_CAP')
            elif len(selected) >= recipe['target_cases']:
                item['reasons'].append('TARGET_REACHED')
            else:
                selected.append(item['view_id'])
                used_groups.add(item['group'])
                repos[item['repository']] += 1
                mechanisms[item['primary_mechanism']] += 1
        item['decision'] = 'SELECTED' if item['view_id'] in selected else 'EXCLUDED'
    ready = bool(selected) and (len(selected) == recipe['target_cases'] or recipe['allow_shortfall'])
    result = {'schema_version': 1, 'recipe': recipe, 'graph': state,
              'selector_hash': digest(Path(__file__).read_bytes()),
              'exposure_ids': exposure_ids, 'candidates': candidates, 'selected': sorted(selected), 'status': 'READY' if ready else 'HOLD',
              'shortfall': recipe['target_cases'] - len(selected)}
    refs = [*state['current_cases'].values(), *state['relations'], *exposure_ids,
            *(item['view_id'] for item in candidates),
            *(rid for item in candidates for rid in item['review_ids'].values())]
    with c.transaction():
        sid = c.record('selection_run', result, records=refs)
    return {'selection_id': sid, **result}


def validate_selection(c, sid, view_ids=None):
    selection = c.get(sid, 'selection_run')
    validate_recipe(selection['recipe'])
    require(selection['selector_hash'] == digest(Path(__file__).read_bytes()), 'Selector changed: build a new selection')
    require(selection['status'] == 'READY', 'Selection is HOLD; inspect exclusions and record required reviews')
    if view_ids is not None:
        require(sorted(view_ids) == selection['selected'], 'Snapshot differs from frozen selection')
    require(graph(c) == selection['graph'], 'Case/relation graph changed: build a new selection')
    from .boundary import approvals, validate_view
    for item in selection['candidates']:
        if item['decision'] != 'SELECTED':
            continue
        view = validate_view(c, item['view_id'])
        require(approvals(c, item['view_id']) == item['approvals'], 'Selection review changed: select again')
        check_exposure(c, view['spec'], selection['recipe']['exposure_scope'], selection['graph']['groups'])
    return selection
