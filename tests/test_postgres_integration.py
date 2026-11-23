import os
import unittest
import uuid

from app.database import MemoryStore


@unittest.skipUnless(os.getenv("TEST_DATABASE_URL"), "TEST_DATABASE_URL is not configured")
class PostgreSQLIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = MemoryStore(os.environ["TEST_DATABASE_URL"])

    @classmethod
    def tearDownClass(cls):
        cls.store.close()

    def test_two_users_cannot_read_or_delete_each_others_conversation(self):
        conversation_id = "ci-" + str(uuid.uuid4())
        self.store.add_message(conversation_id, "alice", "user", "alice-private")
        self.assertEqual(self.store.history(conversation_id, "alice")[0]["content"], "alice-private")
        with self.assertRaises(PermissionError):
            self.store.history(conversation_id, "bob")
        with self.assertRaises(PermissionError):
            self.store.clear(conversation_id, "bob")
        self.assertEqual(self.store.history(conversation_id, "alice")[0]["content"], "alice-private")
        self.store.clear(conversation_id, "alice")


if __name__ == "__main__":
    unittest.main()
