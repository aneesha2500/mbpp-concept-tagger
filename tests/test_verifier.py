from __future__ import annotations

from pathlib import Path

import pytest
from slimconfig import build_output, plain_output

import verifier
from contract import TagInput, TagOutput
from plugin import tag_snippets

IDS = [11, 40, 173, 367, 400]
# What the rules give, worked out by reading each snippet:
TRUTH = {
    11: ["loop", "conditional"],
    40: ["dict_or_set", "import"],
    173: ["regex", "import"],
    367: ["conditional", "recursion", "class_def"],
    400: ["comprehension", "dict_or_set"],
}


def reference(ids=IDS) -> TagOutput:
    return build_output(plain_output(tag_snippets(TagInput(task_ids=ids), Path("."))), TagOutput)


def verify(labels: list[dict], ids=IDS) -> dict:
    return verifier.verify_task(
        "tag-concepts",
        build_output({"task_ids": ids}, TagInput),
        build_output({"labels": labels}, TagOutput),
        reference(ids),
        ".",
    )


def answer() -> list[dict]:
    return [{"task_id": i, "concepts": list(TRUTH[i])} for i in IDS]


def test_the_reference_matches_a_hand_labelling() -> None:
    assert {label.task_id: [c.value for c in label.concepts] for label in reference().labels} == TRUTH


def test_approves_exact_labels_in_any_concept_order() -> None:
    labels = answer()
    labels[3]["concepts"] = list(reversed(labels[3]["concepts"]))
    verdict = verify(labels)
    assert verdict["valid"] is True and verdict["score"] == 1.0


@pytest.mark.parametrize(
    ("task_id", "concepts", "extra", "missing"),
    [
        (11, ["loop"], [], ["conditional"]),  # missed one
        (40, ["dict_or_set", "import", "loop"], ["loop"], []),  # added one
        (400, ["comprehension"], [], ["dict_or_set"]),  # dict comprehension is also dict_or_set
        (367, [], [], ["class_def", "conditional", "recursion"]),  # empty label
    ],
)
def test_refuses_wrong_labels_with_partial_f1(task_id: int, concepts: list, extra: list, missing: list) -> None:
    verdict = verify(_with(task_id, concepts))
    assert verdict["valid"] is False and 0.0 < verdict["score"] < 1.0
    assert verdict["details"]["mistakes"][str(task_id)] == {"extra": extra, "missing": missing}


def _with(task_id: int, concepts: list) -> list[dict]:
    labels = answer()
    for label in labels:
        if label["task_id"] == task_id:
            label["concepts"] = concepts
    return labels


def test_refuses_missing_reordered_or_duplicated_entries() -> None:
    assert verify(answer()[:4])["valid"] is False  # a snippet missing
    assert verify(list(reversed(answer())))["valid"] is False  # wrong order
    doubled = answer()
    doubled[0]["concepts"] = ["loop", "loop", "conditional"]
    assert verify(doubled)["valid"] is False


def test_refuses_an_unknown_concept() -> None:
    with pytest.raises(ValueError):
        build_output({"labels": [{"task_id": 11, "concepts": ["recursionish"]}]}, TagOutput)


def test_an_all_wrong_answer_scores_zero() -> None:
    verdict = verify([{"task_id": i, "concepts": ["lambda"]} for i in IDS])
    assert verdict["valid"] is False and verdict["score"] == 0.0


@pytest.mark.parametrize(
    ("ids", "valid"),
    [([11], True), (IDS, True), ([], False), ([11, 11], False), ([10], False), ([511], False), ([11, 12, 13, 14, 15, 16], False)],
)
def test_checks_the_task_ids(ids: list, valid: bool) -> None:
    assert verifier.verify_input("tag_snippets", build_output({"task_ids": ids}, TagInput))["valid"] is valid


def test_a_snippet_with_no_concepts_is_right_when_left_empty() -> None:
    assert reference([17]).labels[0].concepts == []
    assert verify([{"task_id": 17, "concepts": []}], ids=[17])["valid"] is True
    assert verify([{"task_id": 17, "concepts": ["loop"]}], ids=[17])["score"] == 0.0
