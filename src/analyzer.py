"""
analyzer.py - Core Survey Analytics & Descriptive Statistics Module
Computes option-wise vote shares, explicit percentage distributions,
demographic cross-tabulations, multi-select parsing, and time trends.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

def calculate_single_choice_share(df: pd.DataFrame, question_col: str) -> pd.DataFrame:
    """
    Calculates response counts, percentage shares, and cumulative percentages for a single-choice question.
    
    Parameters:
        df (pd.DataFrame): Input dataframe.
        question_col (str): Column name containing categorical answers.
        
    Returns:
        pd.DataFrame: Table with columns [Option, Votes, Share (%), Cumulative (%)]
    """
    if question_col not in df.columns:
        raise ValueError(f"Column '{question_col}' not found in DataFrame.")
        
    series = df[question_col].dropna()
    total_valid = len(series)
    
    if total_valid == 0:
        return pd.DataFrame(columns=["Option", "Votes", "Share (%)", "Cumulative (%)"])
        
    counts = series.value_counts()
    share_pct = (counts / total_valid * 100).round(2)
    cum_pct = share_pct.cumsum().round(2)
    
    result = pd.DataFrame({
        "Option": counts.index,
        "Votes": counts.values,
        "Share (%)": share_pct.values,
        "Cumulative (%)": cum_pct.values
    })
    
    return result

def calculate_multi_select_share(df: pd.DataFrame, question_col: str, delimiter: str = ";") -> pd.DataFrame:
    """
    Parses delimiter-separated multiple-choice questions and calculates:
    1. Respondent Share (% of all respondents who selected the option)
    2. Mention Share (% of total selections made across all respondents)
    """
    if question_col not in df.columns:
        raise ValueError(f"Column '{question_col}' not found in DataFrame.")
        
    series = df[question_col].dropna().astype(str)
    total_respondents = len(series)
    
    if total_respondents == 0:
        return pd.DataFrame(columns=["Option", "Mentions", "% of Respondents", "% of Total Selections"])
        
    # Split each response and flatten
    all_mentions = []
    for resp in series:
        items = [item.strip() for item in resp.split(delimiter) if item.strip()]
        all_mentions.extend(items)
        
    mention_series = pd.Series(all_mentions)
    counts = mention_series.value_counts()
    total_mentions = len(mention_series)
    
    resp_share = (counts / total_respondents * 100).round(2)
    mention_share = (counts / total_mentions * 100).round(2)
    
    result = pd.DataFrame({
        "Option": counts.index,
        "Mentions": counts.values,
        "% of Respondents": resp_share.values,
        "% of Total Selections": mention_share.values
    })
    
    return result

def calculate_numerical_summary(df: pd.DataFrame, num_col: str) -> Dict[str, float]:
    """
    Calculates comprehensive descriptive statistics for numerical / rating questions.
    """
    if num_col not in df.columns:
        raise ValueError(f"Column '{num_col}' not found in DataFrame.")
        
    series = pd.to_numeric(df[num_col], errors="coerce").dropna()
    
    if len(series) == 0:
        return {}
        
    q25 = float(series.quantile(0.25))
    q75 = float(series.quantile(0.75))
    
    return {
        "Count": int(len(series)),
        "Mean": round(float(series.mean()), 2),
        "Std Dev": round(float(series.std()), 2),
        "Median": round(float(series.median()), 2),
        "Min": round(float(series.min()), 2),
        "Max": round(float(series.max()), 2),
        "25th Percentile": round(q25, 2),
        "75th Percentile": round(q75, 2),
        "IQR": round(q75 - q25, 2)
    }

def calculate_demographic_crosstab(
    df: pd.DataFrame,
    demographic_col: str,
    question_col: str,
    normalize: str = "index"  # 'index', 'columns', or None (counts)
) -> pd.DataFrame:
    """
    Computes a cross-tabulation of poll responses grouped by demographic categories.
    
    Parameters:
        df (pd.DataFrame): Cleaned survey dataset.
        demographic_col (str): Grouping field (e.g., 'Region', 'Age_Group').
        question_col (str): Target poll question (e.g., 'Primary_Platform').
        normalize (str): Normalization axis ('index' produces row percentage shares).
        
    Returns:
        pd.DataFrame: Cross-tabulation table.
    """
    if demographic_col not in df.columns or question_col not in df.columns:
        raise ValueError("Specified columns not found in DataFrame.")
        
    clean_sub = df[[demographic_col, question_col]].dropna()
    
    if normalize == "index":
        ct = pd.crosstab(clean_sub[demographic_col], clean_sub[question_col], normalize="index") * 100
        return ct.round(2)
    elif normalize == "all":
        ct = pd.crosstab(clean_sub[demographic_col], clean_sub[question_col], normalize="all") * 100
        return ct.round(2)
    else:
        return pd.crosstab(clean_sub[demographic_col], clean_sub[question_col])

def calculate_time_trend(df: pd.DataFrame, date_col: str, question_col: str, freq: str = "M") -> pd.DataFrame:
    """
    Aggregates poll responses over time periods (Monthly, Weekly) to track dynamic share changes.
    """
    if date_col not in df.columns or question_col not in df.columns:
        raise ValueError("Specified columns not found in DataFrame.")
        
    temp = df[[date_col, question_col]].dropna().copy()
    temp["Period"] = pd.to_datetime(temp[date_col]).dt.to_period(freq).astype(str)
    
    trend = pd.crosstab(temp["Period"], temp[question_col], normalize="index") * 100
    return trend.round(2)
