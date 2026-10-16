"""Checks shared by the tool verifiers. Pure functions of their arguments."""

FIRST, LAST = 11, 510
MAX_IDS = 5


def result(valid, message, *, score=None, **details):
    return {
        "valid": valid,
        "score": float(valid) if score is None else score,
        "message": message,
        "details": details,
    }


def task_id_problem(task_id):
    if not FIRST <= task_id <= LAST:
        return f"task_id {task_id} is not an MBPP test-split id, {FIRST} to {LAST}"
    return None


def task_ids_problem(task_ids):
    if not 1 <= len(task_ids) <= MAX_IDS:
        return f"task_ids must hold 1 to {MAX_IDS} ids"
    if len(set(task_ids)) != len(task_ids):
        return "task_ids must be distinct"
    for task_id in task_ids:
        problem = task_id_problem(task_id)
        if problem:
            return problem
    return None


def labels_problem(task_ids, labels):
    """What is wrong with the shape of a list of contract SnippetLabels for ``task_ids``, or None."""
    if [label.task_id for label in labels] != list(task_ids):
        return "labels must give one entry per task id, in the order given"
    for label in labels:
        if len(set(label.concepts)) != len(label.concepts):
            return f"task {label.task_id} lists a concept twice"
    return None
