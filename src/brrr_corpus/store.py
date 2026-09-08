"""Single-host, immutable objects plus transactional metadata (stdlib only)."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path


class CorpusError(ValueError):
    pass


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise CorpusError(message)


def keys(value, required, optional=()):
    require(isinstance(value, dict), 'Expected JSON object')
    require(set(required) <= value.keys(), f'Missing keys: {sorted(set(required) - value.keys())}')
    require(value.keys() <= set(required) | set(optional),
            f'Unknown keys: {sorted(value.keys() - set(required) - set(optional))}')


def nonempty(value, name):
    require(isinstance(value, str) and bool(value.strip()), f'{name} must be a nonempty string')


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def no_symlink_components(path):
    path = Path(os.path.abspath(path))
    for part in [*reversed(path.parents), path]:
        require(not part.is_symlink(), f'Symlink path component: {part}')
    return path


def write_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())


def tree_bytes(root):
    """Public trees must contain only regular files and ordinary directories."""
    root = no_symlink_components(root)
    require(root.is_dir(), 'Expected directory')
    files = {}
    for parent, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            p = Path(parent) / name
            require(not p.is_symlink(), f'Symlink in bundle: {p}')
            if name in names:
                require(p.is_file(), f'Non-regular file: {p}')
                files[p.relative_to(root).as_posix()] = p.read_bytes()
    return files


def publish_tree(dest, files):
    dest = no_symlink_components(dest)
    if dest.exists():
        require(tree_bytes(dest) == files, 'Existing output differs (including residual files)')
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.brrr-export-', dir=dest.parent))
    try:
        for rel, data in sorted(files.items()):
            # Callers cannot escape even if a future adapter forgets to validate.
            require(isinstance(rel, str) and rel and '\\' not in rel, 'Invalid output path')
            require(not rel.startswith('/') and all(x not in ('', '.', '..') for x in rel.split('/')),
                    'Unsafe output path')
            write_bytes(stage / rel, data)
        for parent, _, _ in os.walk(stage, topdown=False):
            fsync_dir(parent)
        require(not dest.exists() and not dest.is_symlink(), 'Output appeared during publication')
        os.rename(stage, dest)
        fsync_dir(dest.parent)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return False


class Corpus:
    """One coordinator lock covers metadata, import, export and consistent backup."""
    def __init__(self, root):
        self.root = no_symlink_components(root)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = no_symlink_components(self.root / '.lock').open('a+b')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            raise CorpusError('Corpus is busy; retry after the current coordinator exits')
        for name in ('objects/sha256', 'staging', 'quarantine', 'exports'):
            no_symlink_components(self.root / name).mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(no_symlink_components(self.root / 'corpus.sqlite'), isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA synchronous=FULL')
        require(self.db.execute('PRAGMA user_version').fetchone()[0] in (0, 1), 'Unsupported DB version')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS objects (
                hash TEXT PRIMARY KEY, size INTEGER NOT NULL CHECK(size >= 0));
            CREATE TABLE IF NOT EXISTS records (
                id TEXT PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS record_objects (
                record_id TEXT REFERENCES records(id), blob TEXT REFERENCES objects(hash),
                PRIMARY KEY(record_id, blob));
            CREATE TABLE IF NOT EXISTS record_links (
                record_id TEXT REFERENCES records(id), target_id TEXT REFERENCES records(id),
                PRIMARY KEY(record_id, target_id));
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY, provider TEXT NOT NULL, resource_kind TEXT NOT NULL,
                provider_id TEXT NOT NULL, UNIQUE(provider, resource_kind, provider_id));
            CREATE TABLE IF NOT EXISTS aliases (
                run_id TEXT NOT NULL, alias TEXT NOT NULL, case_id TEXT NOT NULL UNIQUE,
                PRIMARY KEY(run_id, alias));
            CREATE TABLE IF NOT EXISTS legacy_revisions (
                run_id TEXT NOT NULL, alias TEXT NOT NULL, record_id TEXT REFERENCES records(id),
                PRIMARY KEY(run_id, alias, record_id),
                FOREIGN KEY(run_id, alias) REFERENCES aliases(run_id, alias));
            CREATE TABLE IF NOT EXISTS review_events (
                seq INTEGER PRIMARY KEY, view_id TEXT REFERENCES records(id),
                kind TEXT NOT NULL, record_id TEXT REFERENCES records(id));
            CREATE TABLE IF NOT EXISTS snapshot_events (
                seq INTEGER PRIMARY KEY, snapshot_id TEXT REFERENCES records(id),
                state TEXT NOT NULL, reason TEXT NOT NULL);
            PRAGMA user_version=1;
        ''')

    def close(self):
        self.db.close()
        self.lock.close()

    @contextmanager
    def transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def blob_path(self, blob):
        require(isinstance(blob, str) and re.fullmatch(r'[0-9a-f]{64}', blob), 'Invalid object hash')
        return no_symlink_components(self.root / 'objects/sha256' / blob[:2] / blob[2:])

    def put(self, data):
        blob = digest(data)
        path = self.blob_path(blob)
        if path.exists():
            require(path.read_bytes() == data, 'Existing immutable object is corrupt')
        else:
            fd, name = tempfile.mkstemp(dir=self.root / 'staging')
            try:
                with os.fdopen(fd, 'wb') as out:
                    out.write(data)
                    out.flush()
                    os.fsync(out.fileno())
                path.parent.mkdir(exist_ok=True)
                fsync_dir(path.parent.parent)
                os.link(name, path)  # Never replaces an existing object.
                fsync_dir(path.parent)
            finally:
                os.unlink(name)
        self.db.execute('INSERT OR IGNORE INTO objects VALUES (?, ?)', (blob, len(data)))
        return blob

    def read(self, blob):
        path = self.blob_path(blob)
        require(path.is_file(), f'Missing object: {blob}')
        data = path.read_bytes()
        require(digest(data) == blob, f'Corrupt object: {blob}')
        return data

    def record(self, kind, payload, blobs=(), records=()):
        refs = sorted(set(blobs))
        links = sorted(set(records))
        for rid in links:
            self.get(rid)
        for blob in refs:
            data = self.read(blob)
            self.db.execute('INSERT OR IGNORE INTO objects VALUES (?, ?)', (blob, len(data)))
        body = {'serialization_version': 1, 'kind': kind, 'payload': payload, 'blobs': refs, 'records': links}
        encoded = canonical(body)
        rid = digest(encoded)
        self.db.execute('INSERT OR IGNORE INTO records VALUES (?, ?, ?)', (rid, kind, encoded.decode()))
        for blob in refs:
            self.db.execute('INSERT OR IGNORE INTO record_objects VALUES (?, ?)', (rid, blob))
        for target in links:
            self.db.execute('INSERT OR IGNORE INTO record_links VALUES (?, ?)', (rid, target))
        return rid

    def get(self, rid, kind=None):
        row = self.db.execute('SELECT * FROM records WHERE id=?', (rid,)).fetchone()
        require(row is not None, f'Missing record: {rid}')
        require(digest(row['payload'].encode()) == rid, f'Corrupt record: {rid}')
        body = json.loads(row['payload'])
        require(body['kind'] == row['kind'], 'Record kind mismatch')
        actual_blobs = sorted(r[0] for r in self.db.execute('SELECT blob FROM record_objects WHERE record_id=?', (rid,)))
        actual_links = sorted(r[0] for r in self.db.execute('SELECT target_id FROM record_links WHERE record_id=?', (rid,)))
        require(actual_blobs == body['blobs'] and actual_links == body['records'], 'Record reference index mismatch')
        require(kind is None or kind == row['kind'], f'Expected {kind}, got {row["kind"]}')
        for blob in body['blobs']:
            self.read(blob)
        for target in body['records']:
            require(self.db.execute('SELECT 1 FROM records WHERE id=?', (target,)).fetchone() is not None,
                    f'Missing linked record: {target}')
        return body['payload']

    def audit(self):
        errors = []
        for row in self.db.execute('PRAGMA integrity_check'):
            if row[0] != 'ok':
                errors.append(row[0])
        errors.extend(str(tuple(row)) for row in self.db.execute('PRAGMA foreign_key_check'))
        for row in self.db.execute('SELECT hash, size FROM objects'):
            try:
                require(len(self.read(row['hash'])) == row['size'], 'Object size mismatch')
            except CorpusError as e:
                errors.append(str(e))
        for row in self.db.execute('SELECT id FROM records'):
            try:
                self.get(row['id'])
            except CorpusError as e:
                errors.append(str(e))
        return {'ok': not errors, 'errors': errors,
                'objects': self.db.execute('SELECT count(*) FROM objects').fetchone()[0],
                'records': self.db.execute('SELECT count(*) FROM records').fetchone()[0],
                'aliases': self.db.execute('SELECT count(*) FROM aliases').fetchone()[0]}

    def backup(self, dest):
        require(self.audit()['ok'], 'Cannot back up inconsistent corpus')
        dest = no_symlink_components(dest)
        require(not dest.exists(), 'Backup destination exists')
        require(not dest.is_relative_to(self.root), 'Backup must be outside corpus root')
        dest.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix='.brrr-backup-', dir=dest.parent))
        try:
            db = sqlite3.connect(stage / 'corpus.sqlite')
            try:
                self.db.backup(db)
            finally:
                db.close()
            entries = {}
            for row in self.db.execute('SELECT hash FROM objects ORDER BY hash'):
                blob = row['hash']
                data = self.read(blob)
                rel = f'objects/sha256/{blob[:2]}/{blob[2:]}'
                write_bytes(stage / rel, data)
                entries[rel] = blob
            with (stage / 'corpus.sqlite').open('rb') as dbfile:
                os.fsync(dbfile.fileno())
            entries['corpus.sqlite'] = digest((stage / 'corpus.sqlite').read_bytes())
            write_bytes(stage / 'backup.json', canonical({'schema_version': 1, 'files': entries}))
            for parent, _, _ in os.walk(stage, topdown=False):
                fsync_dir(parent)
            os.rename(stage, dest)
            fsync_dir(dest.parent)
        finally:
            if stage.exists():
                shutil.rmtree(stage)
        return {'backup': str(dest), 'files': len(entries)}


def restore_backup(source, dest):
    files = tree_bytes(source)
    require('backup.json' in files, 'Missing backup manifest')
    manifest = json.loads(files['backup.json'])
    keys(manifest, ['schema_version', 'files'])
    require(manifest['schema_version'] == 1, 'Unsupported backup version')
    require(set(files) == set(manifest['files']) | {'backup.json'}, 'Backup file set mismatch')
    for name, expected in manifest['files'].items():
        require(digest(files[name]) == expected, f'Backup hash mismatch: {name}')
    require(not Path(dest).exists(), 'Restore destination must be new')
    # Validate a scratch copy before publishing the restored tree.
    with tempfile.TemporaryDirectory(prefix='brrr-restore-') as scratch:
        check = Path(scratch).resolve() / 'corpus'
        publish_tree(check, {k: v for k, v in files.items() if k != 'backup.json'})
        corpus = Corpus(check)
        try:
            result = corpus.audit()
            require(result['ok'], 'Restored corpus fails integrity audit')
        finally:
            corpus.close()
    publish_tree(dest, {k: v for k, v in files.items() if k != 'backup.json'})
    return {'restored': str(dest), **result}
