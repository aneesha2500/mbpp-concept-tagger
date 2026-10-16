"""The concept rules, decided on Python's AST. Each rule is syntactic, so a label is a fact about
the code that anyone can check by reading it.

- loop: a ``for`` or ``while`` statement (comprehensions do not count).
- comprehension: a list, set or dict comprehension, or a generator expression.
- conditional: an ``if``/``elif`` statement or a conditional expression ``a if c else b``
  (an ``if`` clause inside a comprehension does not count).
- recursion: a function that calls itself by its plain name inside its own ``def``.
- dict_or_set: a dict or set display or comprehension, or a call to dict, set, frozenset,
  Counter, defaultdict or OrderedDict (by plain name or as an attribute, e.g. collections.Counter).
- lambda: a lambda expression.
- regex: the code imports the ``re`` module (``import re``, ``import re as x``, ``from re import ...``).
- class_def: a ``class`` statement.
- exception: a ``try`` or ``raise`` statement.
- import: any ``import`` or ``from ... import`` statement.
"""

from __future__ import annotations

import ast
import json
import warnings
from functools import cache
from pathlib import Path

from contract import Concept, SnippetInput, SnippetLabel, SnippetOutput, TagInput, TagOutput

DATA = Path(__file__).with_name("data") / "mbpp_test_code.json"
FIRST, LAST = 11, 510
MAX_IDS = 5
DICT_OR_SET_CALLS = {"dict", "set", "frozenset", "Counter", "defaultdict", "OrderedDict"}


@cache
def snippets() -> dict[int, dict]:
    return {row["task_id"]: row for row in json.loads(DATA.read_text(encoding="utf-8"))}


def snippet(task_id: int) -> dict:
    if not FIRST <= task_id <= LAST:
        raise ValueError(f"task_id must be an MBPP test-split id, {FIRST} to {LAST}")
    return snippets()[task_id]


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def concepts(code: str) -> list[Concept]:
    """The concepts ``code`` meets, in the order of the Concept enum."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse(code)
    found: set[Concept] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            found.add(Concept.LOOP)
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            found.add(Concept.COMPREHENSION)
            if isinstance(node, (ast.SetComp, ast.DictComp)):
                found.add(Concept.DICT_OR_SET)
        elif isinstance(node, (ast.If, ast.IfExp)):
            found.add(Concept.CONDITIONAL)
        elif isinstance(node, (ast.Dict, ast.Set)) or isinstance(node, ast.Call) and _call_name(node) in DICT_OR_SET_CALLS:
            found.add(Concept.DICT_OR_SET)
        elif isinstance(node, ast.Lambda):
            found.add(Concept.LAMBDA)
        elif isinstance(node, ast.ClassDef):
            found.add(Concept.CLASS_DEF)
        elif isinstance(node, (ast.Try, ast.TryStar, ast.Raise)):
            found.add(Concept.EXCEPTION)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            found.add(Concept.IMPORT)
            names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module]
            if "re" in names:
                found.add(Concept.REGEX)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == node.name:
                    found.add(Concept.RECURSION)
                    break
    return [concept for concept in Concept if concept in found]


def get_snippet(given: SnippetInput, workspace: Path) -> SnippetOutput:
    row = snippet(given.task_id)
    return SnippetOutput(task_id=row["task_id"], text=row["text"], code=row["code"])


def tag_snippets(given: TagInput, workspace: Path) -> TagOutput:
    """The tag-concepts reference: every snippet labelled by the rules, pinned before the agent runs."""
    ids = given.task_ids
    if not 1 <= len(ids) <= MAX_IDS or len(set(ids)) != len(ids):
        raise ValueError(f"task_ids must be 1 to {MAX_IDS} distinct ids")
    return TagOutput(labels=[SnippetLabel(task_id=i, concepts=concepts(snippet(i)["code"])) for i in ids])
