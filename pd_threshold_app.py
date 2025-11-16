import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# Page setup
st.set_page_config(page_title="PD Biomarker Threshold App", layout="wide")

st.markdown("""
<style>
/* Entire background (main + sidebars) */
[data-testid="stAppViewContainer"] {
    background-color: #f5f5f5;   /* light gray */
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #f5f5f5;
}

/* Optional: remove white streaks/padding */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* Optional tweak: make cards pop more */
.card {
    background-color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Main content container */
[data-testid="stAppViewContainer"] .main {
    background-color: #ffffff !important;   /* white */
}

/* Keep the overall page / around the main area light gray */
[data-testid="stAppViewContainer"] {
    background-color: #f5f5f5 !important;
}

/* Also set sidebar to light gray (optional) */
[data-testid="stSidebar"] {
    background-color: #f5f5f5 !important;
}
</style>
""", unsafe_allow_html=True)


# ---------- Logo ----------
def display_logo(image_filename):
    image_path = Path(__file__).parent / image_filename
    if not image_path.exists():
        st.error(f"❌ Image not found: {image_path}")
        return
    st.markdown(
        "<style>.logo { display: flex; justify-content: center; margin-bottom: 5px; }</style>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="logo">', unsafe_allow_html=True)
    st.image(str(image_path), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

display_logo("PD_App_Banner_Large.png")


# --------------------------------------------------------
# Clinical Dashboard CSS
# --------------------------------------------------------
st.markdown("""
<style>
/* Clean card style */
.card {
    background-color: #ffffff;
    padding: 16px 20px;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    margin-bottom: 15px;
    box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
}

/* Better section headers */
h3 {
    font-family: 'Roboto', sans-serif;
    font-weight: 600;
    margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)


# ---------- Load fixed thresholds file ----------
THRESHOLD_FILE = Path("PD_StrongBiomarkers.csv")

if not THRESHOLD_FILE.exists():
    st.error("❌ Could not find PD_5_Biomarkers.csv in the app folder.")
    st.stop()

th = pd.read_csv(THRESHOLD_FILE)
th.columns = th.columns.str.strip().str.title()   # Normalize capitalization

# -------------------------------------------------------------
# Automatically recalculate weights based on MeanImportance
# -------------------------------------------------------------
if "Meanimportance" in th.columns:
    # Ensure numeric
    th["Meanimportance"] = pd.to_numeric(th["Meanimportance"], errors="coerce")

    # Prevent divide-by-zero
    total_imp = th["Meanimportance"].sum()
    if total_imp > 0:
        th["Weight"] = th["Meanimportance"] / total_imp
    else:
        st.error("MeanImportance column sums to zero. Cannot recompute weights.")
else:
    st.error("Uploaded CSV is missing 'MeanImportance' needed for automatic weight recalculation.")

# -------------------------------------------------------------
# Required columns
# -------------------------------------------------------------

# Required columns
required = ["Biomarker", "Direction", "Threshold", "Weight"]
missing = [c for c in required if c not in th.columns]
if missing:
    st.error(f"❌ The threshold file is missing the following required columns: {missing}")
    st.stop()



# ---------- Clean Biomarker Labels ----------
def safe_label(x, idx):
    if pd.isna(x) or str(x).strip() in ["", "nan", "None"]:
        return f"Biomarker_{idx+1}"
    return str(x).strip()

th["Biomarker"] = [safe_label(b, i) for i, b in enumerate(th["Biomarker"])]

# ---------- Clean Threshold Values ----------
def safe_float(x):
    try:
        x = float(x)
        if np.isnan(x):
            return 0.0
        return x
    except:
        return 0.0

th["Threshold"] = th["Threshold"].apply(safe_float)

# st.subheader("Threshold-based PD Probability Estimator")

# Calibration parameters
cal_a = st.number_input("Calibration slope (a)", value=1.0)
cal_b = st.number_input("Calibration intercept (b)", value=0.0)


# --- Create gauge figure once you compute pd_score ---
#pd_score = st.session_state.get("pd_score", None)

#if pd_score is not None:
#    fig = go.Figure(go.Indicator(
 #       mode="gauge+number",
  #      value=pd_score,
   #     gauge={"axis": {"range": [0, 100]}},
    #))
    #st.session_state["fig_gauge"] = fig
    
# --------------------------------------------------------
# Clinical Dashboard Layout (Left Panel: Inputs)
# --------------------------------------------------------
left_col, right_col = st.columns([1.1, 1.4])   # slightly larger results panel

with left_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Patient Biomarker Inputs")

    inputs = {}
    input_cols = st.columns(2)

    for i, row in enumerate(th.to_dict(orient="records")):
        label = row["Biomarker"]
        default_val = float(row["Threshold"])

        inputs[label] = input_cols[i % 2].number_input(
            label,
            value=default_val,
            step=0.00001,
            format="%.5f"
        )

    st.markdown("</div>", unsafe_allow_html=True)
    
    # PD Gauge Card (shows after calculation)
   # if st.session_state.get("computed", False):
    #    st.markdown("<div class='card'>", unsafe_allow_html=True)
     #   st.subheader("📈 PD Risk Gauge")
      #  st.plotly_chart(st.session_state["fig_gauge"], use_container_width=True)
       # st.markdown("</div>", unsafe_allow_html=True)  # end of card


# ---------------------------------------------------------
# Compute PD Probability + Clinical Visualizations
# ---------------------------------------------------------
with right_col:


    if st.button("Compute probability (threshold score)"):

        # ----------------------------
        # STEP 1: Compute threshold score
        # ----------------------------
        score = 0.0
        total_w = 0.0
        details = []

        for _, r in th.iterrows():
            biom = r["Biomarker"]
            d = r["Direction"]
            t = float(r["Threshold"])
            w = r["Weight"] if not pd.isna(r["Weight"]) else 1.0

            val = inputs.get(biom, np.nan)

            # Determine hit/miss
            if pd.notna(val):
                hit = (val > t) if d.strip() == ">" else (val < t)
            else:
                hit = False

            # Score accumulation
            score += w * (1.0 if hit else 0.0)
            total_w += w

            # Save row details
            details.append({
                "Biomarker": biom,
                "Value": val,
                "Threshold": t,
                "Direction": d,
                "Match": hit,
                "Weight": w
            })

        # Normalize score + logistic calibration
        norm_score = score / max(total_w, 1e-9)
        prob = 1.0 / (1.0 + np.exp(-(cal_a * norm_score + cal_b)))

        # ----------------------------
        # STEP 2: Display numeric results
        # ----------------------------
        st.metric("Threshold Score (Weighted)", f"{norm_score:.3f}")
        st.metric("Estimated PD Probability", f"{prob:.3f}")

        df_details = pd.DataFrame(details)
        st.dataframe(df_details)

        # Add contribution column
        df_details["Contribution"] = df_details["Weight"] * df_details["Match"].astype(int)

        # Count hits
        hits_count = int(df_details["Match"].sum())
        total_tests = len(df_details)

        # ----------------------------
        # STEP 3: Traffic-Light Risk Category
        # ----------------------------
        st.subheader("Clinical Risk Summary")

        if prob < 0.20:
            risk_cat = "Low"
            risk_msg = "Low probability of Parkinson’s based on this biomarker panel."
            box_color = "#d4edda"
        elif prob < 0.50:
            risk_cat = "Borderline"
            risk_msg = (
                "Mildly elevated biomarker pattern; consider monitoring, repeat testing, "
                "and correlation with symptoms."
            )
            box_color = "#fff3cd"
        elif prob < 0.75:
            risk_cat = "Moderate"
            risk_msg = (
                "Biomarker pattern suggests increased likelihood of Parkinson’s; clinical correlation "
                "and neurology evaluation are recommended."
            )
            box_color = "#ffe5b4"
        else:
            risk_cat = "High"
            risk_msg = (
                "Biomarker pattern is strongly suggestive of increased Parkinson’s disease risk; "
                "a comprehensive neurological assessment is recommended."
            )
            box_color = "#f8d7da"

        st.markdown(
            f"""
            <div style="border-radius:10px;padding:12px;background-color:{box_color};
                        border:1px solid #ccc;margin-bottom:10px;">
                <b>Risk Category:</b> {risk_cat} ({prob*100:.1f}% estimated probability)<br>
                <b>Threshold score:</b> {norm_score:.3f}<br>
                <b>Threshold hits:</b> {hits_count} of {total_tests} biomarkers met the risk criterion.<br><br>
                {risk_msg}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------
        # STEP 4: Automatic Clinical Interpretation
        # ----------------------------
        st.subheader("Clinical Interpretation")
        st.markdown("<i>Draft – Not for Diagnostic Use</i>", unsafe_allow_html=True)

        top_biomarkers = df_details.sort_values("Contribution", ascending=False).head(3)

        interpretation_lines = []
        interpretation_lines.append(
            f"- **Overall risk:** {risk_cat} (estimated probability {prob*100:.1f}%)."
        )
        interpretation_lines.append(
            f"- **Threshold hits:** {hits_count} of {total_tests} biomarkers met the risk "
            f"criterion used in this panel."
        )
        interpretation_lines.append("- **Most influential biomarkers:**")

        for _, row in top_biomarkers.iterrows():
            direction_word = "above" if str(row["Direction"]).strip() == ">" else "below"
            relation = "met" if row["Match"] else "did not meet"
            interpretation_lines.append(
                f"  • **{row['Biomarker']}** — patient value {row['Value']:.4f} is "
                f"{direction_word} the threshold ({row['Threshold']:.4f}); this {relation} "
                f"the risk criterion and contributes **{row['Contribution']:.3f}** to the risk score."
            )

        # Recommendation summary
        if prob >= 0.75:
            rec = (
                "The biomarker pattern strongly suggests increased Parkinson’s risk. "
                "Comprehensive neurology evaluation is recommended."
            )
        elif prob >= 0.50:
            rec = (
                "Biomarker changes indicate moderate elevation in Parkinson’s risk. "
                "Clinical correlation and follow-up testing are advised."
            )
        elif prob >= 0.20:
            rec = (
                "Mild biomarker elevation observed. Monitoring and re-evaluation may be appropriate "
                "if symptoms develop."
            )
        else:
            rec = (
                "Low biomarker-based probability of Parkinson’s on this panel. "
                "Interpret within full clinical context."
            )

        interpretation_lines.append("")
        interpretation_lines.append(rec)
        interpretation_lines.append("")
        interpretation_lines.append(
            "⚠️ **Disclaimer:** This tool is for research and educational purposes only and is **not** a "
            "substitute for clinical diagnosis or medical judgment."
        )

        st.markdown("\n".join(interpretation_lines))

    # ---------------------------------------------------------
    # Probability Gauge (Clinician-friendly)
    # ---------------------------------------------------------
       # ---------- PROBABILITY GAUGE ----------
    
            
        
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={"suffix": "%", "valueformat": ".1f"},
                title={"text": "Estimated PD Probability"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "darkred"},
                    "steps": [
                        {"range": [0, 20], "color": "#d4edda"},
                        {"range": [20, 50], "color": "#fff3cd"},
                        {"range": [50, 75], "color": "#ffe5b4"},
                        {"range": [75, 100], "color": "#f8d7da"},
                    ],
                },
            )
        )

        
       
        # Save gauge
        st.session_state["fig_gauge"] = fig_gauge
        st.session_state["computed"] = True


        if st.session_state.get("fig_gauge", None) is not None:
            with left_col:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.subheader("PD Risk Gauge")
                st.plotly_chart(st.session_state["fig_gauge"], use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
        
        
    # ---------------------------------------------------------
    # PD vs Control Distribution Comparison
    # ---------------------------------------------------------
        st.subheader("Biomarker Distributions (PD vs Control Reference)")

        with st.expander("Upload Cohorts to Compare Distributions"):
            st.write(
                "Upload optional PD and Control datasets (CSV) containing the same biomarker names "
                "to compare this patient's values to reference distributions."
            )

            pd_file = st.file_uploader("Upload PD cohort CSV", type=["csv"], key="pd_cohort")
            ctl_file = st.file_uploader("Upload Control cohort CSV", type=["csv"], key="ctl_cohort")

            if pd_file is not None and ctl_file is not None:
                pd_df = pd.read_csv(pd_file)
                ctl_df = pd.read_csv(ctl_file)

                # Identify top 3 most influential biomarkers
                top3 = (
                    df_details.sort_values("Contribution", ascending=False)["Biomarker"]
                    .head(3)
                    .tolist()
                )

                st.write(f"Most influential biomarkers: **{', '.join(top3)}**")

                for biom in top3:
                    if biom not in pd_df.columns or biom not in ctl_df.columns:
                        st.warning(f"Biomarker '{biom}' not found in both reference datasets.")
                        continue

                    # Clean data
                    pd_vals = pd_df[biom].dropna()
                    ctl_vals = ctl_df[biom].dropna()

                    if len(pd_vals) == 0 or len(ctl_vals) == 0:
                        st.warning(f"Not enough reference data to plot '{biom}'.")
                        continue

                    # Build a density-normalized plot
                    plot_df = pd.DataFrame({
                        "Value": pd.concat([pd_vals, ctl_vals], ignore_index=True),
                        "Group": (["PD"] * len(pd_vals)) + (["Control"] * len(ctl_vals)),
                    })

                    fig_dist = px.histogram(
                        plot_df,
                        x="Value",
                        color="Group",
                        barmode="overlay",
                        histnorm="probability density",
                        title=f"{biom}: PD vs Control Distribution",
                        opacity=0.6,
                    )

                    # Add patient value as a vertical line
                    patient_val = df_details.loc[df_details["Biomarker"] == biom, "Value"].iloc[0]

                    fig_dist.add_vline(
                        x=patient_val,
                        line_width=3,
                        line_dash="dash",
                        line_color="black",
                        annotation_text="Patient",
                        annotation_position="top right",
                    )

                    st.plotly_chart(fig_dist, use_container_width=True)
            else:
                st.info("Upload both PD and Control cohort CSV files to generate overlay histograms.")
