"""Bounded, side-effect-free tools exposed via the official MCP SDK."""

import hashlib
import re

from mcp.server.fastmcp import FastMCP

MAX_CHARACTERS = 100_000

mcp = FastMCP(
    "Text Toolbox",
    host="0.0.0.0",
    port=9000,
    streamable_http_path="/mcp",
    stateless_http=True,
)


def _validate(text: str) -> None:
    if len(text) > MAX_CHARACTERS:
        raise ValueError(f"text must contain at most {MAX_CHARACTERS} Unicode code points")


@mcp.tool()
def text_stats(text: str) -> dict[str, int]:
    """Count Unicode code points, UTF-8 bytes, whitespace-delimited words and lines.

    Empty input has zero lines. A final line terminator does not add an empty
    line. Words are non-whitespace runs, not language-aware word segmentation.
    Input is limited to 100,000 Unicode code points; no text is persisted.
    """
    _validate(text)
    return {
        "characters": len(text),
        "utf8_bytes": len(text.encode("utf-8")),
        "words": len(re.findall(r"\S+", text)),
        "lines": len(text.splitlines()),
    }


@mcp.tool()
def sha256_text(text: str) -> dict[str, str]:
    """Return the SHA-256 hex digest of the exact UTF-8 input, without normalization.

    Limited to 100,000 Unicode code points. Hashing is not encryption and is
    not suitable for password storage. No files or network services are used.
    """
    _validate(text)
    return {"algorithm": "sha256", "encoding": "utf-8", "digest": hashlib.sha256(text.encode("utf-8")).hexdigest()}


@mcp.tool()
def deduplicate_lines(text: str, case_sensitive: bool = True) -> dict[str, str | int]:
    """Keep the first occurrence of each line and preserve its original spelling.

    Comparison preserves whitespace; optional case-insensitive comparison uses
    Unicode casefold. Output uses LF separators and retains one final LF when
    input ended in a recognized line terminator. Empty input stays empty.
    Limited to 100,000 Unicode code points; does not write to disk.
    """
    _validate(text)
    lines = text.splitlines()
    seen: set[str] = set()
    kept: list[str] = []
    for line in lines:
        key = line if case_sensitive else line.casefold()
        if key not in seen:
            seen.add(key)
            kept.append(line)
    result = "\n".join(kept)
    if text and text.endswith(("\n", "\r", "\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029")):
        result += "\n"
    return {"text": result, "input_lines": len(lines), "output_lines": len(kept), "removed_lines": len(lines) - len(kept)}
