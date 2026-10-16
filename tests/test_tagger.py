from __future__ import annotations

from pathlib import Path

import pytest

from contract import Concept, SnippetInput, TagInput
from plugin import get_snippet, tag_snippets
from plugin.tagger import concepts


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("def f(xs):\n    for x in xs:\n        pass", [Concept.LOOP]),
        ("def f(xs):\n    return [x for x in xs if x]", [Concept.COMPREHENSION]),  # comprehension if: not conditional
        ("def f(x):\n    return 1 if x else 2", [Concept.CONDITIONAL]),
        ("def f(n):\n    return f(n - 1)", [Concept.RECURSION]),
        ("class S:\n    def pop(self):\n        return self.items.pop()", [Concept.CLASS_DEF]),  # not recursion
        ("def f(xs):\n    return {x: 1 for x in xs}", [Concept.COMPREHENSION, Concept.DICT_OR_SET]),
        ("import collections\ndef f(xs):\n    return collections.Counter(xs)", [Concept.DICT_OR_SET, Concept.IMPORT]),
        ("from re import sub\ndef f(s):\n    return sub('a', '', s)", [Concept.REGEX, Concept.IMPORT]),
        ("import regex\ndef f(s):\n    return s", [Concept.IMPORT]),  # not the re module
        ("def f(xs):\n    return sorted(xs, key=lambda x: -x)", [Concept.LAMBDA]),
        ("def f(x):\n    try:\n        return int(x)\n    except ValueError:\n        raise", [Concept.EXCEPTION]),
        ("def f(x):\n    return x", []),
    ],
)
def test_rules(code: str, expected: list) -> None:
    assert concepts(code) == expected


def test_tools() -> None:
    assert "def " in get_snippet(SnippetInput(task_id=11), Path(".")).code
    with pytest.raises(ValueError):
        get_snippet(SnippetInput(task_id=9), Path("."))
    with pytest.raises(ValueError):
        tag_snippets(TagInput(task_ids=[11, 11]), Path("."))
