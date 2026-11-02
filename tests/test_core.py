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
    def test_history_and_clear(self):
        with tempfile.TemporaryDirectory() as directory:
            store = MemoryStore(str(Path(directory) / "test.db"))
            store.add_message("c1", "user", "Cześć")
            store.add_message("c1", "assistant", "Witaj")
            self.assertEqual(len(store.history("c1")), 2)
            store.clear("c1")
            self.assertEqual(store.history("c1"), [])


if __name__ == "__main__":
    unittest.main()
