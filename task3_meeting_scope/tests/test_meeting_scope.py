import time

import pytest

from app.agents.estimator import estimate
from app.agents.requirements_extractor import extract_requirements
from app.scope_engine.diff_engine import compare_scope


@pytest.mark.parametrize(
    "transcript,expected",
    [
        ("We need a member search page.", 1),
        ("Please add event registration.", 1),
        ("We would like a new home page.", 1),
        ("The team wants automated onboarding.", 1),
        ("We need to integrate our CRM.", 1),
        ("Please create a reporting dashboard.", 1),
        ("The business requires member approvals.", 1),
        ("We want to add a payment method.", 1),
        ("Could you build a booking calendar?", 1),
        ("The site needs user notifications.", 1),
        ("We must improve account security.", 1),
        ("We need to migrate existing records.", 1),
        ("Please automate the renewal process.", 1),
        ("We would like custom data exports.", 1),
        ("We need a private member area.", 1),
        ("Please add role-based access.", 1),
        ("We want to integrate a payment gateway.", 1),
        ("The client requires a custom search filter.", 1),
        ("Please build a referral feature.", 1),
        ("We should create a new listing category.", 1),
    ],
)
def test_extracts_explicit_requested_features(transcript, expected):
    result = extract_requirements(transcript)
    assert len(result["requirements"]) == expected


def test_extracts_pain_points_without_duplicates():
    result = extract_requirements("The process is slow and difficult.\nThe process is slow and difficult.")
    assert len(result["pain_points"]) == 1


def test_builtin_estimate_is_low_effort_and_no_custom_build():
    result = estimate("Change the label in site settings", "built_in")
    assert result["estimated_hours"] == 1
    assert result["complexity"] == "low"


def test_custom_integration_estimate_is_higher_complexity():
    result = estimate("We need to integrate our API and migrate all records.", "needs_review")
    assert result["complexity"] == "high"
    assert result["estimated_hours"] >= 28


def test_scope_delta_identifies_new_modified_removed_and_cost_changes():
    old = [
        {"title": "Build search", "estimated_hours": 10, "cost": 1250},
        {"title": "Create reports", "estimated_hours": 8, "cost": 1000},
    ]
    new = [
        {"title": "Build search", "estimated_hours": 14, "cost": 1750},
        {"title": "Add payments", "estimated_hours": 20, "cost": 2500},
    ]
    result = compare_scope(old, new)
    assert len(result["new_tasks"]) == 1
    assert len(result["modified_tasks"]) == 1
    assert len(result["removed_tasks"]) == 1
    assert len(result["out_of_scope_items"]) == 1


def test_evaluation_summary():
    started = time.perf_counter()
    cases = 25
    passed = sum(
        len(extract_requirements(f"We need evaluation feature {index}." )["requirements"]) == 1
        for index in range(cases)
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    print(f"\n| Task | Cases | Quality | Latency (ms) | Estimated API cost |\n|---|---:|---:|---:|---:|\n| Meeting Scope | {cases} | {passed / cases:.0%} | {elapsed_ms:.2f} | $0.00 (local estimator) |")
    assert passed == cases
