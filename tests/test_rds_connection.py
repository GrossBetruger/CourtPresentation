import unittest

from utils import get_remote_engine


class TestRds(unittest.TestCase):
    def test_rds(self):
        rds_engine = get_remote_engine()
        rds_engine_cursor = rds_engine.cursor()
        rds_engine_cursor.execute("select * from file_download_info limit 100")
        self.assertEqual(100, len(list(rds_engine_cursor.fetchmany(100))))


if __name__ == '__main__':
    unittest.main()
