import json
import re
from typing import Any, Dict, Iterable, List, Set

from langchain_core.messages import HumanMessage, ToolMessage

EXR_RE = re.compile(r"\bexr_[a-zA-Z0-9]+\b")


def extract_exercise_ids_from_text(text: str) -> Set[str]:
    """Fallback: Extract exr_* IDs from any raw text."""
    return set(EXR_RE.findall(text))


def human_and_tool_only(messages: List[Any]) -> List[Any]:
    """Keep user instructions + tool outputs only."""
    return [m for m in messages if isinstance(m, (HumanMessage, ToolMessage))]


def extract_exercise_ids(messages: Iterable[Any]) -> Set[str]:
    """Extract unique exercise IDs from ToolMessages (list/dict/json-string/text)."""
    ids: Set[str] = set()

    for msg in messages:
        if not isinstance(msg, ToolMessage):
            continue

        content = msg.content

        # Case 1: structured list (best)
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    ex_id = item.get("id")
                    if isinstance(ex_id, str) and ex_id.startswith("exr_"):
                        ids.add(ex_id)

        # Case 2: string (JSON string OR YAML/text dump)
        elif isinstance(content, str):
            try:
                parsed = json.loads(content)

                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict):
                            ex_id = item.get("id")
                            if isinstance(ex_id, str) and ex_id.startswith("exr_"):
                                ids.add(ex_id)

                elif isinstance(parsed, dict):
                    ex_id = parsed.get("id")
                    if isinstance(ex_id, str) and ex_id.startswith("exr_"):
                        ids.add(ex_id)

            except json.JSONDecodeError:
                ids.update(extract_exercise_ids_from_text(content))

    return ids


def extract_exercise_objects(messages: Iterable[Any]) -> List[Dict[str, str]]:
    """Get complete exercise objects (name + id), deduped by id."""
    exercises: List[Dict[str, str]] = []
    seen_ids: Set[str] = set()

    for msg in messages:
        if not isinstance(msg, ToolMessage):
            continue

        content = msg.content

        # list form
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    ex_id = item.get("id")
                    if (
                        isinstance(ex_id, str)
                        and ex_id.startswith("exr_")
                        and ex_id not in seen_ids
                    ):
                        exercises.append(
                            {"name": item.get("name", "unknown"), "id": ex_id}
                        )
                        seen_ids.add(ex_id)

        # json string form
        elif isinstance(content, str):
            try:
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict):
                            ex_id = item.get("id")
                            if (
                                isinstance(ex_id, str)
                                and ex_id.startswith("exr_")
                                and ex_id not in seen_ids
                            ):
                                exercises.append(
                                    {"name": item.get("name", "unknown"), "id": ex_id}
                                )
                                seen_ids.add(ex_id)
            except json.JSONDecodeError:
                # text/yaml case: can't reliably reconstruct name+id pairs
                pass

    return exercises
