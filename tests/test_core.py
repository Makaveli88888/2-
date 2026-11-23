import tempfile
import unittest
from pathlib import Path

from app.database import MemoryStore
from app.tools import calculator, current_time, execute_tool


class ToolTests(unittest.TestCase):
    def test_calculator(self):
        self.assertEqual(calculator("2 + 3 * 4")["result"], 14)

    def test_calculator_rejects_code(self):
        with self.assertRaises((ValueError, SyntaxError)):
            calculator("__import__('os').system('echo unsafe')")

    def test_calculator_rejects_large_exponent(self):
        with self.assertRaises(ValueError):
            calculator("2 ** 99")

    def test_tool_allowlist(self):
        with self.assertRaises(ValueError):
            execute_tool("shell", {"command": "whoami"})

    def test_current_time(self):
        self.assertIn("+00:00", current_time()["utc"])


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.store = MemoryStore("sqlite+pysqlite:///" + str(Path(self.directory.name) / "test.db"))

    def tearDown(self):
        self.store.close()
        self.directory.cleanup()

    def test_history_and_clear(self):
        self.store.add_message("c1", "user-1", "user", "Cześć")
        self.store.add_message("c1", "user-1", "assistant", "Witaj")
        self.assertEqual(len(self.store.history("c1", "user-1")), 2)
        self.store.clear("c1", "user-1")
        self.assertEqual(self.store.history("c1", "user-1"), [])

    def test_conversation_isolation(self):
        self.store.add_message("private-chat", "alice", "user", "sekret")
        with self.assertRaises(PermissionError):
            self.store.history("private-chat", "bob")
        with self.assertRaises(PermissionError):
            self.store.clear("private-chat", "bob")
        with self.assertRaises(PermissionError):
            self.store.add_message("private-chat", "bob", "user", "próba przejęcia")

    def test_unknown_conversation_is_not_created_by_read(self):
        with self.assertRaises(PermissionError):
            self.store.history("missing-chat", "alice")
        with self.assertRaises(PermissionError):
            self.store.clear("missing-chat", "alice")


if __name__ == "__main__":
    unittest.main()
