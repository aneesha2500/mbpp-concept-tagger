"""tag_snippets (the tag-concepts reference) and the tag-concepts task's outcome check.

The agent's labels are compared, snippet by snippet, with the reference labels the rules give on
Python's AST, pinned before the agent started. The task is valid only when every snippet's set of
concepts is exactly right; the score is the micro-averaged F1 over (task id, concept) pairs, so a
partly right answer gets partial credit.
"""

from .checks import labels_problem, result, task_ids_problem


def verify_input(value):
    problem = task_ids_problem(value.task_ids)
    return result(False, problem) if problem else result(True, "input is valid")


def verify_output(input_value, output_value, workspace):
    problem = labels_problem(input_value.task_ids, output_value.labels)
    return result(False, problem) if problem else result(True, "labels are well formed")


def _pairs(labels):
    return {(label.task_id, concept.value) for label in labels for concept in label.concepts}


def verify_task(arguments, output, reference, workspace):
    """``output`` and ``reference``: contract TagOutputs for ``arguments.task_ids``."""
    problem = task_ids_problem(arguments.task_ids) or labels_problem(arguments.task_ids, output.labels)
    if problem:
        return result(False, problem, score=0.0)
    got, want = _pairs(output.labels), _pairs(reference.labels)
    true_positive = len(got & want)
    if not got and not want:
        f1 = 1.0
    else:
        f1 = 2 * true_positive / (len(got) + len(want))
    mistakes = {}
    for mine, truth in zip(output.labels, reference.labels):
        extra = sorted({c.value for c in mine.concepts} - {c.value for c in truth.concepts})
        missing = sorted({c.value for c in truth.concepts} - {c.value for c in mine.concepts})
        if extra or missing:
            mistakes[str(truth.task_id)] = {"extra": extra, "missing": missing}
    if mistakes:
        return result(
            False,
            f"{len(mistakes)} of {len(reference.labels)} snippet(s) mislabelled (micro F1 {f1:.3f})",
            score=f1,
            mistakes=mistakes,
        )
    return result(True, f"all {len(reference.labels)} snippet(s) labelled exactly", score=1.0)
