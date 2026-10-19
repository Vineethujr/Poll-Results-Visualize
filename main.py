"""
main.py - Poll Results Visualizer Application Entrypoint
Supports dual execution modes:
1. Interactive Web Dashboard via Streamlit: `streamlit run main.py`
2. Automated Headless CLI Pipeline: `python main.py`
"""

import sys
import os
import pandas as pd
import numpy as np

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data_generator import generate_synthetic_poll
from src.validator import validate_dataset
from src.cleaner import clean_survey_data
from src.analyzer import (
    calculate_single_choice_share,
    calculate_multi_select_share,
    calculate_demographic_crosstab,
    calculate_numerical_summary,
    calculate_time_trend
)
from src.visualizer import (
    create_bar_chart,
    create_pie_chart,
    create_stacked_demographic_chart,
    create_trend_chart,
    create_numerical_distribution,
    save_static_summary_plot
)
from src.insights import generate_poll_insights
from src.report_generator import generate_pdf_report, export_summary_to_csv


# =====================================================================
# CLI HEADLESS PIPELINE EXECUTION
# =====================================================================
def run_cli_pipeline():
    """Executes the full automated analysis pipeline and saves all output artifacts."""
    print("=" * 70)
    print(" POLL RESULTS VISUALIZER - AUTOMATED ANALYTICS PIPELINE")
    print("=" * 70)
    
    # 1. Dataset Acquisition
    data_path = os.path.join("data", "poll_survey_data.csv")
    if os.path.exists(data_path):
        print(f"\n[Step 1] Loading existing survey dataset from '{data_path}'...")
        raw_df = pd.read_csv(data_path)
    else:
        print("\n[Step 1] Generating synthetic survey dataset...")
        raw_df = generate_synthetic_poll(n_responses=1200, seed=42, inject_noise=True)
        os.makedirs("data", exist_ok=True)
        raw_df.to_csv(data_path, index=False)
        print(f"-> Saved synthetic poll dataset to '{data_path}'.")
        
    print(f"-> Raw Dataset Shape: {raw_df.shape[0]} rows, {raw_df.shape[1]} columns.")
    
    # 2. Validation
    print("\n[Step 2] Validating dataset integrity & detecting column types...")
    val_report = validate_dataset(raw_df)
    print(f"-> Validation Passed: {val_report['is_valid']}")
    if val_report["warnings"]:
        for w in val_report["warnings"]:
            print(f"   [Notice] {w}")
            
    # 3. Transparent Cleaning
    print("\n[Step 3] Executing non-destructive cleaning pipeline...")
    clean_df, audit_log = clean_survey_data(raw_df, drop_duplicates=True, strip_whitespace=True, standardize_casing=True)
    print("-> Cleaning Audit Trail:")
    for entry in audit_log:
        print(f"   * {entry['step']}: {entry['action']}")
    print(f"-> Cleaned Dataset Shape: {clean_df.shape[0]} rows, {clean_df.shape[1]} columns.")
    
    # 4. Core Statistical Calculations
    target_question = "Primary_Platform"
    print(f"\n[Step 4] Computing vote shares and percentage distributions for '{target_question}'...")
    share_df = calculate_single_choice_share(clean_df, target_question)
    print("\n" + share_df.to_string(index=False))
    
    # Demographic Cross-tabulation
    demographic_col = "Region"
    print(f"\n[Step 5] Performing demographic comparative cross-tabulation ('{demographic_col}' vs. '{target_question}')...")
    crosstab_df = calculate_demographic_crosstab(clean_df, demographic_col, target_question)
    print("\n" + crosstab_df.to_string())
    
    # Numerical Rating Summary
    num_col = "Satisfaction_Score"
    print(f"\n[Step 6] Analyzing numerical rating metrics for '{num_col}'...")
    num_summary = calculate_numerical_summary(clean_df, num_col)
    for k, v in num_summary.items():
        print(f"   * {k}: {v}")
        
    # Multi-select Feature Analysis
    multi_col = "Key_Features"
    if multi_col in clean_df.columns:
        print(f"\n[Step 7] Analyzing multi-selection feature preferences ('{multi_col}')...")
        multi_df = calculate_multi_select_share(clean_df, multi_col, delimiter=";")
        print("\n" + multi_df.to_string(index=False))
        
    # 5. Automated Narrative Takeaways
    print("\n[Step 8] Generating automated factual narrative insights...")
    insights = generate_poll_insights(
        share_df=share_df,
        crosstab_df=crosstab_df,
        num_summary=num_summary,
        total_respondents=len(clean_df)
    )
    for idx, item in enumerate(insights, 1):
        clean_text = item.replace("**", "")
        print(f"   {idx}. {clean_text}")
        
    # 6. Export Visuals and PDF Report
    print("\n[Step 9] Exporting visual charts, CSV summaries, and executive PDF report...")
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    
    # Static chart for reports
    chart_img_path = os.path.join("images", "poll_results_overview.png")
    save_static_summary_plot(share_df, chart_img_path, title=f"Poll Results: {target_question} Share")
    print(f"-> Saved static chart image: '{chart_img_path}'")
    
    # CSV Exports
    csv_share_path = os.path.join("outputs", "vote_share_summary.csv")
    export_summary_to_csv(share_df, csv_share_path)
    csv_cross_path = os.path.join("outputs", "demographic_crosstab.csv")
    export_summary_to_csv(crosstab_df, csv_cross_path)
    print(f"-> Exported CSV summaries to 'outputs/'")
    
    # Executive PDF Generation
    pdf_report_path = os.path.join("outputs", "poll_results_executive_report.pdf")
    metrics_meta = {
        "sample_size": len(clean_df),
        "valid_votes": int(share_df["Votes"].sum()),
        "top_option": share_df.iloc[0]["Option"],
        "top_share": share_df.iloc[0]["Share (%)"]
    }
    generate_pdf_report(
        output_pdf_path=pdf_report_path,
        share_df=share_df,
        insights=insights,
        metrics=metrics_meta,
        static_chart_path=chart_img_path
    )
    print(f"-> Generated Executive PDF Report: '{pdf_report_path}'")
    
    print("\n" + "=" * 70)
    print(" PIPELINE EXECUTION COMPLETE. ALL ARTIFACTS SAVED SUCCESSFULLY.")
    print(" To launch the interactive web dashboard, run:")
    print("    streamlit run main.py")
    print("=" * 70)


# =====================================================================
# STREAMLIT INTERACTIVE WEB DASHBOARD
# =====================================================================
def run_streamlit_app():
    """Renders the full-featured interactive Streamlit web dashboard."""
    import streamlit as st
    
    # Page Configuration
    st.set_page_config(
        page_title="Poll Results Visualizer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom Styling
    st.markdown("""
        <style>
        .metric-box {
            background-color: #F8FAFC;
            border-left: 5px solid #2563EB;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .insight-card {
            background-color: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📊 Poll Results Visualizer & Insights Engine")
    st.caption("Interactive Survey Analytics, Demographic Comparative Analysis & Automated Insights")
    
    # Sidebar: Data Source & Filtering
    st.sidebar.header("📁 Data Source & Ingestion")
    source_choice = st.sidebar.radio("Choose Survey Dataset:", ["Built-in Sample (Consumer Tech Poll)", "Upload Custom CSV"])
    
    raw_df = None
    if source_choice == "Built-in Sample (Consumer Tech Poll)":
        data_path = os.path.join("data", "poll_survey_data.csv")
        if not os.path.exists(data_path):
            with st.spinner("Generating sample survey data..."):
                raw_df = generate_synthetic_poll(1200, seed=42, inject_noise=True)
                os.makedirs("data", exist_ok=True)
                raw_df.to_csv(data_path, index=False)
        else:
            raw_df = pd.read_csv(data_path)
    else:
        uploaded_file = st.sidebar.file_uploader("Upload Google Forms or Survey CSV:", type=["csv"])
        if uploaded_file is not None:
            raw_df = pd.read_csv(uploaded_file)
            
    if raw_df is None or raw_df.empty:
        st.info("👆 Please select or upload a valid survey CSV file in the sidebar to begin analysis.")
        st.stop()
        
    # Validation & Cleaning
    val_report = validate_dataset(raw_df)
    clean_df, audit_log = clean_survey_data(raw_df, drop_duplicates=True, strip_whitespace=True, standardize_casing=True)
    
    # Sidebar Demographic Slicers (Dynamic Filtering)
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Demographic Filters")
    filtered_df = clean_df.copy()
    
    # Region filter if exists
    if "Region" in filtered_df.columns:
        all_regions = ["All Regions"] + sorted(list(filtered_df["Region"].dropna().unique()))
        selected_region = st.sidebar.selectbox("Filter by Region:", all_regions)
        if selected_region != "All Regions":
            filtered_df = filtered_df[filtered_df["Region"] == selected_region]
            
    # Age group filter if exists
    if "Age_Group" in filtered_df.columns:
        all_ages = ["All Age Groups"] + sorted(list(filtered_df["Age_Group"].dropna().unique()))
        selected_age = st.sidebar.selectbox("Filter by Age Bracket:", all_ages)
        if selected_age != "All Age Groups":
            filtered_df = filtered_df[filtered_df["Age_Group"] == selected_age]
            
    # Main Tabs
    tab_overview, tab_eda, tab_cross, tab_cleaning, tab_export = st.tabs([
        "📈 Executive Dashboard",
        "📊 Question Analytics",
        "👥 Demographic Comparison",
        "🧹 Data Quality & Audit",
        "📄 Export & Reports"
    ])
    
    # Detect target question columns
    categorical_cols = [c for c, t in val_report["column_types"].items() if "Categorical" in t and c not in ["Region", "Age_Group", "Gender", "Education"]]
    if not categorical_cols:
        categorical_cols = [c for c in clean_df.select_dtypes(include="object").columns if c not in ["Respondent_ID", "Timestamp"]]
    default_target = "Primary_Platform" if "Primary_Platform" in categorical_cols else categorical_cols[0]
    
    # TAB 1: EXECUTIVE DASHBOARD
    with tab_overview:
        # Top KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sample Size", f"{len(raw_df):,}")
        col2.metric("Filtered Records", f"{len(filtered_df):,}")
        share_df = calculate_single_choice_share(filtered_df, default_target)
        if not share_df.empty:
            col3.metric("Leading Preference", str(share_df.iloc[0]["Option"]))
            col4.metric("Leader Share", f"{share_df.iloc[0]['Share (%)']}%")
            
        st.markdown("---")
        
        # Dual Plot Row
        c_left, c_right = st.columns([3, 2])
        with c_left:
            st.subheader(f"Preference Distribution: {default_target}")
            st.plotly_chart(create_bar_chart(share_df, title=f"{default_target} Vote Share"), use_container_width=True)
        with c_right:
            st.subheader("Share Breakdown")
            st.plotly_chart(create_pie_chart(share_df, title="Proportion Breakdown"), use_container_width=True)
            
        # Automated Insights Card
        st.subheader("💡 Automated Descriptive Insights")
        crosstab_region = calculate_demographic_crosstab(filtered_df, "Region", default_target) if "Region" in filtered_df.columns else None
        num_summary = calculate_numerical_summary(filtered_df, "Satisfaction_Score") if "Satisfaction_Score" in filtered_df.columns else None
        
        insights = generate_poll_insights(
            share_df=share_df,
            crosstab_df=crosstab_region,
            num_summary=num_summary,
            total_respondents=len(filtered_df)
        )
        for ins in insights:
            st.info(ins)
            
    # TAB 2: QUESTION ANALYTICS
    with tab_eda:
        st.subheader("Single-Variable Question Exploration")
        selected_q = st.selectbox("Select Question to Analyze:", [c for c in clean_df.columns if c not in ["Respondent_ID", "Timestamp"]])
        
        q_type = val_report["column_types"].get(selected_q, "Categorical")
        st.caption(f"Inferred Question Type: **{q_type}**")
        
        if "Multi-select" in q_type:
            multi_df = calculate_multi_select_share(filtered_df, selected_q)
            st.dataframe(multi_df, use_container_width=True)
            fig_multi = create_bar_chart(
                multi_df.rename(columns={"% of Respondents": "Share (%)", "Mentions": "Votes"}),
                title=f"{selected_q} (% of Respondents Selecting)"
            )
            st.plotly_chart(fig_multi, use_container_width=True)
        elif pd.api.types.is_numeric_dtype(filtered_df[selected_q]):
            stats = calculate_numerical_summary(filtered_df, selected_q)
            st.write("### Descriptive Statistics")
            st.json(stats)
            st.plotly_chart(create_numerical_distribution(filtered_df, selected_q), use_container_width=True)
        else:
            q_share = calculate_single_choice_share(filtered_df, selected_q)
            st.dataframe(q_share, use_container_width=True)
            st.plotly_chart(create_bar_chart(q_share, title=f"{selected_q} Share"), use_container_width=True)
            
    # TAB 3: DEMOGRAPHIC COMPARISON
    with tab_cross:
        st.subheader("Comparative Cross-Tabulation & Demographic Splits")
        demo_cols = [c for c in ["Region", "Age_Group", "Gender", "Education"] if c in filtered_df.columns]
        if not demo_cols:
            demo_cols = [c for c in filtered_df.columns if c != default_target]
            
        c1, c2 = st.columns(2)
        selected_demo = c1.selectbox("Demographic Grouping Variable:", demo_cols)
        selected_target = c2.selectbox("Target Question:", categorical_cols if categorical_cols else [c for c in filtered_df.columns if c != selected_demo])
        
        crosstab_res = calculate_demographic_crosstab(filtered_df, selected_demo, selected_target)
        st.write(f"### Percentage Breakdown: {selected_target} by {selected_demo} (%)")
        st.dataframe(crosstab_res, use_container_width=True)
        
        st.plotly_chart(
            create_stacked_demographic_chart(crosstab_res, title=f"{selected_target} by {selected_demo}"),
            use_container_width=True
        )
        
        if "Timestamp" in filtered_df.columns:
            st.markdown("---")
            st.subheader("Time-Series Response Share Trend")
            trend_data = calculate_time_trend(filtered_df, "Timestamp", selected_target)
            st.plotly_chart(create_trend_chart(trend_data, title=f"Trend Over Time for {selected_target}"), use_container_width=True)
            
    # TAB 4: DATA QUALITY & AUDIT
    with tab_cleaning:
        st.subheader("Data Quality Audit & Transparent Cleaning Log")
        st.write("Original uploaded data is preserved. All cleaning steps are documented below:")
        audit_table = pd.DataFrame(audit_log)
        st.table(audit_table)
        
        st.write("### Dataset Preview (First 10 Cleaned Records)")
        st.dataframe(clean_df.head(10), use_container_width=True)
        
    # TAB 5: EXPORT & REPORTS
    with tab_export:
        st.subheader("Generate & Export Reports")
        st.write("Download analytical summary tables or compile a publication-ready executive PDF report.")
        
        # CSV Export
        csv_data = share_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Vote Share Summary (CSV)",
            data=csv_data,
            file_name="vote_share_summary.csv",
            mime="text/csv"
        )
        
        # PDF Generation Button
        if st.button("📄 Generate Executive PDF Report"):
            with st.spinner("Compiling PDF report..."):
                os.makedirs("images", exist_ok=True)
                os.makedirs("outputs", exist_ok=True)
                chart_path = os.path.join("images", "pdf_summary_chart.png")
                save_static_summary_plot(share_df, chart_path, title=f"Survey Overview: {default_target}")
                
                pdf_path = os.path.join("outputs", "survey_executive_report.pdf")
                metrics_dict = {
                    "sample_size": len(clean_df),
                    "valid_votes": int(share_df["Votes"].sum()),
                    "top_option": share_df.iloc[0]["Option"],
                    "top_share": share_df.iloc[0]["Share (%)"]
                }
                generate_pdf_report(
                    output_pdf_path=pdf_path,
                    share_df=share_df,
                    insights=insights,
                    metrics=metrics_dict,
                    static_chart_path=chart_path
                )
                
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                    
                st.success("Executive PDF report generated successfully!")
                st.download_button(
                    label="⬇️ Download Executive PDF Report",
                    data=pdf_bytes,
                    file_name="poll_results_executive_report.pdf",
                    mime="application/pdf"
                )


# =====================================================================
# SCRIPT EXECUTION SELECTOR
# =====================================================================
def is_running_with_streamlit() -> bool:
    """Accurately detects if the script is running inside a Streamlit runner process."""
    import inspect
    for frame in inspect.stack():
        # Check if any parent caller in the call stack originates from the streamlit package
        if "streamlit" in frame.filename.lower() and not frame.filename.lower().endswith("main.py"):
            return True
    return False

if __name__ == "__main__":
    if is_running_with_streamlit():
        run_streamlit_app()
    else:
        run_cli_pipeline()


