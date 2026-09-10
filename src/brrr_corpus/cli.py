"""Corpus CLI. Only collect/resume/refresh perform explicit GitHub GET requests."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .boundary import (approvals, export_snapshot, review, seal, stage_view,
                       validate_recipe, validate_view)
from .legacy import import_legacy, inventory, verify_baseline
from .collection import (collection_status, resolve_collection, run_collection, setup,
                         start_collection)
from .collection_plan import make_plan
from .store import (Corpus, CorpusError, canonical, keys, nonempty,
                    no_symlink_components, publish_tree, require, restore_backup)


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default='.brrr-corpus')
    commands = p.add_subparsers(dest='command', required=True)
    for name in ('inventory', 'verify-baseline', 'import-legacy'):
        cmd = commands.add_parser(name)
        cmd.add_argument('--run', required=True)
        cmd.add_argument('--companion')
        if name in ('inventory', 'verify-baseline'):
            cmd.add_argument('--design', default='docs/archive/issue-collection-redesign.md')
        if name == 'inventory':
            cmd.add_argument('--output', required=True)
        elif name == 'verify-baseline':
            cmd.add_argument('--baseline', required=True)
        else:
            cmd.add_argument('--dry-run', action='store_true')
            cmd.add_argument('--limit', type=int)
    commands.add_parser('audit')
    cmd = commands.add_parser('sources', help='Search all stored source revisions offline')
    for name in ('query', 'repository', 'kind', 'origin'):
        cmd.add_argument('--' + name, default='')
    cmd.add_argument('--limit', type=int, default=50)
    cmd = commands.add_parser('show-source')
    cmd.add_argument('revision')
    for name in ('save-case', 'relate-case', 'add-claim'):
        cmd = commands.add_parser(name)
        cmd.add_argument('--file', required=True)
    commands.add_parser('list-cases')
    cmd = commands.add_parser('save-recovery', help='Record actionable blockers; never grants PASS')
    cmd.add_argument('--file', required=True)
    cmd = commands.add_parser('recovery-status')
    cmd.add_argument('case_id')
    cmd = commands.add_parser('prepare-review', help='Reprocess resolved recovery into a private review package')
    cmd.add_argument('recovery_id')
    cmd.add_argument('--config', required=True)
    cmd.add_argument('--recipe', required=True)
    cmd.add_argument('--output', required=True)
    cmd = commands.add_parser('init-experiment', help='Freeze run policy; does not start models')
    cmd.add_argument('--file', required=True)
    cmd = commands.add_parser('record-discovery', help='Assess speculative usage separately from runtime evidence')
    cmd.add_argument('--file', required=True)
    cmd.add_argument('--trace', required=True)
    cmd = commands.add_parser('experiment-status')
    cmd.add_argument('run_id')
    cmd = commands.add_parser('experiment-progress')
    cmd.add_argument('run_id')
    cmd.add_argument('--kind', choices=['input_ready', 'blocker_resolved', 'affordance_found'], required=True)
    cmd.add_argument('--evidence', required=True)
    cmd = commands.add_parser('admit-job', help='Gate and reserve one attempt before starting a job')
    cmd.add_argument('run_id')
    cmd.add_argument('--kind', choices=['recovery', 'dream', 'grounding'], required=True)
    cmd.add_argument('--subject', required=True)
    cmd.add_argument('--hypothesis', required=True)
    cmd = commands.add_parser('close-experiment')
    cmd.add_argument('run_id')
    cmd.add_argument('--reason', required=True)
    cmd = commands.add_parser('show-case')
    cmd.add_argument('revision')
    cmd = commands.add_parser('reprocess')
    cmd.add_argument('--config', required=True)
    cmd.add_argument('--recipe', required=True)
    cmd = commands.add_parser('select')
    cmd.add_argument('--recipe', required=True)
    for name in ('inspect-selection', 'seal-selection'):
        cmd = commands.add_parser(name)
        cmd.add_argument('selection_id')
    cmd = commands.add_parser('mini-demo', help='Offline synthetic end-to-end exercise in a dedicated directory')
    cmd.add_argument('--output', required=True)
    cmd = commands.add_parser('backup')
    cmd.add_argument('--output', required=True)
    cmd = commands.add_parser('restore')
    cmd.add_argument('--backup', required=True)
    cmd.add_argument('--output', required=True)
    cmd = commands.add_parser('import-source', help='Record operator-supplied original text; no network')
    cmd.add_argument('--file', required=True)
    cmd.add_argument('--metadata', required=True)
    cmd = commands.add_parser('stage-view')
    cmd.add_argument('--spec', required=True)
    cmd.add_argument('--recipe', required=True)
    cmd = commands.add_parser('inspect-view', help='Write a private human-review package, not a public export')
    cmd.add_argument('view_id')
    cmd.add_argument('--output', required=True)
    cmd = commands.add_parser('record-review')
    cmd.add_argument('--file', required=True)
    cmd = commands.add_parser('seal')
    cmd.add_argument('--view', action='append', required=True)
    cmd = commands.add_parser('export')
    cmd.add_argument('snapshot_id')
    cmd.add_argument('--output', required=True)
    cmd = commands.add_parser('revoke')
    cmd.add_argument('snapshot_id')
    cmd.add_argument('--reason', required=True)
    cmd = commands.add_parser('record-exposure')
    cmd.add_argument('snapshot_id')
    cmd.add_argument('--consumer', required=True)
    cmd.add_argument('--scope', required=True)
    cmd.add_argument('--split', choices=['all', 'discovery', 'holdout'], default='all')
    cmd = commands.add_parser('readiness')
    cmd.add_argument('--recipe', required=True)
    cmd = commands.add_parser('plan', help='Freeze a collection recipe and legacy seed set; offline')
    cmd.add_argument('--recipe', required=True)
    for name in ('collect', 'resume', 'refresh'):
        cmd = commands.add_parser(name)
        if name == 'collect':
            group = cmd.add_mutually_exclusive_group(required=True)
            group.add_argument('--recipe')
            group.add_argument('--plan')
        else:
            cmd.add_argument('--collection', required=True)
        cmd.add_argument('--max-requests', type=int, default=100)
        cmd.add_argument('--max-seconds', type=float, default=300)
        if name == 'resume':
            cmd.add_argument('--retry-failed', action='store_true')
    cmd = commands.add_parser('collection-status')
    cmd.add_argument('collection', nargs='?', default='latest')
    return p


def source_import(c, file, metadata):
    keys(metadata, ['schema_version', 'provider', 'resource_kind', 'provider_id', 'url',
                    'observed_at', 'provider_created_at', 'provider_updated_at',
                    'content_available_at', 'origin'])
    require(metadata['schema_version'] == 1, 'Unsupported metadata version')
    require(metadata['origin'] in ('real', 'synthetic'), 'Invalid source origin')
    for field in ('provider', 'resource_kind', 'provider_id', 'url', 'observed_at'):
        nonempty(metadata[field], field)
    for field in ('observed_at', 'provider_created_at', 'provider_updated_at', 'content_available_at'):
        value = metadata[field]
        if value is not None:
            nonempty(value, field)
            require(datetime.fromisoformat(value.replace('Z', '+00:00')).tzinfo is not None,
                    f'{field} requires timezone')
    data = no_symlink_components(file).read_bytes()
    data.decode('utf-8')
    blob = c.put(data)
    with c.transaction():
        identity = tuple(metadata[x] for x in ('provider', 'resource_kind', 'provider_id'))
        row = c.db.execute('SELECT id FROM sources WHERE provider=? AND resource_kind=? AND provider_id=?', identity).fetchone()
        source_id = row[0] if row else str(uuid.uuid4())
        if row is None:
            c.db.execute('INSERT INTO sources VALUES (?, ?, ?, ?)', (source_id, *identity))
        # Acquisition time is an observation, not part of content identity.
        revision_metadata = {k: v for k, v in metadata.items() if k != 'observed_at'}
        rid = c.record('source_revision', {**revision_metadata, 'source_id': source_id,
                       'acquisition': 'operator_supplied', 'body_blob': blob}, [blob])
        observation = c.record('source_observation', {'source_revision': rid,
                               'observed_at': metadata['observed_at'], 'transport': 'operator_supplied'}, records=[rid])
    return {'source_id': source_id, 'source_revision': rid, 'body_blob': blob, 'observation': observation,
            'historical_content': 'unverified' if metadata['content_available_at'] is None else 'operator_attested'}


def readiness(c, recipe):
    validate_recipe(recipe)
    eligible, blocked = [], []
    for row in c.db.execute("SELECT id FROM records WHERE kind='view' ORDER BY id"):
        vid = row[0]
        view = c.get(vid, 'view')
        if view['recipe'] != recipe:
            continue
        try:
            validate_view(c, vid)
            approvals(c, vid)
            eligible.append(vid)
        except CorpusError as e:
            blocked.append({'view_id': vid, 'reason': str(e)})
    cases = {c.get(v, 'view')['spec']['case_id'] for v in eligible}
    return {'ready_for_selection': bool(eligible), 'ready_for_hdd': False,
            'reason': 'Select explicit views and seal a snapshot before HDD execution.',
            'target_cases': recipe['target_cases'], 'reviewed_case_candidates': len(cases),
            'shortfall': max(0, recipe['target_cases'] - len(cases)),
            'eligible_view_ids': eligible, 'blocked_views': blocked,
            'legacy_aliases': c.db.execute('SELECT count(*) FROM aliases').fetchone()[0],
            'pending_work': ['case relations, evidence and exposure-policy adjudication (P3)',
                             '24-case human content audit and pilot selection (P4)',
                             'consumer isolation and fresh HDD context']}


def dispatch(args):
    if args.command == 'mini-demo':
        from .mini import run_demo
        return run_demo(args.output)
    if args.command == 'inventory':
        result = inventory(args.run, args.companion, args.design)
        path = no_symlink_components(args.output)
        data = canonical(result)
        if path.exists():
            require(path.read_bytes() == data, 'Baseline differs; use a new filename')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as out:
                out.write(data)
        return {'output': str(path), 'trees_hash': result['trees_hash'], 'summary': result['summary']}
    if args.command == 'verify-baseline':
        return verify_baseline(read_json(args.baseline), args.run, args.companion, args.design)
    if args.command == 'import-legacy' and args.dry_run:
        result = inventory(args.run, args.companion)
        return {'dry_run': True, 'trees_hash': result['trees_hash'], 'summary': result['summary'],
                'publication_eligible': 0, 'quality': 'PENDING', 'leakage': 'PENDING'}
    if args.command == 'restore':
        return restore_backup(args.backup, args.output)
    if args.command not in ('import-legacy', 'import-source', 'plan', 'collect'):
        require((Path(args.root) / 'corpus.sqlite').is_file(), 'Corpus does not exist; import data first')
    c = Corpus(args.root)
    try:
        if args.command in ('init-experiment', 'record-discovery', 'experiment-status',
                            'experiment-progress', 'admit-job', 'close-experiment'):
            from . import experiment
            if args.command == 'init-experiment':
                return experiment.init(c, read_json(args.file))
            if args.command == 'record-discovery':
                return experiment.discovery(c, read_json(args.file), no_symlink_components(args.trace).read_bytes())
            if args.command == 'experiment-status':
                return experiment.status(c, args.run_id)
            if args.command == 'experiment-progress':
                return experiment.progress(c, args.run_id, args.kind, args.evidence)
            if args.command == 'admit-job':
                return experiment.admit(c, args.run_id, args.kind, args.subject, args.hypothesis)
            return experiment.close(c, args.run_id, args.reason)
        from . import cases, catalog, selection
        if args.command in ('save-recovery', 'recovery-status', 'prepare-review'):
            from . import recovery
            if args.command == 'save-recovery':
                return recovery.save(c, read_json(args.file))
            if args.command == 'recovery-status':
                return recovery.status(c, args.case_id)
            return recovery.prepare(c, args.recovery_id, read_json(args.config),
                                    read_json(args.recipe), args.output)
        if args.command == 'sources':
            return catalog.sources(c, query=args.query, repository=args.repository,
                                   kind=args.kind, origin=args.origin, limit=args.limit)
        if args.command == 'show-source':
            return catalog.show_source(c, args.revision)
        if args.command == 'save-case':
            return cases.save_case(c, read_json(args.file))
        if args.command == 'list-cases':
            return {'cases': [{'revision': rid, **c.get(rid, 'case_revision')}
                              for rid in cases.current_cases(c).values()]}
        if args.command == 'show-case':
            return c.get(args.revision, 'case_revision')
        if args.command == 'relate-case':
            return {'relation_id': cases.relate(c, read_json(args.file))}
        if args.command == 'add-claim':
            return {'claim_id': cases.save_claim(c, read_json(args.file))}
        if args.command == 'reprocess':
            return cases.reprocess(c, read_json(args.config), read_json(args.recipe))
        if args.command == 'select':
            return selection.build_selection(c, read_json(args.recipe))
        if args.command == 'inspect-selection':
            return c.get(args.selection_id, 'selection_run')
        if args.command == 'seal-selection':
            selected = selection.validate_selection(c, args.selection_id)
            return {'snapshot_id': seal(c, selected['selected'], args.selection_id)}
        if args.command == 'plan':
            pid = make_plan(c, read_json(args.recipe))
            return {'plan_id': pid, **c.get(pid, 'collection_plan')}
        if args.command == 'collection-status':
            return collection_status(c, args.collection)
        if args.command in ('collect', 'resume', 'refresh'):
            if args.command == 'collect':
                pid = make_plan(c, read_json(args.recipe)) if args.recipe else args.plan
                cid = start_collection(c, pid)
            else:
                cid = resolve_collection(c, args.collection)
                if args.command == 'refresh':
                    old = c.db.execute('SELECT plan_id FROM collections WHERE id=?', (cid,)).fetchone()[0]
                    pid = make_plan(c, c.get(old, 'collection_plan')['recipe'])
                    cid = start_collection(c, pid, refresh_of=cid)
            print(json.dumps({'collection_id': cid, 'resume': f'python3 scripts/corpus.py --root {args.root} resume --collection {cid}'}), file=sys.stderr)
            return run_collection(c, cid, max_requests=args.max_requests, max_seconds=args.max_seconds,
                                  retry_failed=getattr(args, 'retry_failed', False),
                                  progress=lambda message: print(json.dumps(message), file=sys.stderr))
        if args.command == 'import-legacy':
            require(args.limit is None or args.limit > 0, 'limit must be positive')
            return import_legacy(c, args.run, args.companion, args.limit)
        if args.command == 'audit':
            return c.audit()
        if args.command == 'backup':
            return c.backup(args.output)
        if args.command == 'import-source':
            return source_import(c, args.file, read_json(args.metadata))
        if args.command == 'stage-view':
            vid = stage_view(c, read_json(args.spec), read_json(args.recipe))
            states = {}
            for kind in ('quality', 'leakage'):
                row = c.db.execute('SELECT record_id FROM review_events WHERE view_id=? AND kind=? ORDER BY seq DESC LIMIT 1',
                                   (vid, kind)).fetchone()
                states[kind] = c.get(row[0], 'review')['verdict'] if row else 'PENDING'
            return {'view_id': vid, **states}
        if args.command == 'inspect-view':
            return catalog.review_package(c, args.view_id, args.output)
        if args.command == 'record-review':
            data = read_json(args.file)
            keys(data, ['view_id', 'kind', 'verdict', 'reviewer', 'reviewer_type', 'rationale', 'attestations'])
            return {'review_id': review(c, **data)}
        if args.command == 'seal':
            return {'snapshot_id': seal(c, args.view)}
        if args.command == 'export':
            return export_snapshot(c, args.snapshot_id, args.output)
        if args.command == 'revoke':
            c.get(args.snapshot_id, 'snapshot')
            nonempty(args.reason, 'reason')
            with c.transaction():
                c.db.execute("INSERT INTO snapshot_events(snapshot_id,state,reason) VALUES (?, 'REVOKED', ?)",
                             (args.snapshot_id, args.reason))
            return {'snapshot_id': args.snapshot_id, 'state': 'REVOKED'}
        if args.command == 'record-exposure':
            c.get(args.snapshot_id, 'snapshot')
            nonempty(args.consumer, 'consumer')
            nonempty(args.scope, 'scope')
            with c.transaction():
                rid = c.record('exposure', {'snapshot_id': args.snapshot_id, 'consumer': args.consumer,
                               'scope': args.scope, 'split': args.split, 'observed_at': datetime.now(timezone.utc).isoformat()},
                               records=[args.snapshot_id])
            return {'exposure_id': rid}
        if args.command == 'readiness':
            return readiness(c, read_json(args.recipe))
        raise CorpusError('Unknown command')
    finally:
        c.close()


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = dispatch(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result.get('ok') is False:
            return 1
        if args.command == 'experiment-status' and result['action'] != 'WORK':
            return 3
        if args.command == 'select' and result['status'] != 'READY':
            return 3
        if args.command == 'readiness' and not result['ready_for_selection']:
            return 3
        if args.command in ('collect', 'resume', 'refresh', 'collection-status') and result['state'] != 'COMPLETE_FOR_POLICY':
            return 3
        return 0
    except (CorpusError, OSError, ValueError, KeyError, TypeError, sqlite3.Error) as e:
        print(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(json.dumps({'ok': False, 'error': 'INTERRUPTED',
                          'recovery': 'Resume the printed collection ID after its active lease expires.'}), file=sys.stderr)
        return 130
