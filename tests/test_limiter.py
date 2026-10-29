import unittest
import tempfile
from pathlib import Path
import db
from limiter import TokenBucket

class LimiterTests(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file for the test
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        
        # Override the DB_PATH in the db module
        self.original_db_path = db.DB_PATH
        db.DB_PATH = Path(self.temp_db.name)
        db.init_db()
        
        self.bucket = TokenBucket(capacity=3, refill_rate=1.0)

    def tearDown(self):
        # Restore original DB_PATH and delete temporary files
        db.DB_PATH = self.original_db_path
        
        # Clean up Windows WAL files first
        for suffix in ["", "-wal", "-shm"]:
            path = Path(self.temp_db.name + suffix)
            if path.exists():
                try:
                    path.unlink()
                except PermissionError:
                    pass

    def test_burst_and_block(self):
        # 3 allowed
        self.assertTrue(self.bucket.consume("127.0.0.1")[0])
        self.assertTrue(self.bucket.consume("127.0.0.1")[0])
        self.assertTrue(self.bucket.consume("127.0.0.1")[0])
        
        # 4th blocked
        allowed, retry = self.bucket.consume("127.0.0.1")
        self.assertFalse(allowed)
        self.assertGreater(retry, 0)

    def test_refill(self):
        self.bucket.consume("127.0.0.1")
        self.bucket.consume("127.0.0.1")
        self.bucket.consume("127.0.0.1")
        
        # Manually manipulate time in DB to simulate waiting
        with db.get_connection() as conn:
            conn.execute("UPDATE buckets SET last_refill = last_refill - 2.1 WHERE key = '127.0.0.1'")
            conn.commit()
            
        # Should have 2 tokens now
        self.assertTrue(self.bucket.consume("127.0.0.1")[0])
        self.assertTrue(self.bucket.consume("127.0.0.1")[0])
        self.assertFalse(self.bucket.consume("127.0.0.1")[0])

if __name__ == "__main__":
    unittest.main()