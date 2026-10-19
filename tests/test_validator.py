"""
test_validator.py - Unit Tests for Schema & Integrity Validation
"""

import pytest
import pandas as pd
from src.validator import validate_dataset

def test_validate_valid_dataset():
    df = pd.DataFrame({
        "Respondent_ID": [f"R{i}" for i in range(20)],
        "Satisfaction": [7] * 20,
        "Platform": ["Alpha"] * 20
    })
    report = validate_dataset(df)
    assert report["is_valid"] is True
    assert len(report["errors"]) == 0
    assert report["metrics"]["row_count"] == 20

def test_validate_empty_dataset():
    report = validate_dataset(pd.DataFrame())
    assert report["is_valid"] is False
    assert "Dataset is completely empty" in report["errors"][0]

def test_validate_none_dataset():
    report = validate_dataset(None)
    assert report["is_valid"] is False
    assert "null or invalid" in report["errors"][0]

def test_validate_type_inference():
    df = pd.DataFrame({
        "Respondent_ID": ["R1", "R2", "R3"],
        "Rating": [1, 5, 10],
        "Platform": ["Alpha", "Beta", "Gamma"],
        "Features": ["Speed; UI", "Security", "Cost; Speed"]
    })
    report = validate_dataset(df, min_rows=1)
    assert "Numerical" in report["column_types"]["Rating"]
    assert "Categorical (Multi-select)" in report["column_types"]["Features"]
