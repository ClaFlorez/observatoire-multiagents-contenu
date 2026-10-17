import tempfile
import unittest
from pathlib import Path

from observatoire.import_youtube import analyser
from observatoire.stockage import charger_import, enregistrer_import, lister_imports


class StorageTests(unittest.TestCase):
    def test_roundtrip_deduplication_and_origin_separation(self):
        source = Path(__file__).resolve().parents[1] / 'data' / 'examples'
        result = analyser(source, 'fictive')
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / 'nested' / 'local.sqlite'
            self.assertEqual(lister_imports(database), [])
            identifier, inserted = enregistrer_import(result, database)
            self.assertTrue(inserted)
            self.assertEqual(charger_import(database, identifier), result)
            self.assertEqual(enregistrer_import(result, database), (identifier, False))
            self.assertEqual(len(lister_imports(database)), 1)
            real = analyser(source, 'reelle')
            other_id, inserted = enregistrer_import(real, database)
            self.assertTrue(inserted)
            self.assertNotEqual(identifier, other_id)
            with self.assertRaises(KeyError):
                charger_import(database, 'absent')


if __name__ == '__main__':
    unittest.main()
