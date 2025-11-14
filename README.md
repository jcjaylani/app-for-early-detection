# Parkinson’s Disease Threshold-Based Detection App
### A Streamlit Application for Biomarker-Driven Early Detection

#### Application for early detection of Parkinson's disease based on blood-tested biomarkers

##### link for streamlit deployed app: https://app-for-pd-early-detection.streamlit.app/

### Overview
This interactive Streamlit application provides a threshold-based scoring system to support early detection of Parkinson’s disease (PD) using blood-based biomarker values. The app combines statistical thresholding, ROC-based cutoff optimization, and weighted scoring to produce an interpretable PD risk score for individual patients.
The app is designed for researchers, data analysts, and clinicians interested in evaluating biomarker panels, comparing rule-based scoring with ML models, and validating candidate thresholds in real datasets.

### Key Features
#### 1. Upload Patient Biomarker Data
Accepts CSV files exported from lab or research datasets.
Automatically standardizes column names and validates required features.
Supports single-patient or multi-patient rows.


#### 2. Analysis Mode
✓ Threshold Mode (Youden / ROC Cutoffs)
Uses a curated biomarker panel with:
Direction (↑ or ↓)
ROC-optimized threshold
Feature-specific diagnostic weight
Computes patient-level PD scores using weighted summation.
Produces a final class prediction (PD / Control).


#### 3. Visual Outputs
Interactive threshold plots (Plotly).
Distribution comparisons for each biomarker.
Summary of contribution weights.
Patient-level score cards.

#### 4. Real-Time Validation & Error Checking
Detects missing biomarkers.
Warns if thresholds cannot be applied.
Confirms successful file loading and data alignment.

### Required Input Files
#### 1. Threshold Panel (thresholds.csv)
Your panel should contain at minimum:<br>
biomarker<br>
direction <br>
threshold<br> 
weight<br> 
<br>
example:A2MG>0.0380.0313-Hydroxykynurenine>18.0650.075…………


### How to Use the App
#### 1. Launch the App
If using Streamlit Cloud, simply open the deployed URL:<br>
https://your-app-name.streamlit.app<br>
If running locally:<br>
streamlit run parkinsons_threshold_app.py<br>

#### 2. Upload Required Files
Biomarker CSV<br>
Threshold CSV<br>
Image/logo (optional)<br>

#### 3. View Results
The app displays:<br>
Prediction (PD / Control)<br>
Probability (if model-based)<br>
Weighted threshold score<br>
Per-biomarker contributions<br>
Interactive plots<br>

### Scientific Background
The method used in this app is based on:<br>
ROC-curve based threshold selection<br>
Youden’s index optimization<br>
Feature weighting using normalized AUC values<br>
Summed risk scoring across informative biomarkers<br>
Validation via stratified cross-validation<br>

This approach is interpretable, lightweight, and suitable for pairing with blood-based biomarker panels that may be used in screening or early-stage research.

### Installation
pip install -r requirements.txt

Make sure your environment includes:

Python 3.10+<br>
Streamlit<br>
Pandas / NumPy<br>
Plotly<br>
Scikit-learn<br>
XGBoost (optional)<br>

### Project Structure
project/ <br>
│── pd_threshold_app.py <br>
│── PD_StrongBiomarkers.csv (thresholds for top blood-based biomarkers) <br>
│── PD_Image_4.png <br>
│── requirements.txt <br>
│── README.md <br>

### Additional Files
│── Presentation Towards Early Detection.ppt <br>
│── blood_markers_top_results.xlsx (thresholds for top blood-based biomarkers)<br>
│── Video Introduction PD.mp4 (by Priyanka Gowd Mitta, M.D)  <br>

### Example Biomarker Format
PatientID,A2MG,3-Hydroxykynurenine,LYSC,CatD,… <br>
001,0.041,18.5,121,0.92,…<br>


### Citation / Acknowledgements
If you use this tool in academic work, please cite: <br>
Jaylani, J. (2025). Threshold-Based Biomarker Classification for Early Parkinson’s Disease Detection.<br>
Presented at the 2025 Center for Analytics Symposium, Sacred Heart University.<br>
<br>
#### Introductory Video by Priyanka Gowd Mitta, M.D

### Contact
For questions, collaboration, or feedback:<br>
Joan Jaylani<br>
Innovative Insights Consulting LLC<br>
GitHub: @jcjaylani<br>

