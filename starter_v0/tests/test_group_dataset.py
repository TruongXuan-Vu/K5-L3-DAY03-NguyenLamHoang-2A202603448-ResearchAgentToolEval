import json
from copy import deepcopy
from pathlib import Path

from run_eval import evaluate_phase_b, load_cases, validate_expected_tools
from tools import load_tool_declarations

ROOT = Path(__file__).resolve().parents[1]


def test_group_has_ten_unique_cases_five_single_and_five_multi():
    cases = load_cases(ROOT / "data/eval_group.json", "B")
    assert len(cases) == len({c["id"] for c in cases}) == 10
    assert sum("turns" in c for c in cases) == 5
    assert sum("query" in c for c in cases) == 5
    declarations = load_tool_declarations(ROOT / "artifacts/tools.yaml")
    validate_expected_tools(cases, declarations, ROOT / "data/eval_group.json")


def test_deduplicate_cases_can_be_scored_and_reject_wrong_mode():
    cases = json.loads((ROOT / "data/eval_group.json").read_text(encoding="utf-8"))["cases"]
    targeted = [c for c in cases if any(t["name"] == "deduplicate" for t in c["expect"].get("tool_calls", []))]
    assert len(targeted) == 2
    for case in targeted:
        calls = deepcopy(case["expect"]["tool_calls"])
        assert evaluate_phase_b(case, calls, None)["passed"]
        calls[0]["args"]["mode"] = "wrong-mode"
        assert not evaluate_phase_b(case, calls, None)["passed"]
