"""
data_generator.py - Synthetic Poll and Survey Data Generator
Generates realistic poll response data with demographic distributions,
multi-select options, numerical ratings, and subtle anomalies for cleaning tests.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_synthetic_poll(n_responses: int = 1200, seed: int = 42, inject_noise: bool = True) -> pd.DataFrame:
    """
    Generates a realistic survey dataset for consumer tech platform preferences.
    
    Parameters:
        n_responses (int): Number of survey respondents to generate.
        seed (int): Random seed for reproducibility.
        inject_noise (bool): Whether to inject real-world survey messiness (spaces, casing, missing, duplicates).
        
    Returns:
        pd.DataFrame: Synthetic survey dataframe.
    """
    np.random.seed(seed)
    
    # 1. Demographics definition
    regions = ["North", "South", "East", "West", "Central"]
    region_weights = [0.28, 0.24, 0.18, 0.20, 0.10]
    
    age_groups = ["18-25", "26-35", "36-50", "51-65", "65+"]
    age_weights = [0.22, 0.35, 0.23, 0.14, 0.06]
    
    genders = ["Female", "Male", "Non-Binary", "Prefer not to say"]
    gender_weights = [0.49, 0.46, 0.03, 0.02]
    
    education_levels = ["High School", "Bachelor's", "Master's", "Doctorate"]
    edu_weights = [0.25, 0.50, 0.20, 0.05]
    
    # Generate demographic arrays
    selected_regions = np.random.choice(regions, size=n_responses, p=region_weights)
    selected_ages = np.random.choice(age_groups, size=n_responses, p=age_weights)
    selected_genders = np.random.choice(genders, size=n_responses, p=gender_weights)
    selected_edu = np.random.choice(education_levels, size=n_responses, p=edu_weights)
    
    # 2. Date generation (Jan 15, 2026 to Oct 15, 2026)
    start_date = datetime(2026, 1, 15)
    random_days = np.random.randint(0, 270, size=n_responses)
    dates = [start_date + timedelta(days=int(d)) for d in random_days]
    dates_sorted = sorted(dates) # roughly chronological
    
    # 3. Target Variable: Primary Preferred Platform with Regional Bias
    # Platform Alpha: Strong in North & West
    # Platform Beta: Dominant in South
    # Platform Gamma: Preferred in East
    # Platform Delta: Emerging contender in Central
    platforms = ["Platform Alpha", "Platform Beta", "Platform Gamma", "Platform Delta"]
    selected_platforms = []
    
    for r in selected_regions:
        if r == "North":
            p = [0.45, 0.22, 0.20, 0.13]
        elif r == "South":
            p = [0.18, 0.52, 0.18, 0.12]
        elif r == "East":
            p = [0.20, 0.22, 0.46, 0.12]
        elif r == "West":
            p = [0.48, 0.20, 0.18, 0.14]
        else: # Central
            p = [0.28, 0.25, 0.17, 0.30]
        selected_platforms.append(np.random.choice(platforms, p=p))
        
    # 4. Numerical Rating: Satisfaction Score (1-10) influenced by platform
    satisfaction_scores = []
    for plat in selected_platforms:
        if plat == "Platform Alpha":
            score = np.random.normal(loc=8.2, scale=1.2)
        elif plat == "Platform Beta":
            score = np.random.normal(loc=7.8, scale=1.4)
        elif plat == "Platform Gamma":
            score = np.random.normal(loc=7.1, scale=1.6)
        else:
            score = np.random.normal(loc=6.9, scale=1.8)
        # Clip to valid 1-10 integer
        clamped = int(np.clip(round(score), 1, 10))
        satisfaction_scores.append(clamped)
        
    # 5. Multiple-Selection Question: Key Features Value Most (Delimited with '; ')
    all_features = [
        "Ease of Use",
        "Data Privacy & Security",
        "Speed & Performance",
        "Customer Support",
        "Affordable Pricing",
        "Cross-Device Sync"
    ]
    feature_selections = []
    for _ in range(n_responses):
        k = np.random.choice([1, 2, 3, 4], p=[0.15, 0.45, 0.30, 0.10])
        chosen = list(np.random.choice(all_features, size=k, replace=False))
        feature_selections.append("; ".join(chosen))
        
    # 6. Recommendation Likelihood: Yes, No, Maybe based on satisfaction
    recommendations = []
    for score in satisfaction_scores:
        if score >= 8:
            rec = np.random.choice(["Yes", "Maybe", "No"], p=[0.82, 0.15, 0.03])
        elif score >= 6:
            rec = np.random.choice(["Yes", "Maybe", "No"], p=[0.40, 0.45, 0.15])
        else:
            rec = np.random.choice(["Yes", "Maybe", "No"], p=[0.10, 0.35, 0.55])
        recommendations.append(rec)
        
    # 7. Respondent IDs
    respondent_ids = [f"RESP_{1000 + i}" for i in range(n_responses)]
    
    df = pd.DataFrame({
        "Respondent_ID": respondent_ids,
        "Timestamp": [d.strftime("%Y-%m-%d") for d in dates_sorted],
        "Region": selected_regions,
        "Age_Group": selected_ages,
        "Gender": selected_genders,
        "Education": selected_edu,
        "Primary_Platform": selected_platforms,
        "Satisfaction_Score": satisfaction_scores,
        "Key_Features": feature_selections,
        "Would_Recommend": recommendations
    })
    
    # 8. Inject Real-World Survey Messiness if requested
    if inject_noise:
        # Trailing spaces in some platform names
        space_idx = np.random.choice(df.index, size=int(n_responses * 0.03), replace=False)
        df.loc[space_idx, "Primary_Platform"] = df.loc[space_idx, "Primary_Platform"] + "  "
        
        # Lowercase inconsistency in a few regions
        case_idx = np.random.choice(df.index, size=int(n_responses * 0.02), replace=False)
        df.loc[case_idx, "Region"] = df.loc[case_idx, "Region"].str.lower()
        
        # A few missing values in Satisfaction_Score and Would_Recommend
        nan_score_idx = np.random.choice(df.index, size=int(n_responses * 0.015), replace=False)
        df.loc[nan_score_idx, "Satisfaction_Score"] = np.nan
        
        nan_rec_idx = np.random.choice(df.index, size=int(n_responses * 0.01), replace=False)
        df.loc[nan_rec_idx, "Would_Recommend"] = np.nan
        
        # Add 3 duplicate rows to test duplicate detection
        duplicates = df.iloc[:3].copy()
        df = pd.concat([df, duplicates], ignore_index=True)
        
    return df

if __name__ == "__main__":
    df = generate_synthetic_poll()
    df.to_csv("data/poll_survey_data.csv", index=False)
    print(f"Generated synthetic survey dataset: {df.shape[0]} rows, {df.shape[1]} columns.")
