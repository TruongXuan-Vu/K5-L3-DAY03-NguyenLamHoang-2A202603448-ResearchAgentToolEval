# V3 — resolve the active request after source changes

## Baseline evidence

User-run v2: `runs/v2_B_base_openrouter_20261110T114454962931.json`.
19/20 cases passed; case/routing/argument accuracy 95%; multi-turn 5/6;
provider errors 0. The only failed case was M06_switch_tool.

The user canceled Twitter, switched to web news, then retained the OpenAI topic.
V2 called lookup correctly but also called social_search. The grader recorded
`extra_tool_call`. The earlier social source should have remained canceled.

## Single hypothesis and change

V2's instruction to call all needed tools did not explicitly separate active
requests from historical or canceled ones. V3 resolves conversation updates in
order before selecting tools: replacements/cancellations remove sources, while
unchanged subject/count/time constraints remain. A later topic-only message
must not reactivate an excluded source.

Only `artifacts/system_prompt.md` changes behavior. Tools, agent code, base and
group evaluation datasets are unchanged. Exact pre-edit v2 prompt/tool files
are saved in `artifacts/versions/v2/` for comparison.

## Acceptance criteria

- M06: lookup only, query OpenAI, topic news; no social_search.
- R13: keep both lookup and social_search when both sources remain requested.
- Preserve the other 18 v2 passing cases, including confirmation and missing-input handling.
- Treat 20/20 as a target, not an observed result. Repeat the run to assess stability.
- Inspect tool execution errors separately from routing/arguments.

## Verification status

Existing offline suite: **84 passed, 17 skipped**. All skipped tests are existing
starter TODOs. No new test files or dataset cases were added for v3.
This verifies existing code contracts; it does not prove model routing improved.

The live v3 evaluation was rejected by automatic approval review before process
execution: explicit approval is needed to send this prompt, tool declarations
and eval queries to OpenRouter. No v3 live score or run JSON exists from that
attempt. Version log records v3 as not measured; it now includes the real v2 score.

## Run from starter_v0

```powershell
..\venv\Scripts\python.exe run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v3 --suite base --eval-cases data/eval_base.json
..\venv\Scripts\python.exe run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v3 --suite group --eval-cases data/eval_group.json
```

After a valid run, update the v3 metrics and run path in version_log.csv using
actual evidence, and compare M06 plus R13 with v2. Do not overwrite base cases
or infer a measured score from the offline test result.
