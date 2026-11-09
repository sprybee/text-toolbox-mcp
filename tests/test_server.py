import asyncio
import unittest

from text_toolbox_mcp.server import MAX_CHARACTERS, deduplicate_lines, mcp, sha256_text, text_stats


class ToolboxTests(unittest.TestCase):
    def test_empty_stats(self):
        self.assertEqual(text_stats(""), {"characters": 0, "utf8_bytes": 0, "words": 0, "lines": 0})

    def test_unicode_stats(self):
        self.assertEqual(text_stats("你好 world\n"), {"characters": 9, "utf8_bytes": 13, "words": 2, "lines": 1})

    def test_known_hash(self):
        self.assertEqual(sha256_text("abc")["digest"], "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_dedup(self):
        self.assertEqual(deduplicate_lines("a\r\nb\r\na\r\n"), {"text": "a\nb\n", "input_lines": 3, "output_lines": 2, "removed_lines": 1})

    def test_casefold_and_whitespace(self):
        self.assertEqual(deduplicate_lines("Straße\nSTRASSE\n Straße", False)["text"], "Straße\n Straße")

    def test_empty_dedup(self):
        self.assertEqual(deduplicate_lines("")["text"], "")
        self.assertEqual(deduplicate_lines("\n\n")["text"], "\n")

    def test_limits(self):
        self.assertEqual(text_stats("x" * MAX_CHARACTERS)["characters"], MAX_CHARACTERS)
        for tool in (text_stats, sha256_text, deduplicate_lines):
            with self.subTest(tool=tool.__name__), self.assertRaises(ValueError):
                tool("x" * (MAX_CHARACTERS + 1))

    def test_tool_registration(self):
        tools = asyncio.run(mcp.list_tools())
        self.assertEqual({tool.name for tool in tools}, {"text_stats", "sha256_text", "deduplicate_lines"})

    def test_sdk_tool_call(self):
        result = asyncio.run(mcp.call_tool("sha256_text", {"text": "abc"}))
        self.assertIn("ba7816bf", str(result))


if __name__ == "__main__":
    unittest.main()
