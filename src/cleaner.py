"""
cleaner.py - Transparent Survey Data Cleaning Module
Performs non-destructive cleaning, whitespace removal, standardization,
deduplication, and produces an audit log of every operation.
"""

from typing import Tuple, List, Dict, Any
import pandas as pd
import numpy as np

def clean_survey_data(
    raw_df: pd.DataFrame,
    drop_duplicates: bool = True,
    strip_whitespace: bool = True,
    standardize_casing: bool = True,
    handle_missing_categorical: str = "keep_as_missing"  # options: 'keep_as_missing', 'fill_unknown', 'drop_row'
) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Cleans raw survey data non-destructively and compiles an audit trail.
    
    Parameters:
        raw_df (pd.DataFrame): Immutable original dataset.
        drop_duplicates (bool): Whether to remove duplicate rows.
        strip_whitespace (bool): Whether to trim leading/trailing spaces from strings.
        standardize_casing (bool): Whether to standardize mixed casing in categorical columns.
        handle_missing_categorical (str): Strategy for missing categorical values.
        
    Returns:
        Tuple[pd.DataFrame, List[Dict[str, Any]]]: Cleaned DataFrame and audit log entries.
    """
    if raw_df is None or raw_df.empty:
        return raw_df, [{"operation": "Validation", "status": "Error", "details": "DataFrame is empty."}]
        
    df = raw_df.copy()
    audit_log: List[Dict[str, Any]] = []
    initial_rows = len(df)
    
    # 1. Deduplication
    if drop_duplicates:
        dups_count = int(df.duplicated().sum())
        if dups_count > 0:
            df = df.drop_duplicates().reset_index(drop=True)
            audit_log.append({
                "step": "Deduplication",
                "action": "Removed identical duplicate rows",
                "affected_rows": dups_count,
                "resulting_rows": len(df)
            })
        else:
            audit_log.append({
                "step": "Deduplication",
                "action": "Verified uniqueness - no duplicates found",
                "affected_rows": 0,
                "resulting_rows": len(df)
            })
            
    # 2. Whitespace trimming
    if strip_whitespace:
        trimmed_cols = 0
        for col in df.select_dtypes(include=["object", "string", str]).columns:
            # Check if any values have leading/trailing whitespace
            s = df[col].astype(str)
            has_ws = s.str.startswith(" ") | s.str.endswith(" ")
            if has_ws.any():
                df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
                trimmed_cols += 1
                
        audit_log.append({
            "step": "Whitespace Stripping",
            "action": f"Trimmed leading/trailing spaces across text fields",
            "affected_columns": trimmed_cols,
            "resulting_rows": len(df)
        })
        
    # 3. Standardization of Casing
    if standardize_casing:
        casing_cols = []
        for col in df.select_dtypes(include=["object", "string", str]).columns:
            # Skip ID columns and multi-select semicolon columns
            if "id" in col.lower() or df[col].astype(str).str.contains(";").any():
                continue
            # If unique values have mixed casing (e.g. 'north' and 'North')
            uniques = df[col].dropna().unique()
            lower_uniques = [str(u).lower() for u in uniques]
            if len(set(lower_uniques)) < len(uniques):
                # Normalize to Title Case
                df[col] = df[col].apply(lambda x: x.title() if isinstance(x, str) else x)
                casing_cols.append(col)
                
        audit_log.append({
            "step": "Casing Standardization",
            "action": f"Normalized mixed casing to Title Case: {', '.join(casing_cols) if casing_cols else 'None needed'}",
            "affected_columns": len(casing_cols),
            "resulting_rows": len(df)
        })
        
    # 4. Missing Value Strategy
    missing_before = int(df.isna().sum().sum())
    if handle_missing_categorical == "fill_unknown":
        filled_count = 0
        for col in df.select_dtypes(include=["object"]).columns:
            n_nan = df[col].isna().sum()
            if n_nan > 0:
                df[col] = df[col].fillna("Unknown")
                filled_count += n_nan
        audit_log.append({
            "step": "Missing Values",
            "action": f"Filled missing categorical cells with 'Unknown'",
            "affected_cells": int(filled_count),
            "resulting_rows": len(df)
        })
    elif handle_missing_categorical == "drop_row":
        df = df.dropna().reset_index(drop=True)
        dropped_rows = initial_rows - len(df)
        audit_log.append({
            "step": "Missing Values",
            "action": f"Dropped rows with any missing values",
            "affected_rows": int(dropped_rows),
            "resulting_rows": len(df)
        })
    else:
        audit_log.append({
            "step": "Missing Values",
            "action": f"Preserved missing values explicitly as NaN ({missing_before} cells)",
            "affected_cells": missing_before,
            "resulting_rows": len(df)
        })
        
    return df, audit_log
