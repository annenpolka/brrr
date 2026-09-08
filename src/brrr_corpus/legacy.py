"""Lossless, non-following inventory and conservative legacy import."""
from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import uuid
from collections import Counter
from pathlib import Path

from .store import CorpusError, canonical, digest, require


def walk(root):
    root = Path(root)
    require(root.is_dir() and not root.is_symlink(), 'Archive root must be an ordinary directory')
    entries = []
    for parent, dirs, names in os.walk(root, followlinks=False):
        for name in sorted(dirs + names):
            path = Path(parent) / name
            mode = path.lstat().st_mode
            item = {'path': path.relative_to(root).as_posix(), 'mode': stat.S_IMODE(mode)}
            if stat.S_ISLNK(mode):
                data = os.fsencode(os.readlink(path))
                item.update(type='symlink', sha256=digest(data), size=len(data))
            elif stat.S_ISREG(mode):
                data = path.read_bytes()
                item.update(type='file', sha256=digest(data), size=len(data))
            elif stat.S_ISDIR(mode):
                item.update(type='directory')
            elif stat.S_ISFIFO(mode):
                item.update(type='fifo')  # Record metadata; reading could block forever.
            else:
                raise CorpusError(f'Unsupported archive entry: {path}')
            entries.append(item)
    return sorted(entries, key=lambda x: x['path'])


def manifest_scalar(text, name):
    """Extract simple historical scalars only; preserve full YAML as an artifact."""
    matches = re.findall(r'^' + re.escape(name) + r':\s*([^\n]*)$', text, re.MULTILINE)
    if len(matches) != 1:
        return 'unknown'
    return matches[0].strip().strip('\"\'') or 'unknown'


def packet_inventory(run):
    root = Path(run) / 'specimens'
    require(root.is_dir() and not root.is_symlink(), 'Missing specimens directory')
    packets, other, missing = [], [], []
    for child in sorted(root.iterdir()):
        if child.is_symlink() or not child.is_dir():
            other.append(child.name)
            continue
        path = child / 'packet.json'
        if not path.is_file() or path.is_symlink():
            missing.append(child.name)
            continue
        data = json.loads(path.read_bytes())
        require(isinstance(data, dict) and isinstance(data.get('manifest'), str), f'Invalid packet: {child.name}')
        require(data.get('id') == child.name, f'Packet alias mismatch: {child.name}')
        packets.append({'alias': child.name,
                        'legacy_kind': manifest_scalar(data['manifest'], 'kind'),
                        'repository': manifest_scalar(data['manifest'], 'repository')})
    return {'packets': packets, 'packet_count': len(packets), 'non_packet_entries': other,
            'directories_missing_packet': missing,
            'legacy_kinds': dict(sorted(Counter(p['legacy_kind'] for p in packets).items()))}


def inventory(run, companion=None, design=None):
    roots = {'run': Path(run)}
    if companion:
        roots['hdd'] = Path(companion)
    trees = {label: walk(path) for label, path in roots.items()}
    result = {'schema_version': 1, 'run_id': Path(run).name,
              'trees': trees, 'trees_hash': digest(canonical(trees)),
              'summary': packet_inventory(run)}
    if design:
        result['design_sha256'] = digest(Path(design).read_bytes())
        result['base_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    return result


def import_legacy(corpus, run, companion=None, limit=None, fail_at=None):
    baseline = inventory(run, companion)
    roots = {'run': Path(run), 'hdd': Path(companion) if companion else None}
    # --limit exercises a small subset without changing the meaning of a full import.
    chosen = baseline['summary']['packets'][:limit]
    aliases = {p['alias'] for p in chosen}
    trees = {}
    refs = []
    for label, entries in baseline['trees'].items():
        kept = []
        for entry in entries:
            rel = Path(entry['path'])
            if limit is not None and (label != 'run' or len(rel.parts) < 2
                                      or rel.parts[0] != 'specimens' or rel.parts[1] not in aliases):
                continue
            item = dict(entry)
            if entry['type'] in ('file', 'symlink'):
                path = roots[label] / entry['path']
                data = os.fsencode(os.readlink(path)) if entry['type'] == 'symlink' else path.read_bytes()
                require(digest(data) == entry['sha256'], 'Archive changed while importing')
                blob = corpus.put(data)
                item['blob'] = blob
                refs.append(blob)
            kept.append(item)
        trees[label] = kept
    # A second scan detects concurrent edits and additions, not just changed files read above.
    require(inventory(run, companion)['trees_hash'] == baseline['trees_hash'], 'Archive changed during import')
    if fail_at == 'after_objects':
        raise CorpusError('Injected stop after objects, before metadata transaction')
    run_id = baseline['run_id']
    new_aliases = new_revisions = 0
    source_candidates = set()
    with corpus.transaction():
        archive = corpus.record('legacy_archive', {
            'schema_version': 1, 'run_id': run_id, 'scope': 'sample' if limit is not None else 'full',
            'trees_hash': baseline['trees_hash'], 'trees': trees,
            'quality': 'PENDING', 'leakage': 'PENDING', 'exposure': 'unknown',
        }, refs)
        for packet in chosen:
            alias = packet['alias']
            row = corpus.db.execute('SELECT case_id FROM aliases WHERE run_id=? AND alias=?',
                                    (run_id, alias)).fetchone()
            if row is None:
                case_id = str(uuid.uuid4())
                corpus.db.execute('INSERT INTO aliases VALUES (?, ?, ?)', (run_id, alias, case_id))
                new_aliases += 1
            else:
                case_id = row[0]
            prefix = f'specimens/{alias}/'
            artifacts = [p for p in trees['run'] if p['path'].startswith(prefix)]
            packet_entry = next(p for p in artifacts if p['path'] == prefix + 'packet.json')
            data = json.loads(corpus.read(packet_entry['blob']))
            # URLs are unresolved candidates, never original SourceRevisions or provider IDs.
            urls = sorted(set(re.findall(r'https://github\.com/[\w.-]+/[\w.-]+/(?:issues|pull)/\d+',
                                        data.get('source', '') + '\n' + data['manifest'])))
            source_candidates.update(urls)
            revision = corpus.record('legacy_case_revision', {
                'schema_version': 1, 'case_id': case_id, 'run_id': run_id, 'legacy_alias': alias,
                'legacy_kind': packet['legacy_kind'], 'repository': packet['repository'],
                'artifacts': artifacts, 'source_candidates': urls,
                'origin': 'unknown', 'verification': 'reported', 'acquisition': 'unavailable',
                'claim_kind': 'legacy_claim', 'quality': 'PENDING', 'leakage': 'PENDING',
                'exposure': 'unknown', 'local_execution_verified': False,
                'source_note': 'Legacy interpretations preserved; original content not independently verified.',
            }, [p['blob'] for p in artifacts if 'blob' in p])
            cursor = corpus.db.execute('INSERT OR IGNORE INTO legacy_revisions VALUES (?, ?, ?)',
                                       (run_id, alias, revision))
            new_revisions += cursor.rowcount
        if fail_at == 'before_commit':
            raise CorpusError('Injected stop before metadata commit')
    if fail_at == 'after_commit':
        raise CorpusError('Injected response loss after metadata commit')
    return {'archive_id': archive, 'trees_hash': baseline['trees_hash'], 'imported_packets': len(chosen),
            'new_aliases': new_aliases, 'new_revisions': new_revisions,
            'quality_pending': len(chosen), 'publication_eligible': 0,
            'unresolved_source_candidates': len(source_candidates),
            'preserved_entries': sum(map(len, trees.values())),
            'summary': baseline['summary']}


def verify_baseline(baseline, run, companion=None, design=None):
    current = inventory(run, companion, design)
    require(current['trees'] == baseline['trees'], 'Historical archive changed from baseline')
    if 'design_sha256' in baseline:
        require(current.get('design_sha256') == baseline['design_sha256'], 'Design changed from baseline')
    return {'ok': True, 'trees_hash': current['trees_hash'], 'packet_count': current['summary']['packet_count']}
