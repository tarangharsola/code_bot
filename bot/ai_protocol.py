from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FileWrite:
    path: str
    content: str


@dataclass(frozen=True)
class ChangeSet:
    summary: str
    writes: list[FileWrite]
    deletes: list[str]


class ProtocolError(RuntimeError):
    pass


def _is_safe_rel_path(path: str) -> bool:
    if not path or path.strip() != path:
        return False
    if path.startswith("/") or path.startswith("\\"):
        return False
    if ":" in path:
        return False
    parts = path.replace("\\", "/").split("/")
    if any(p in ("..", "") for p in parts):
        return False
    if parts[0] == ".git":
        return False
    return True


def parse_changeset(obj: dict[str, Any]) -> ChangeSet:
    if not isinstance(obj, dict):
        raise ProtocolError("changeset must be a JSON object")

    summary = obj.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise ProtocolError("Missing or invalid 'summary'")

    writes_raw = obj.get("writes", [])
    deletes_raw = obj.get("deletes", [])

    if not isinstance(writes_raw, list) or not isinstance(deletes_raw, list):
        raise ProtocolError("'writes' and 'deletes' must be lists")

    writes: list[FileWrite] = []
    for w in writes_raw:
        if not isinstance(w, dict):
            raise ProtocolError("Each write must be an object")
        path = w.get("path")
        content = w.get("content")
        if not isinstance(path, str) or not _is_safe_rel_path(path):
            raise ProtocolError(f"Unsafe write path: {path!r}")
        if not isinstance(content, str):
            raise ProtocolError(f"Invalid content for {path!r}")
        writes.append(FileWrite(path=path, content=content))

    deletes: list[str] = []
    for p in deletes_raw:
        if not isinstance(p, str) or not _is_safe_rel_path(p):
            raise ProtocolError(f"Unsafe delete path: {p!r}")
        deletes.append(p)

    if not writes and not deletes:
        raise ProtocolError("Empty changeset (no writes/deletes)")

    return ChangeSet(summary=summary.strip(), writes=writes, deletes=deletes)


def validate_size(changeset: ChangeSet, *, max_file_chars: int = 200_000, max_total_chars: int = 800_000) -> None:
    total = 0
    for w in changeset.writes:
        if len(w.content) > max_file_chars:
            raise ProtocolError(f"File too large: {w.path} ({len(w.content)} chars)")
        total += len(w.content)
    if total > max_total_chars:
        raise ProtocolError(f"Changeset too large: {total} chars")
