"""
insights.py - Automated Narrative Insights Generation Engine
Derives factual, rule-based summary insights from calculated survey metrics.
Avoids unsupported causal claims and focuses on clear statistical observations.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

def generate_poll_insights(
    share_df: pd.DataFrame,
    crosstab_df: Optional[pd.DataFrame] = None,
    num_summary: Optional[Dict[str, float]] = None,
    total_respondents: int = 0
) -> List[str]:
    """
    Synthesizes natural-language analytical takeaways based strictly on calculated metrics.
    
    Parameters:
        share_df (pd.DataFrame): Table with ['Option', 'Votes', 'Share (%)']
        crosstab_df (pd.DataFrame, optional): Cross-tabulation table across demographics.
        num_summary (dict, optional): Descriptive statistics dictionary.
        total_respondents (int): Total count of respondents.
        
    Returns:
        List[str]: Bulleted narrative insights.
    """
    insights: List[str] = []
    
    if share_df.empty:
        return ["Insufficient data to derive analytical insights."]
        
    df_sorted = share_df.sort_values(by="Share (%)", ascending=False).reset_index(drop=True)
    
    # 1. Participation Volume
    valid_votes = int(df_sorted["Votes"].sum())
    insights.append(
        f"**Sample Engagement**: A total of **{valid_votes:,} valid responses** were analyzed "
        f"(representing {round(valid_votes / total_respondents * 100, 1) if total_respondents > 0 else 100}% participation)."
    )
    
    # 2. Leading Option & Margin Analysis
    leader = df_sorted.iloc[0]
    insights.append(
        f"**Plurality Leader**: **{leader['Option']}** emerged as the top choice, securing "
        f"**{leader['Share (%)']}%** of all valid selections ({int(leader['Votes']):,} votes)."
    )
    
    if len(df_sorted) > 1:
        runner_up = df_sorted.iloc[1]
        margin = round(leader["Share (%)"] - runner_up["Share (%)"], 2)
        if margin > 15:
            margin_desc = "a decisive commanding lead"
        elif margin > 5:
            margin_desc = "a moderate competitive advantage"
        else:
            margin_desc = "a tight, highly contested race"
            
        insights.append(
            f"**Competitive Margin**: The leader holds {margin_desc} of **{margin} percentage points** "
            f"over runner-up **{runner_up['Option']}** ({runner_up['Share (%)']}%)."
        )
        
    # 3. Trailing Option
    if len(df_sorted) > 2:
        trailing = df_sorted.iloc[-1]
        insights.append(
            f"**Lowest Preference**: **{trailing['Option']}** recorded the lowest overall adoption at "
            f"**{trailing['Share (%)']}%** ({int(trailing['Votes']):,} votes)."
        )
        
    # 4. Demographic / Regional Strongholds
    if crosstab_df is not None and not crosstab_df.empty:
        # For each option, find which demographic group had the highest preference
        strongholds = []
        for opt in crosstab_df.columns:
            top_group = crosstab_df[opt].idxmax()
            top_val = crosstab_df.loc[top_group, opt]
            strongholds.append(f"{opt} performed strongest in **{top_group}** ({top_val:.1f}%)")
            
        insights.append(
            f"**Demographic Variance**: Cross-segment analysis reveals distinct regional preferences: "
            f"{'; '.join(strongholds[:3])}."
        )
        
    # 5. Numerical Rating Sentiment
    if num_summary and "Mean" in num_summary:
        mean_val = num_summary["Mean"]
        median_val = num_summary["Median"]
        std_val = num_summary.get("Std Dev", 0)
        
        sentiment = "positive" if mean_val >= 7.5 else "moderate" if mean_val >= 5.5 else "negative"
        insights.append(
            f"**Sentiment & Satisfaction**: Overall average score is **{mean_val} / 10** "
            f"(Median: {median_val}, Std Dev: {std_val}), indicating a generally **{sentiment}** sentiment among participants."
        )
        
    return insights
