# Parkinson’s Disease Threshold-Based Detection App
### A Streamlit Application for Biomarker-Driven Early Detection

#### Application for early detection of Parkinson's disease based on blood-tested biomarkers

#### link for streamlit deployed app: https://app-for-pd-early-detection.streamlit.app/

#### Overview
This interactive Streamlit application provides a threshold-based scoring system to support early detection of Parkinson’s disease (PD) using blood-based biomarker values. The app combines statistical thresholding, ROC-based cutoff optimization, and weighted scoring to produce an interpretable PD risk score for individual patients.
The app is designed for researchers, data analysts, and clinicians interested in evaluating biomarker panels, comparing rule-based scoring with ML models, and validating candidate thresholds in real datasets.

####🔍 Key Features
1. Upload Patient Biomarker Data
Accepts CSV files exported from lab or research datasets.
Automatically standardizes column names and validates required features.
Supports single-patient or multi-patient rows.


2. Analysis Mode
✓ Threshold Mode (Youden / ROC Cutoffs)
Uses a curated biomarker panel with:
Direction (↑ or ↓)
ROC-optimized threshold
Feature-specific diagnostic weight
Computes patient-level PD scores using weighted summation.
Produces a final class prediction (PD / Control).


3. Visual Outputs
Interactive threshold plots (Plotly).
Distribution comparisons for each biomarker.
Summary of contribution weights.
Patient-level score cards.

4. Real-Time Validation & Error Checking
Detects missing biomarkers.
Warns if thresholds cannot be applied.
Confirms successful file loading and data alignment.

📁 Required Input Files
1. Threshold Panel (thresholds.csv)
Your panel should contain at minimum:
biomarkerdirectionthresholdweightA2MG>0.0380.0313-Hydroxykynurenine>18.0650.075…………
2. (Optional) Machine Learning Model (model.pkl)
Any scikit-learn or XGBoost classifier saved via joblib or pickle.

🚀 How to Use the App
1. Launch the App
If using Streamlit Cloud, simply open the deployed URL:
👉 https://your-app-name.streamlit.app
If running locally:
streamlit run parkinsons_threshold_app.py

2. Choose an Analysis Mode (Sidebar)
Threshold (Youden/ROC)
Trained Model (.pkl)

3. Upload Required Files
Biomarker CSV
Threshold CSV or Model File
Image/logo (optional)

4. View Results
The app displays:
Prediction (PD / Control)
Probability (if model-based)
Weighted threshold score
Per-biomarker contributions
Interactive plots



🧠 Scientific Background
The method used in this app is based on:
ROC-curve based threshold selection
Youden’s index optimization
Feature weighting using normalized AUC values
Summed risk scoring across informative biomarkers
Validation via stratified cross-validation

This approach is interpretable, lightweight, and suitable for pairing with blood-based biomarker panels that may be used in screening or early-stage research.

📦 Installation
pip install -r requirements.txt

Make sure your environment includes:

Python 3.10+
Streamlit
Pandas / NumPy
Plotly
Scikit-learn
XGBoost (optional)

📁 Project Structure
project/
│── parkinsons_threshold_app.py
│── thresholds.csv
│── model.pkl (optional)
│── pd_image.png
│── requirements.txt
│── README.md


🧪 Example Biomarker Format
PatientID,A2MG,3-Hydroxykynurenine,LYSC,CatD,…
001,0.041,18.5,121,0.92,…


📣 Citation / Acknowledgements
If you use this tool in academic work, please cite:
Jaylani, J. (2025). Threshold-Based Biomarker Classification for Early Parkinson’s Disease Detection.
Presented at the 2025 Center for Analytics Symposium, Sacred Heart University.

📬 Contact
For questions, collaboration, or feedback:
Joan Jaylani
Innovative Insights Consulting LLC
GitHub: @jcjaylani
Email: (add if you want)

If you'd like, I can also:
✅ Add screenshots
✅ Generate a badge section (version, license, build)
✅ Add usage examples with real patient data
✅ Format this README specifically for GitHub with emojis + collapsible sections
Just let me know!
