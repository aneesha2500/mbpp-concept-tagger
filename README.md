# MBPP Concept Tagger

A `nanoagent.plugin/v1` plugin, built with the structure of NanoAgent's
reference plugin, [arxiv-source](https://github.com/zeyuyang8/arxiv-source).
An agent labels MBPP reference solutions with the programming concepts they
use. Each concept is defined by a syntactic rule, so the right labels are a
fact about the code that a program can decide.

## Tools

| Tool | Does | Code |
|---|---|---|
| `get_snippet` | Returns the problem statement and MBPP's reference solution for a test-split task id (11 to 510) | `src/plugin/tagger.py` |
| `tag_snippets` | Labels snippets with the concept rules, decided on Python's AST; the `tag-concepts` reference | `src/plugin/tagger.py` |

### Tasks

| Task | Does | Runner |
|---|---|---|
| `tag-concepts` | Labels 1 to 5 MBPP solutions with the concepts they use, by fixed syntactic rules | `agent`, with `get_snippet`; reference `tag_snippets` |

### The rules

| Concept | Rule |
|---|---|
| `loop` | a `for` or `while` statement (comprehensions do not count) |
| `comprehension` | a list, set or dict comprehension, or a generator expression |
| `conditional` | an `if`/`elif` statement or `a if c else b` (an `if` inside a comprehension does not count) |
| `recursion` | a function calls itself by its plain name inside its own `def` |
| `dict_or_set` | a dict/set literal or comprehension, or a call to `dict`, `set`, `frozenset`, `Counter`, `defaultdict` or `OrderedDict` |
| `lambda` | a lambda expression |
| `regex` | the code imports the `re` module |
| `class_def` | a `class` statement |
| `exception` | a `try` or `raise` statement |
| `import` | any import statement |

The task's instructions state the same rules to the agent. Before the agent
starts, NanoAgent runs `tag_snippets` and pins its labels. `verifier/tags.py`
compares the agent's labels with them snippet by snippet. The task is valid
only when every snippet's concept set is exactly right. The score is the
micro-averaged F1 over (task id, concept) pairs, and the verdict lists each
snippet's extra and missing concepts. A label list that skips a task id, or
gives them in another order, or names a concept twice, is refused.

Data: MBPP, Austin et al., *Program Synthesis with Large Language Models*
(2021), [google-research/mbpp](https://github.com/google-research/google-research/tree/master/mbpp),
CC BY 4.0, test split bundled in `src/plugin/data/mbpp_test_code.json`.

## Layout

```text
.
├── nanoagent.yaml   # manifest (a slimconfig ManifestConfig): id, runtime, permissions, tools, tasks
├── contract.py      # each tool's and task's typed input and output; Concept is an Enum
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .env             # environment variable NAMEs this plugin needs (none)
├── src/plugin/      # the MCP server (__main__.py, IMPLEMENTATIONS), tagger.py and data/
├── tests/           # test_verifier.py (correct, wrong, missing, malformed, boundary) and test_tagger.py
├── ui/              # outputs drawn from their JSON Schema: renderers.js and renderers.css
├── product/         # the product page a catalog shows: product.yaml and icon.svg
└── verifier/        # deterministic verifier package: snippet.py, tags.py, checks.py
```

## Develop and run

```bash
uv sync --extra dev
uv run pytest
```

On RUSH Lab, ask the plugin's chat, for example "tag the concepts in MBPP
tasks 11, 40, 173, 367 and 400".
