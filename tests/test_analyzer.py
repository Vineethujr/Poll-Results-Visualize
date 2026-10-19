"""
test_analyzer.py - Unit Tests for Analytical Calculations & Metrics
"""

import pytest
import pandas as pd
import numpy as np
from src.analyzer import (
    calculate_single_choice_share,
    calculate_multi_select_share,
    calculate_numerical_summary,
    calculate_demographic_crosstab
)

@pytest.fixture
def sample_survey_df():
    return pd.DataFrame({
        "Respondent_ID": ["R1", "R2", "R3", "R4", "R5"],
        "Region": ["North", "North", "South", "South", "East"],
        "Primary_Platform": ["Alpha", "Beta", "Alpha", "Alpha", "Beta"],
        "Satisfaction_Score": [8, 6, 9, 7, np.nan],
        "Key_Features": [
            "Speed; Security",
            "Speed",
            "Security; UI",
            "Speed; UI; Security",
            "UI"
        ]
    })

def test_calculate_single_choice_share(sample_survey_df):
    share_df = calculate_single_choice_share(sample_survey_df, "Primary_Platform")
    
    assert len(share_df) == 2
    assert "Option" in share_df.columns
    assert "Share (%)" in share_df.columns
    
    alpha_row = share_df[share_df["Option"] == "Alpha"].iloc[0]
    beta_row = share_df[share_df["Option"] == "Beta"].iloc[0]
    
    assert alpha_row["Votes"] == 3
    assert alpha_row["Share (%)"] == 60.0
    assert beta_row["Votes"] == 2
    assert beta_row["Share (%)"] == 40.0
    assert round(share_df["Share (%)"].sum(), 1) == 100.0

def test_calculate_multi_select_share(sample_survey_df):
    multi_df = calculate_multi_select_share(sample_survey_df, "Key_Features", delimiter=";")
    
    # Total respondents = 5
    # Speed appears in R1, R2, R4 (3 times) -> 3 / 5 = 60.0%
    # Security appears in R1, R3, R4 (3 times) -> 3 / 5 = 60.0%
    # UI appears in R3, R4, R5 (3 times) -> 3 / 5 = 60.0%
    assert len(multi_df) == 3
    for _, row in multi_df.iterrows():
        assert row["Mentions"] == 3
        assert row["% of Respondents"] == 60.0
        assert round(row["% of Total Selections"], 2) == round(3 / 9 * 100, 2)

def test_calculate_numerical_summary(sample_survey_df):
    summary = calculate_numerical_summary(sample_survey_df, "Satisfaction_Score")
    
    # Valid values: [8, 6, 9, 7] -> Mean = 7.5, Median = 7.5, Min = 6, Max = 9
    assert summary["Count"] == 4
    assert summary["Mean"] == 7.5
    assert summary["Median"] == 7.5
    assert summary["Min"] == 6.0
    assert summary["Max"] == 9.0

def test_calculate_demographic_crosstab(sample_survey_df):
    ct = calculate_demographic_crosstab(sample_survey_df, "Region", "Primary_Platform", normalize="index")
    
    # North: 1 Alpha, 1 Beta -> 50% each
    assert ct.loc["North", "Alpha"] == 50.0
    assert ct.loc["North", "Beta"] == 50.0
    # South: 2 Alpha, 0 Beta -> 100% Alpha
    assert ct.loc["South", "Alpha"] == 100.0
    assert ct.loc["South", "Beta"] == 0.0
