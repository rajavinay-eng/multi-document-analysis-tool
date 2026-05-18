# project3/test_pipeline.py
# Basic tests for Project 3 CI/CD pipeline

import pytest

# ── UTILITY TESTS ─────────────────────────────────────────
def normalize_score(score):
    return max(0.0, min(1.0, float(score)))

def validate_query(query):
    if not query or not query.strip():
        return False
    if len(query) > 1000:
        return False
    return True

def estimate_cost(tokens, model="gpt-3.5-turbo"):
    rates = {
        "gpt-3.5-turbo": 0.002 / 1000,
        "gpt-4":         0.03  / 1000
    }
    rate = rates.get(model, 0.002/1000)
    return round(tokens * rate, 6)

def route_model(query_type):
    if query_type in ["compare", "analyze_complex"]:
        return "gpt-4"
    return "gpt-3.5-turbo"

# ── TEST CASES ────────────────────────────────────────────
def test_normalize_score_normal():
    assert normalize_score(0.5) == 0.5

def test_normalize_score_clamp_high():
    assert normalize_score(2.0) == 1.0

def test_normalize_score_clamp_low():
    assert normalize_score(-1.0) == 0.0

def test_validate_query_valid():
    assert validate_query("kidney dosage") == True

def test_validate_query_empty():
    assert validate_query("") == False

def test_validate_query_whitespace():
    assert validate_query("   ") == False

def test_validate_query_too_long():
    assert validate_query("x" * 1001) == False

def test_cost_estimation_gpt35():
    cost = estimate_cost(1000, "gpt-3.5-turbo")
    assert cost > 0
    assert cost < 1.0

def test_model_routing_compare():
    assert route_model("compare") == "gpt-4"

def test_model_routing_simple():
    assert route_model("summarize") == "gpt-3.5-turbo"

def test_model_routing_default():
    assert route_model("anything") == "gpt-3.5-turbo"

# Day 46 — CI/CD Quiz Answers

# What does CI stand for and what does it do?

#CI stands for Continuous Integration.
#It automatically runs tests whenever new code is pushed to the repository.

# What does CD stand for and what does it do?

#CD stands for Continuous Deployment.
#If tests pass, the updated application deploys automatically to production.

# How does pytest find test functions automatically?

#pytest automatically discovers files and functions starting with test_.

# What happens in your pipeline if a test fails?

#The deployment stops automatically and broken code never reaches production.

# What are GitHub Secrets and why use them?

#GitHub Secrets securely store sensitive values like API keys, EC2 IPs, and SSH private keys.

# Why keep main branch always deployable?

#The main branch should always contain stable working code safe for production deployment.

# What triggers your GitHub Actions workflow?

#A push or pull request to the main branch triggers the workflow automatically.

# What command runs all tests locally?

#pytest -v