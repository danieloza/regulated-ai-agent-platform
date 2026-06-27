import json
from pathlib import Path

import pytest

from app.main import PROMPT_ATTACKS, classify_policy


EVAL_PATH = Path(__file__).resolve().parents[1] / "evals" / "security_cases.json"


@pytest.mark.parametrize("case", json.loads(EVAL_PATH.read_text()))
def test_security_policy_eval_cases(case):
    decision = classify_policy(case["input"])
    assert decision["decision"] == case["expected_decision"], case["id"]


@pytest.mark.parametrize("attack", PROMPT_ATTACKS)
def test_prompt_attack_catalog_has_expected_outcomes(attack):
    decision = classify_policy(attack["prompt"])
    assert decision["decision"] == attack["expected_decision"], attack["id"]
