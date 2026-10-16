"""get_snippet: the snippet returned is the one asked for."""

from .checks import result, task_id_problem


def verify_input(value):
    problem = task_id_problem(value.task_id)
    return result(False, problem) if problem else result(True, "input is valid")


def verify_output(input_value, output_value, workspace):
    if output_value.task_id != input_value.task_id:
        return result(False, "output is for another task")
    if not output_value.code.strip() or "def " not in output_value.code:
        return result(False, "the snippet has no code to label")
    return result(True, "snippet is well formed")
