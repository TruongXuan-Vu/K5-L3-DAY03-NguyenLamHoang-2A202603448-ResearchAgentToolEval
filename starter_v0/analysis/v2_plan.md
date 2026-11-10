# V2 — Le Anh Son / 2A202603440

## Evidence and scope

Own baseline: `runs/v0_B_base_openrouter_20261110T105739326281.json`, 14/20.
Own v1: `runs/v1_B_base_openrouter_20261110T112052841713.json`, 17/20;
routing 100%, arguments 85%, multi-turn 100%, provider errors 0.
These are distinct from the team's 18/20 v1 run on main.

Own v1 failures:

| Case | Observation | V2 change |
|---|---|---|
| R11 | clarify omitted response_type; tool default is text, but grader checks the raw call | Explicitly set response_type=text |
| R12 | clarify asked for draft content using text instead of confirmation using yes_no | Ask for confirmation on delivery requests; require exact draft and explicit approval before any actual send |
| R13 | lookup omitted topic=news | Explicit news/timeframe argument rules, including multi-source requests |

The prompt also removes the conflicting single-tool-only instruction, defines
independent calls, and restricts send to actual delivery. It retains the latest
correction and previous constraints for multi-turn requests.

## New tool

`deduplicate(items, mode)` removes duplicate URLs from existing research items.
It runs locally without keys, network, disk writes, or publishing. The first item
and original order/metadata are retained. See `tools/deduplicate/TOOL.md` for URL
normalization and error behavior. Invalid model arguments return error dictionaries.

Registered in `tools/__init__.py` and `artifacts/tools.yaml`.
The group suite contains exactly 5 single-turn and 5 multi-turn cases, including
G05 (normalized URLs) and G08 (change to exact_url in conversation).
The grader compares tool and mode for these cases. Review the model's input items
manually: the starter's generic list comparison does not support object lists.
Output correctness and invalid inputs are tested offline in `tests/test_deduplicate.py`.

## Validation and limitations

Run all tests from the repository root:

```powershell
.\venv\Scripts\python.exe -m pytest starter_v0/tests -q
```

Existing TODO tests remain skipped; they are not completed by this change.
Observed offline result: **84 passed, 17 skipped**. The new deduplicate tests
cover normalization, exact mode, preserved meaningful differences, missing URLs,
input immutability, invalid arguments, empty input and idempotence.
No model/API eval has been run for v2. `version_log.csv` marks v2 as not_run.
The v1 prompt/tool snapshots are in `artifacts/versions/v1/`.

This v2 bundles prompt fixes and a new declaration; any accuracy change measures
the combined release, not the causal effect of one edit. To isolate the new
declaration's effect, also evaluate the saved v1 prompt with v2 tools.

## Live commands (from starter_v0)

```powershell
..\venv\Scripts\python.exe run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v2 --suite base --eval-cases data/eval_base.json
..\venv\Scripts\python.exe run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v2 --suite group --eval-cases data/eval_group.json
```

After a valid run, record its actual metrics, hashes, and run path. Inspect both
raw tool calls and execution errors; routing PASS does not imply API success.
Do not claim v2 improved until live evidence exists.
