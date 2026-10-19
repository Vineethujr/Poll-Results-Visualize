"""
visualizer.py - Interactive & Static Data Visualization Factory
Creates publication-ready Plotly figures for the web dashboard,
and Matplotlib figures for static report embedding.
"""

from typing import Optional, List
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Consistent analytical color palette
COLOR_SEQUENCE = ["#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#06B6D4", "#EC4899"]

def create_bar_chart(share_df: pd.DataFrame, title: str = "Poll Response Share (%)") -> go.Figure:
    """
    Creates an interactive Plotly horizontal bar chart showing vote share and exact counts.
    """
    # Sort ascending for clean top-to-bottom horizontal display
    df_sorted = share_df.sort_values(by="Share (%)", ascending=True)
    
    fig = go.Figure(go.Bar(
        x=df_sorted["Share (%)"],
        y=df_sorted["Option"],
        orientation="h",
        text=df_sorted.apply(lambda r: f"{r['Share (%)']}% ({int(r['Votes'])} votes)", axis=1),
        textposition="auto",
        marker=dict(
            color=COLOR_SEQUENCE[:len(df_sorted)][::-1],
            line=dict(color="#1E293B", width=1)
        )
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, family="Arial, sans-serif")),
        xaxis=dict(title="Share of Valid Votes (%)", range=[0, max(df_sorted["Share (%)"]) * 1.18]),
        yaxis=dict(title=""),
        margin=dict(l=20, r=20, t=50, b=30),
        template="plotly_white",
        height=380
    )
    return fig

def create_pie_chart(share_df: pd.DataFrame, title: str = "Vote Distribution Breakdown") -> go.Figure:
    """
    Creates an interactive Plotly donut chart.
    """
    fig = go.Figure(go.Pie(
        labels=share_df["Option"],
        values=share_df["Votes"],
        hole=0.45,
        marker=dict(colors=COLOR_SEQUENCE),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Votes: %{value}<br>Share: %{percent}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        margin=dict(l=20, r=20, t=50, b=20),
        template="plotly_white",
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

def create_stacked_demographic_chart(crosstab_df: pd.DataFrame, title: str = "Regional / Demographic Breakdown (%)") -> go.Figure:
    """
    Creates a 100% stacked horizontal bar chart comparing option share across demographic groups.
    """
    fig = go.Figure()
    
    for i, col in enumerate(crosstab_df.columns):
        fig.add_trace(go.Bar(
            y=crosstab_df.index,
            x=crosstab_df[col],
            name=str(col),
            orientation="h",
            text=crosstab_df[col].apply(lambda v: f"{v:.1f}%" if v > 4 else ""),
            textposition="inside",
            marker=dict(color=COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)])
        ))
        
    fig.update_layout(
        barmode="stack",
        title=dict(text=title, font=dict(size=18)),
        xaxis=dict(title="Percentage Share (%)", range=[0, 100]),
        yaxis=dict(title="Demographic Group", autorange="reversed"),
        legend=dict(title="Options", orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=50),
        template="plotly_white",
        height=420
    )
    return fig

def create_trend_chart(trend_df: pd.DataFrame, title: str = "Response Share Trend Over Time") -> go.Figure:
    """
    Creates a multi-line time series chart showing changes in response shares over time periods.
    """
    fig = go.Figure()
    
    for i, col in enumerate(trend_df.columns):
        fig.add_trace(go.Scatter(
            x=trend_df.index,
            y=trend_df[col],
            mode="lines+markers",
            name=str(col),
            line=dict(width=3, color=COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)]),
            marker=dict(size=7)
        ))
        
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis=dict(title="Period"),
        yaxis=dict(title="Share (%)", range=[0, max(trend_df.max()) * 1.2]),
        margin=dict(l=20, r=20, t=50, b=30),
        template="plotly_white",
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
    )
    return fig

def create_numerical_distribution(df: pd.DataFrame, num_col: str, title: str = "Rating Score Distribution") -> go.Figure:
    """
    Creates a combination histogram and boxplot for a numerical rating column.
    """
    clean_series = pd.to_numeric(df[num_col], errors="coerce").dropna()
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=clean_series,
        nbinsx=10,
        marker=dict(color="#3B82F6", line=dict(color="#1E3A8A", width=1)),
        name="Frequency"
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis=dict(title=num_col, dtick=1),
        yaxis=dict(title="Number of Respondents"),
        margin=dict(l=20, r=20, t=50, b=30),
        template="plotly_white",
        height=380
    )
    return fig

# --- Static Matplotlib Export Helper for PDF & Image Saving ---
def save_static_summary_plot(share_df: pd.DataFrame, save_path: str, title: str = "Poll Results Overview"):
    """
    Generates and saves a high-resolution static PNG chart using Matplotlib for PDF report inclusion.
    """
    plt.figure(figsize=(8, 4.5), dpi=300)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    
    df_sorted = share_df.sort_values(by="Share (%)", ascending=True)
    bars = plt.barh(df_sorted["Option"], df_sorted["Share (%)"], color="#2563EB", edgecolor="#1E40AF")
    
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 1.0, bar.get_y() + bar.get_height() / 2, f"{width:.1f}%",
                 va="center", ha="left", fontsize=10, fontweight="bold", color="#1E293B")
                 
    plt.title(title, fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Share of Total Votes (%)", fontsize=11)
    plt.xlim(0, max(df_sorted["Share (%)"]) * 1.25)
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
