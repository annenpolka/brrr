"""Explicit, content-bound review before static HDD publication.

This is not an automatic semantic classifier or a consumer OS sandbox.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from .store import canonical, digest, keys, nonempty, publish_tree, require

OPERATOR_REQUEST = '''OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Keep the supplied reports and file bytes unchanged. They are not observations of this environment.
Explore the unfamiliar CLI's behavior, including its limits, without claiming that the supplied
incident has been reproduced, repaired, or independently verified. Keep one consistent CLI identity.
'''


def exporter_hash():
    # Any change to serialization, path handling, template or adapter expires PASS.
    return digest(canonical({p.name: digest(p.read_bytes()) for p in
                             (Path(__file__), Path(__file__).with_name('store.py'))}))


def validate_recipe(recipe):
    keys(recipe, ['schema_version', 'recipe_id', 'view_mode', 'target_cases',
                  'max_cases_per_repository', 'max_cases_per_primary_mechanism',
                  'allow_synthetic', 'allow_shortfall', 'prior_ideas_access', 'isolation_level'], ['delegated_review'])
    require(recipe['schema_version'] == 1 and type(recipe['schema_version']) is int, 'Unsupported recipe schema')
    nonempty(recipe['recipe_id'], 'recipe_id')
    if 'delegated_review' in recipe:
        keys(recipe['delegated_review'], ['reviewer', 'authorization'])
        nonempty(recipe['delegated_review']['reviewer'], 'delegated reviewer')
        nonempty(recipe['delegated_review']['authorization'], 'delegated authorization')
    require(recipe['view_mode'] == 'blind_problem', 'Only blind_problem is implemented')
    require(recipe['isolation_level'] == 'static_bundle_only', 'Consumer isolation has not been implemented')
    require(recipe['prior_ideas_access'] in ('denied', 'allowed'), 'Invalid prior ideas policy')
    for name in ('target_cases', 'max_cases_per_repository', 'max_cases_per_primary_mechanism'):
        require(type(recipe[name]) is int and recipe[name] > 0, f'Invalid {name}')
    for name in ('allow_synthetic', 'allow_shortfall'):
        require(type(recipe[name]) is bool, f'Invalid {name}')


def check_holdout_exposure(corpus, spec):
    if spec['split'] != 'holdout':
        return
    require(spec['exposure'] == 'unexposed', 'EXPOSURE_UNKNOWN_OR_DISCOVERY: holdout excluded')
    # Conservative P0: any recorded discovery exposure excludes this case/group.
    # Named experiment scopes and relation closure are intentionally left for P3.
    for row in corpus.db.execute("SELECT id FROM records WHERE kind='exposure'"):
        event = corpus.get(row[0], 'exposure')
        snapshot = corpus.get(event['snapshot_id'], 'snapshot')
        for vid in snapshot['views']:
            previous = corpus.get(vid, 'view')['spec']
            if previous['split'] == 'discovery':
                require(previous['case_id'] != spec['case_id'] and previous['lineage_group'] != spec['lineage_group'],
                        'KNOWN_DISCOVERY_EXPOSURE: holdout excluded')


def public_path(path):
    require(isinstance(path, str) and len(path) <= 240, 'Invalid artifact path')
    require(path in ('TASK.md', 'OBSERVED.md', 'COMMANDS.md', 'TREE.txt') or
            (path.startswith('files/') and all(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', part)
                                              for part in path.split('/')[1:])),
            'Artifact path outside publication allowlist')
    require(all(part not in ('.', '..') and not part.startswith('.') for part in path.split('/')),
            'Unsafe path component')
    require(not any(part.lower() in ('packet.json', 'answer-key', 'curation.md', 'raw-sources')
                    for part in path.split('/')), 'Restricted artifact name')
    return path


def build_artifact(corpus, artifact, origin):
    keys(artifact, ['path', 'segments'])
    public_path(artifact['path'])
    require(isinstance(artifact['segments'], list) and artifact['segments'], 'Missing claim segments')
    output, references = [], []
    for segment in artifact['segments']:
        require(isinstance(segment, dict), 'Invalid segment')
        if segment.get('kind') == 'generated_prompt':
            keys(segment, ['kind', 'text'])
            nonempty(segment['text'], 'generated_prompt.text')
            output.append(segment['text'].encode('utf-8'))
        else:
            keys(segment, ['kind', 'source_revision', 'start', 'end'])
            require(segment['kind'] == 'reporter_observation',
                    'P0 supports reported text only; local/source-fact claims require P3 evidence contracts')
            source = corpus.get(segment['source_revision'], 'source_revision')
            require(source.get('origin') == origin, 'Source origin differs from view origin')
            require(source.get('acquisition') in ('operator_supplied', 'synthetic_test_fixture', 'github_http'),
                    'Unsupported source acquisition')
            raw = corpus.read(source['body_blob'])
            start, end = segment['start'], segment['end']
            require(type(start) is int and type(end) is int and 0 <= start < end <= len(raw),
                    'Invalid UTF-8 byte range')
            part = raw[start:end]
            part.decode('utf-8')  # Reject a range cutting through a code point.
            output.append(part)
            references.append(segment['source_revision'])
    return b''.join(output), references


def scan(corpus, files, restricted_blobs, identifiers):
    needles = list(identifiers)
    for blob in restricted_blobs:
        text = corpus.read(blob).decode('utf-8')
        needles.extend(line.strip() for line in text.splitlines() if len(line.strip()) >= 40)
        needles.extend(re.findall(r'\b[0-9a-f]{40}\b|https://\S+|\btest_[A-Za-z0-9_]+\b', text))
    haystack = '\n'.join(name + '\n' + data.decode('utf-8') for name, data in sorted(files.items())).casefold()
    for needle in needles:
        nonempty(needle, 'forbidden identifier')
        # Diagnostics never echo the secret back into a public input or terminal log.
        require(needle.casefold() not in haystack, 'ANSWER_LEAK: restricted content or identifier matches bundle')


def stage_view(corpus, spec, recipe):
    validate_recipe(recipe)
    keys(spec, ['schema_version', 'origin', 'case_id', 'lineage_group', 'repository',
                'primary_mechanism', 'split', 'exposure', 'mode', 'artifacts',
                'restricted_blobs', 'forbidden_identifiers'], ['derivation'])
    require(type(spec['schema_version']) is int and spec['schema_version'] == 1, 'Unsupported view schema')
    require(spec['mode'] == recipe['view_mode'], 'Mixed publication modes')
    require(spec['origin'] in ('real', 'synthetic'), 'Unsupported origin; legacy/derived material needs P3 review')
    require(spec['origin'] != 'synthetic' or recipe['allow_synthetic'], 'Synthetic input excluded by recipe')
    require(spec['split'] in ('discovery', 'holdout'), 'Invalid split')
    require(spec['exposure'] in ('unknown', 'unexposed', 'discovery'), 'Invalid exposure')
    for name in ('case_id', 'lineage_group', 'repository', 'primary_mechanism'):
        nonempty(spec[name], name)
    for name in ('artifacts', 'restricted_blobs', 'forbidden_identifiers'):
        require(isinstance(spec[name], list), f'Invalid {name}')
    if spec.get('derivation'):
        from .cases import validate_derivation
        validate_derivation(corpus, spec)
    files, provenance = {}, set()
    for artifact in spec['artifacts']:
        data, refs = build_artifact(corpus, artifact, spec['origin'])
        require(artifact['path'].casefold() not in {p.casefold() for p in files}, 'Duplicate artifact path')
        files[artifact['path']] = data
        provenance.update(refs)
    require({'TASK.md', 'OBSERVED.md', 'COMMANDS.md'} <= files.keys(), 'Missing required HDD artifacts')
    require(provenance, 'At least one traceable source observation is required')
    # Add truthful provenance labels; keep the invention request verbatim.
    files['OBSERVED.md'] = b'Reported observations; not verified by a local runner.\n\n' + files['OBSERVED.md']
    files['COMMANDS.md'] = b'Reported or proposed commands; not executed by this collector.\n\n' + files['COMMANDS.md']
    parts = ['CURRENT SITUATION\nThe supplied material contains reported observations and explicit questions.\n']
    for name, data in sorted(files.items()):
        parts.append(f'### {name}\n\n{data.decode("utf-8")}\n')
    parts.extend(['KNOWN FACTS\nTreat reports as reports. Do not assume a root cause.\n',
                  'UNKNOWN\nWhat relation, provenance, or question would make this failure smaller to investigate?\n',
                  OPERATOR_REQUEST])
    files['seed.md'] = '\n'.join(parts).encode('utf-8')
    scan(corpus, files, spec['restricted_blobs'], spec['forbidden_identifiers'])
    blobs = {path: corpus.put(data) for path, data in sorted(files.items())}
    with corpus.transaction():
        return corpus.record('view', {'schema_version': 1, 'spec': spec, 'recipe': recipe,
                                     'exporter_hash': exporter_hash(), 'files': blobs,
                                     'source_revisions': sorted(provenance)},
                             [*blobs.values(), *spec['restricted_blobs']], [*sorted(provenance), *([spec['derivation']] if spec.get('derivation') else [])])


def validate_view(corpus, view_id):
    view = corpus.get(view_id, 'view')
    require(view['exporter_hash'] == exporter_hash(), 'Exporter changed: restage and review required')
    validate_recipe(view['recipe'])
    if view['spec'].get('derivation'):
        from .cases import validate_derivation
        validate_derivation(corpus, view['spec'])
    for source in view['source_revisions']:
        corpus.get(source, 'source_revision')
    files = {name: corpus.read(blob) for name, blob in view['files'].items()}
    for name in files:
        if name != 'seed.md':
            public_path(name)
    scan(corpus, files, view['spec']['restricted_blobs'], view['spec']['forbidden_identifiers'])
    return view


def review(corpus, view_id, *, kind, verdict, reviewer, reviewer_type, rationale, attestations):
    view = validate_view(corpus, view_id)
    require(kind in ('quality', 'leakage'), 'Invalid review kind')
    choices = ('PENDING', 'PASS', 'HOLD', 'REJECT') if kind == 'quality' else ('PENDING', 'PASS', 'FAIL', 'INDETERMINATE')
    require(verdict in choices, 'Invalid review verdict')
    require(reviewer_type in ('human', 'agent', 'fixture'), 'Invalid reviewer type')
    nonempty(reviewer, 'reviewer')
    nonempty(rationale, 'rationale')
    if verdict == 'PASS':
        require(reviewer_allowed(corpus, view, reviewer_type, reviewer),
                'Pilot PASS requires human content review or the explicitly delegated reviewer; fixture PASS is synthetic-only')
        keys(attestations, ['full_bundle_read', 'provenance_checked', 'solution_context_checked'])
        require(all(v is True for v in attestations.values()), 'PASS requires all explicit attestations')
    with corpus.transaction():
        rid = corpus.record('review', {'schema_version': 1, 'view_id': view_id, 'kind': kind,
                                      'verdict': verdict, 'reviewer': reviewer, 'reviewer_type': reviewer_type,
                                      'rationale': rationale, 'attestations': attestations}, records=[view_id])
        corpus.db.execute('INSERT INTO review_events(view_id, kind, record_id) VALUES (?, ?, ?)', (view_id, kind, rid))
    return rid


def approvals(corpus, view_id):
    result = {}
    for kind in ('quality', 'leakage'):
        row = corpus.db.execute('SELECT record_id FROM review_events WHERE view_id=? AND kind=? ORDER BY seq DESC LIMIT 1',
                                (view_id, kind)).fetchone()
        require(row is not None, f'{kind} review is PENDING')
        r = corpus.get(row[0], 'review')
        require(r['verdict'] == 'PASS' and reviewer_allowed(
                corpus, corpus.get(view_id, 'view'), r['reviewer_type'], r['reviewer']),
                f'{kind} review is not PASS by a permitted reviewer')
        result[kind] = row[0]
    return result


def reviewer_allowed(corpus, view, reviewer_type, reviewer):
    # This records the user's delegation; like human review, it is not identity authentication.
    delegation = view['recipe'].get('delegated_review')
    return (reviewer_type == 'human'
            or (reviewer_type == 'fixture' and fixture_allowed(corpus, view))
            or (reviewer_type == 'agent' and delegation is not None and reviewer == delegation['reviewer']))


def fixture_allowed(corpus, view):
    return (view['spec']['origin'] == 'synthetic' and view['recipe']['allow_synthetic']
            and all(corpus.get(rid, 'source_revision')['origin'] == 'synthetic'
                    for rid in view['source_revisions']))


def seal(corpus, view_ids, selection_id=None):
    selection = None
    if selection_id:
        from .selection import validate_selection
        selection = validate_selection(corpus, selection_id, view_ids)
    require(isinstance(view_ids, list) and view_ids, 'No eligible views; cannot seal an empty snapshot')
    require(len(view_ids) == len(set(view_ids)), 'Duplicate view')
    views = [(vid, validate_view(corpus, vid)) for vid in sorted(view_ids)]
    require(selection is not None or not any(v['spec'].get('derivation') for _, v in views),
            'Derived views require seal-selection to enforce Case relations and selection policy')
    recipe = views[0][1]['recipe']
    require(all(v['recipe'] == recipe for _, v in views), 'Mixed recipes')
    require(len(views) <= recipe['target_cases'], 'Target case count exceeded')
    require(recipe['allow_shortfall'] or len(views) == recipe['target_cases'], 'INSUFFICIENT_ELIGIBLE_CASES')
    cases, groups, repositories, mechanisms = set(), {}, Counter(), Counter()
    approved, filemap = {}, {}
    for index, (vid, view) in enumerate(views, 1):
        spec = view['spec']
        require(spec['case_id'] not in cases, 'Duplicate case')
        cases.add(spec['case_id'])
        group = selection['graph']['groups'][spec['case_id']] if selection else spec['lineage_group']
        require(group not in groups, 'DUPLICATE_INCIDENT or GROUP_SPLIT_CONFLICT')
        groups[group] = spec['split']
        if selection is None:
            check_holdout_exposure(corpus, spec)
        repositories[spec['repository']] += 1
        mechanisms[spec['primary_mechanism']] += 1
        approved[vid] = approvals(corpus, vid)
        for name, blob in view['files'].items():
            filemap[f'{spec["split"]}/input-{index:03d}/{name}'] = blob
    require(max(repositories.values()) <= recipe['max_cases_per_repository'], 'DIVERSITY_CAP: repository')
    require(max(mechanisms.values()) <= recipe['max_cases_per_primary_mechanism'], 'DIVERSITY_CAP: mechanism')
    manifest = {'schema_version': 1, 'views': [vid for vid, _ in views], 'approvals': approved,
                'recipe': recipe, 'exporter_hash': exporter_hash(), 'files': filemap,
                'target_cases': recipe['target_cases'], 'selected_cases': len(views),
                'shortfall': recipe['target_cases'] - len(views),
                'isolation_level': 'static_bundle_only'}
    if selection:
        manifest['selection_id'] = selection_id
        manifest['selection_target_cases'] = selection['recipe']['target_cases']
    with corpus.transaction():
        sid = corpus.record('snapshot', manifest, list(filemap.values()),
                            [*manifest['views'], *(r for pair in approved.values() for r in pair.values()),
                             *([selection_id] if selection else [])])
        previous = corpus.db.execute('SELECT state FROM snapshot_events WHERE snapshot_id=? ORDER BY seq DESC LIMIT 1',
                                     (sid,)).fetchone()
        require(previous is None or previous[0] == 'SEALED', 'Snapshot was revoked; create a new revision')
        if previous is None:
            corpus.db.execute("INSERT INTO snapshot_events(snapshot_id,state,reason) VALUES (?, 'SEALED', 'all required checks passed')", (sid,))
    return sid


def validate_snapshot(corpus, snapshot_id):
    snapshot = corpus.get(snapshot_id, 'snapshot')
    state = corpus.db.execute('SELECT state FROM snapshot_events WHERE snapshot_id=? ORDER BY seq DESC LIMIT 1',
                              (snapshot_id,)).fetchone()
    require(state is not None and state[0] == 'SEALED', 'Snapshot is not SEALED')
    require(snapshot['exporter_hash'] == exporter_hash(), 'Exporter version mismatch')
    if snapshot.get('selection_id'):
        from .selection import validate_selection
        validate_selection(corpus, snapshot['selection_id'], snapshot['views'])
    # Recheck current reviews and all referenced objects before any public write.
    for vid in snapshot['views']:
        view = validate_view(corpus, vid)
        if not snapshot.get('selection_id'):
            check_holdout_exposure(corpus, view['spec'])
        require(approvals(corpus, vid) == snapshot['approvals'][vid], 'Snapshot review changed; reseal required')
    for blob in snapshot['files'].values():
        corpus.read(blob)
    return snapshot


def export_snapshot(corpus, snapshot_id, dest):
    snapshot = validate_snapshot(corpus, snapshot_id)
    files = {name: corpus.read(blob) for name, blob in snapshot['files'].items()}
    reused = publish_tree(dest, files)
    return {'snapshot_id': snapshot_id, 'files': snapshot['files'], 'reused': reused,
            'isolation_level': 'static_bundle_only'}
