"""
test_cleaner.py - Unit Tests for Data Cleaning & Audit Trail
"""

import pytest
import pandas as pd
import numpy as np
from src.cleaner import clean_survey_data

def test_clean_survey_data_deduplication():
    df_with_dups = pd.DataFrame({
        "Respondent_ID": ["R1", "R2", "R2"],
        "Region": ["North", "South", "South"],
        "Platform": ["Alpha", "Beta", "Beta"]
    })
    
    clean_df, audit = clean_survey_data(df_with_dups, drop_duplicates=True)
    
    assert len(clean_df) == 2
    dedup_step = [s for s in audit if s["step"] == "Deduplication"][0]
    assert dedup_step["affected_rows"] == 1

def test_clean_survey_data_whitespace_and_casing():
    df_messy = pd.DataFrame({
        "Respondent_ID": ["R1", "R2", "R3"],
        "Region": ["north", "North ", "South"],
        "Platform": ["Alpha  ", " Beta", "Alpha"]
    })
    
    clean_df, audit = clean_survey_data(df_messy, strip_whitespace=True, standardize_casing=True)
    
    # Whitespace removed
    assert clean_df["Platform"].tolist() == ["Alpha", "Beta", "Alpha"]
    # Casing standardized to Title
    assert clean_df["Region"].tolist() == ["North", "North", "South"]

def test_clean_survey_data_empty():
    empty_df = pd.DataFrame()
    clean_df, audit = clean_survey_data(empty_df)
    assert clean_df.empty
    assert audit[0]["status"] == "Error"
