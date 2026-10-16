"""Each tool's and task's typed input and output (see nanoagent.plugin.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    GET_SNIPPET = "get_snippet"
    TAG_SNIPPETS = "tag_snippets"


class Task(Enum):
    TAG_CONCEPTS = "tag-concepts"


class Concept(Enum):
    LOOP = "loop"
    COMPREHENSION = "comprehension"
    CONDITIONAL = "conditional"
    RECURSION = "recursion"
    DICT_OR_SET = "dict_or_set"
    LAMBDA = "lambda"
    REGEX = "regex"
    CLASS_DEF = "class_def"
    EXCEPTION = "exception"
    IMPORT = "import"


TASK_ID = "An MBPP test-split task id, 11 to 510"


@dataclass
class SnippetInput(Output):
    task_id: Annotated[int, TASK_ID]


@dataclass
class SnippetOutput(Output):
    task_id: Annotated[int, TASK_ID]
    text: Annotated[str, "The problem statement the code solves"]
    code: Annotated[str, "MBPP's reference solution, the code to label"]


@dataclass
class SnippetLabel(Output):
    task_id: Annotated[int, TASK_ID]
    concepts: Annotated[list[Concept], "Every concept whose rule the code meets, each once"]


@dataclass
class TagInput(Output):
    task_ids: Annotated[list[int], "1 to 5 distinct MBPP test-split task ids"]


@dataclass
class TagOutput(Output):
    labels: Annotated[list[SnippetLabel], "One label per task id, in the order given"]


TOOLS = {
    Tool.GET_SNIPPET: (SnippetInput, SnippetOutput),
    Tool.TAG_SNIPPETS: (TagInput, TagOutput),
}
TASKS = {Task.TAG_CONCEPTS: (TagInput, TagOutput)}
