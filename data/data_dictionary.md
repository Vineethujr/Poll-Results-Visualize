# Poll Results Visualizer - Data Dictionary

### Dataset Title: Consumer Technology & Digital Platforms Poll 2026
* **Filename**: `data/poll_survey_data.csv`
* **Total Records**: 1,203 responses (1,200 unique respondents + test duplicates)
* **Date Range**: January 2026 – October 2026
* **Format**: Standard Survey CSV (Google Forms compatible)

---

### Variable Definitions

| Variable Name | Data Type | Description | Permitted / Sample Values |
| :--- | :--- | :--- | :--- |
| `Respondent_ID` | String / Identifier | Unique identifier assigned to each participant | `RESP_1000` to `RESP_2199` |
| `Timestamp` | Date (`YYYY-MM-DD`) | Date when survey response was recorded | 2026-01-15 to 2026-10-15 |
| `Region` | Categorical (Nominal) | Geographical territory of the respondent | `North`, `South`, `East`, `West`, `Central` |
| `Age_Group` | Categorical (Ordinal) | Respondent age bracket | `18-25`, `26-35`, `36-50`, `51-65`, `65+` |
| `Gender` | Categorical (Nominal) | Self-identified gender | `Female`, `Male`, `Non-Binary`, `Prefer not to say` |
| `Education` | Categorical (Ordinal) | Highest level of completed education | `High School`, `Bachelor's`, `Master's`, `Doctorate` |
| `Primary_Platform`| Categorical (Nominal) | Preferred digital platform (Target Question) | `Platform Alpha`, `Platform Beta`, `Platform Gamma`, `Platform Delta` |
| `Satisfaction_Score`| Numerical (Discrete)| Satisfaction rating on a 10-point scale | `1` (Extremely Dissatisfied) to `10` (Extremely Satisfied) |
| `Key_Features` | Multi-select String | Most valued platform features (semicolon-separated) | `Ease of Use`, `Data Privacy & Security`, `Speed & Performance`, etc. |
| `Would_Recommend` | Categorical (Nominal) | Likelihood of recommending platform to peers | `Yes`, `No`, `Maybe` |

---

### Data Quality & Anomaly Design
To test and demonstrate robust data cleaning capabilities, this dataset incorporates:
* Trailing whitespaces in categorical fields.
* Inconsistent lowercase text in regional categories.
* Missing values in optional fields (~1.5%).
* Exact duplicated rows for deduplication verification.
