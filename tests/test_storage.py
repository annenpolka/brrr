import json
import os
import tempfile
import unittest
from pathlib import Path

from brrr_corpus.cli import main, source_import
from brrr_corpus.legacy import import_legacy, inventory
from brrr_corpus.store import Corpus, CorpusError, restore_backup


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.run = self.root / 'synthetic-run'
        spec = self.run / 'specimens' / 'specimen-001'
        spec.mkdir(parents=True)
        packet = {'id': 'specimen-001', 'manifest': 'kind: SYNTHETIC_GROUNDED\nrepository: synthetic/repo\n',
                  'source': 'https://github.com/synthetic/repo/issues/1',
                  'curation': 'ACCEPT_R1', 'answer_key': 'restricted synthetic answer'}
        (spec / 'packet.json').write_text(json.dumps(packet))
        (spec / 'TASK.md').write_text('Synthetic legacy view.\r\n')
        self.c = Corpus(self.root / 'corpus')
        self.addCleanup(self.c.close)

    def test_t01_repeat_import_is_idempotent(self):
        before = inventory(self.run)
        first = import_legacy(self.c, self.run)
        counts = self.c.audit()
        second = import_legacy(self.c, self.run)
        self.assertEqual(first['archive_id'], second['archive_id'])
        self.assertEqual(second['new_aliases'], 0)
        self.assertEqual(second['new_revisions'], 0)
        self.assertEqual(counts, self.c.audit())
        self.assertEqual(before, inventory(self.run))
        rid = self.c.db.execute('SELECT record_id FROM legacy_revisions').fetchone()[0]
        record = self.c.get(rid)
        self.assertEqual(record['quality'], 'PENDING')
        self.assertEqual(record['claim_kind'], 'legacy_claim')
        self.assertFalse(record['local_execution_verified'])

    def test_t02_stop_after_objects_can_resume(self):
        with self.assertRaises(CorpusError):
            import_legacy(self.c, self.run, fail_at='after_objects')
        self.assertEqual(self.c.audit()['aliases'], 0)
        self.assertGreater(self.c.audit()['objects'], 0)
        self.assertEqual(import_legacy(self.c, self.run)['new_aliases'], 1)
        self.assertTrue(self.c.audit()['ok'])

    def test_metadata_transaction_rolls_back(self):
        with self.assertRaises(CorpusError):
            import_legacy(self.c, self.run, fail_at='before_commit')
        self.assertEqual(self.c.audit()['aliases'], 0)
        self.assertEqual(self.c.audit()['records'], 0)
        self.assertEqual(import_legacy(self.c, self.run)['new_aliases'], 1)

    def test_t03_response_loss_after_commit_does_not_duplicate(self):
        with self.assertRaises(CorpusError):
            import_legacy(self.c, self.run, fail_at='after_commit')
        self.assertEqual(import_legacy(self.c, self.run)['new_aliases'], 0)
        self.assertEqual(self.c.audit()['aliases'], 1)

    def test_legacy_edits_add_revisions_and_keep_old_bytes(self):
        first = import_legacy(self.c, self.run)
        old = self.c.get(first['archive_id'])
        (self.run / 'specimens/specimen-001/TASK.md').write_text('Changed legacy input')
        second = import_legacy(self.c, self.run)
        self.assertNotEqual(first['archive_id'], second['archive_id'])
        self.assertEqual(second['new_aliases'], 0)
        self.assertEqual(second['new_revisions'], 1)
        self.assertEqual(self.c.get(first['archive_id']), old)
        item = next(p for p in old['trees']['run'] if p['path'].endswith('TASK.md'))
        self.assertEqual(self.c.read(item['blob']), b'Synthetic legacy view.\r\n')

    def test_symlink_and_fifo_are_preserved_without_reading_targets(self):
        (self.run / 'external-link').symlink_to(self.root / 'does-not-exist')
        os.mkfifo(self.run / 'pipe')
        result = import_legacy(self.c, self.run)
        entries = {p['path']: p for p in self.c.get(result['archive_id'])['trees']['run']}
        self.assertEqual(entries['pipe']['type'], 'fifo')
        self.assertNotIn('blob', entries['pipe'])
        self.assertEqual(self.c.read(entries['external-link']['blob']), os.fsencode(str(self.root / 'does-not-exist')))

    def test_t25_backup_restore_and_corruption_detection(self):
        import_legacy(self.c, self.run)
        backup = self.root / 'backup'
        self.c.backup(backup)
        restored = self.root / 'restored'
        self.assertTrue(restore_backup(backup, restored)['ok'])
        copy = Corpus(restored)
        try:
            self.assertEqual(self.c.audit(), copy.audit())
        finally:
            copy.close()
        (backup / 'corpus.sqlite').write_bytes(b'corrupted')
        with self.assertRaises(CorpusError):
            restore_backup(backup, self.root / 'bad-restore')
        self.assertFalse((self.root / 'bad-restore').exists())

    def test_object_corruption_fails_audit(self):
        blob = self.c.put(b'hello')
        self.c.blob_path(blob).write_bytes(b'corrupt')
        self.assertFalse(self.c.audit()['ok'])
        with self.assertRaises(CorpusError):
            self.c.put(b'hello')

    def test_corpus_lock_rejects_second_coordinator(self):
        with self.assertRaises(CorpusError):
            Corpus(self.c.root)

    def test_t05_source_edit_preserves_revision_and_observation(self):
        text = self.root / 'original.txt'
        text.write_text('Synthetic original observation.\n')
        metadata = {'schema_version': 1, 'provider': 'synthetic', 'resource_kind': 'comment',
                    'provider_id': '1', 'url': 'https://example.invalid/comment/1',
                    'observed_at': '2026-09-08T00:00:00Z', 'provider_created_at': None,
                    'provider_updated_at': None, 'content_available_at': None, 'origin': 'synthetic'}
        first = source_import(self.c, text, metadata)
        again = source_import(self.c, text, metadata)
        self.assertEqual(first, again)
        metadata['observed_at'] = '2026-09-09T00:00:00Z'
        observed = source_import(self.c, text, metadata)
        self.assertEqual(first['source_revision'], observed['source_revision'])
        self.assertNotEqual(first['observation'], observed['observation'])
        text.write_text('Edited synthetic observation.')
        edited = source_import(self.c, text, metadata)
        self.assertEqual(first['source_id'], edited['source_id'])
        self.assertNotEqual(first['source_revision'], edited['source_revision'])
        self.assertEqual(self.c.read(self.c.get(first['source_revision'])['body_blob']), b'Synthetic original observation.\n')


if __name__ == '__main__':
    unittest.main()
