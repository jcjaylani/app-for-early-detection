import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# Page setup
st.set_page_config(page_title="PD Biomarker Threshold App", layout="wide")

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

display_logo("PD_Image_4.png")

# ---------- Load fixed thresholds file ----------
THRESHOLD_FILE = Path("PD_StrongBiomarkers.csv")

if not THRESHOLD_FILE.exists():
    st.error("❌ Could not find xgb_thresholds_top_15.csv in the app folder.")
    st.stop()

th = pd.read_csv(THRESHOLD_FILE)
th.columns = th.columns.str.strip().str.title()   # Normalize capitalization

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

st.subheader("Threshold-based PD Probability Estimator")

# Calibration parameters
cal_a = st.number_input("Calibration slope (a)", value=1.0)
cal_b = st.number_input("Calibration intercept (b)", value=0.0)

# ---------- Generate Inputs ----------
st.subheader("Patient Biomarker Inputs")
cols = st.columns(2)
inputs = {}

for i, row in enumerate(th.to_dict(orient="records")):
    label = row["Biomarker"]
    default_val = safe_float(row["Threshold"])

    inputs[label] = cols[i % 2].number_input(
        label,
        value=float(default_val),
        step=0.00001,
        format="%.5f"
    )

# ---------- Compute Probability ----------
if st.button("Compute probability (threshold score)"):
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

        # Details for table
        details.append({
            "Biomarker": biom,
            "Value": val,
            "Threshold": t,
            "Direction": d,
            "Match": hit,
            "Weight": w
        })

    norm_score = score / max(total_w, 1e-9)
    prob = 1.0 / (1.0 + np.exp(-(cal_a * norm_score + cal_b)))

    st.metric("Threshold score (weighted fraction of hits)", f"{norm_score:.3f}")
    st.metric("Estimated PD probability", f"{prob:.3f}")
    st.dataframe(pd.DataFrame(details))