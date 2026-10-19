"""
validator.py - Survey Dataset Validation Module
Performs structural, schema, and type validation on uploaded or loaded survey datasets.
"""

from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np

def validate_dataset(df: pd.DataFrame, min_rows: int = 10, min_cols: int = 2) -> Dict[str, Any]:
    """
    Validates a survey dataset structure and inspects column properties.
    
    Parameters:
        df (pd.DataFrame): Input dataframe.
        min_rows (int): Minimum acceptable row threshold.
        min_cols (int): Minimum acceptable column threshold.
        
    Returns:
        dict: Validation report containing:
            - is_valid (bool)
            - errors (List[str])
            - warnings (List[str])
            - metrics (dict): row_count, col_count, missing_cells, duplicate_rows
            - column_types (dict): Mapping of column names to inferred types
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    if df is None or not isinstance(df, pd.DataFrame):
        return {
            "is_valid": False,
            "errors": ["Input dataset is null or invalid format."],
            "warnings": [],
            "metrics": {},
            "column_types": {}
        }
        
    row_count, col_count = df.shape
    
    if row_count == 0:
        errors.append("Dataset is completely empty (0 rows).")
        return {
            "is_valid": False,
            "errors": errors,
            "warnings": warnings,
            "metrics": {"row_count": 0, "col_count": col_count},
            "column_types": {}
        }
        
    if row_count < min_rows:
        warnings.append(f"Small sample size warning: Dataset contains only {row_count} rows (minimum recommended is {min_rows}).")
        
    if col_count < min_cols:
        errors.append(f"Insufficient columns: Dataset contains {col_count} columns (requires at least {min_cols}).")
        
    # Check for empty headers
    unnamed_cols = [c for c in df.columns if "Unnamed:" in str(c) or str(c).strip() == ""]
    if unnamed_cols:
        warnings.append(f"Detected {len(unnamed_cols)} columns with missing or default header names.")
        
    # Check for duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        warnings.append(f"Found {dup_count} duplicate rows in dataset.")
        
    # Check overall missingness
    total_cells = df.size
    missing_cells = df.isna().sum().sum()
    missing_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0
    if missing_pct > 20:
        warnings.append(f"High missingness: {missing_pct:.1f}% of total data cells are empty/NaN.")
        
    # Infer column categories
    column_types: Dict[str, str] = {}
    for col in df.columns:
        series = df[col].dropna()
        if len(series) == 0:
            column_types[col] = "Empty"
            continue
            
        # Try datetime
        if "date" in str(col).lower() or "time" in str(col).lower():
            try:
                pd.to_datetime(series.iloc[:20])
                column_types[col] = "Datetime"
                continue
            except Exception:
                pass
                
        # Numeric check
        if pd.api.types.is_numeric_dtype(series):
            unique_vals = series.nunique()
            if unique_vals <= 10 and series.dtype in [np.int64, np.int32, int]:
                column_types[col] = "Numerical (Rating/Likert)"
            else:
                column_types[col] = "Numerical (Continuous)"
        else:
            # Check for multi-select delimiter like ';' or ','
            sample_str = series.astype(str).head(50)
            has_semicolon = sample_str.str.contains(";").sum() > (len(sample_str) * 0.2)
            if has_semicolon:
                column_types[col] = "Categorical (Multi-select)"
            else:
                if series.nunique() <= 20:
                    column_types[col] = "Categorical (Single-choice)"
                else:
                    column_types[col] = "Text / Identifier"
                    
    is_valid = len(errors) == 0
    
    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "row_count": row_count,
            "col_count": col_count,
            "duplicate_rows": int(dup_count),
            "missing_cells": int(missing_cells),
            "missing_pct": round(missing_pct, 2)
        },
        "column_types": column_types
    }
