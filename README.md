# OncoRisk ML

A modular, end-to-end machine learning system for predicting cancer risk levels (Low, Medium, High) using patient demographic, behavioral, and health-related data.

---

## Overview

OncoRisk ML takes structured patient data and runs it through a complete ML pipeline -- from data ingestion and preprocessing through model training, evaluation, and a web-based prediction interface. The system compares three models (Logistic Regression, Random Forest, XGBoost) and selects the best performer using robust evaluation metrics.

This project is built with a clean, modular architecture that separates each stage of the ML workflow into independent, reusable modules.

---

## Architecture

```
Dataset (CSV)
    |
    v
Data Ingestion --> load, validate, check for issues
    |
    v
Preprocessing --> clean, encode, scale, split
    |
    v
EDA --> statistical summaries, visualizations
    |
    v
SMOTE --> balance class distribution (training data only)
    |
    v
Model Training --> Logistic Regression, Random Forest, XGBoost
    |
    v
Hyperparameter Tuning --> Optuna (Bayesian optimization)
    |
    v
Evaluation --> Accuracy, Recall, F1-Score, Confusion Matrix
    |
    v
Save Best Model --> Joblib serialization
    |
    v
Streamlit App --> user inputs patient data, gets risk prediction
```

---

## Project Structure

```
Predictive-Modeling-for-Cancer-Risk-Assessment/
|
|-- data/
|   |-- raw/                    # Original dataset (not tracked in Git)
|   |-- processed/              # Cleaned and transformed data
|
|-- notebooks/                  # Jupyter notebooks for exploration
|
|-- src/
|   |-- __init__.py
|   |-- data_ingestion.py       # Load and validate raw data
|   |-- preprocessing.py        # Clean, encode, scale, split
|   |-- eda.py                  # Exploratory data analysis and plots
|   |-- smote_handler.py        # Class imbalance handling with SMOTE
|   |-- train_model.py          # Train multiple ML models
|   |-- tune_model.py           # Hyperparameter tuning with Optuna
|   |-- evaluate_model.py       # Metrics, confusion matrix, comparison
|   |-- predict.py              # Run predictions on new data
|   |-- utils.py                # Model save/load utilities
|
|-- models/                     # Saved model artifacts (not tracked in Git)
|
|-- visuals/                    # Generated plots and charts
|
|-- app/
|   |-- app.py                  # Streamlit web application
|   |-- components/             # Reusable UI components
|   |-- assets/                 # Static files for the app
|
|-- reports/                    # Generated analysis reports
|
|-- requirements.txt            # Python dependencies
|-- main.py                     # Pipeline entry point
|-- .gitignore
|-- README.md
```

---

## ML Workflow

### 1. Data Ingestion
Load the raw CSV dataset and run validation checks (missing values, duplicates, data types).

### 2. Preprocessing
- Drop unnecessary columns (Patient ID)
- Encode categorical features
- Scale numerical features using StandardScaler
- Split into train/test sets (80/20, stratified)

### 3. Exploratory Data Analysis
- Class distribution (Low vs Medium vs High)
- Feature correlation heatmap
- Distribution plots per feature
- Summary statistics

### 4. SMOTE (Class Balancing)
Apply Synthetic Minority Oversampling to the training set only to address class imbalance.

### 5. Model Training
Train three models with default parameters:
- Logistic Regression (linear baseline)
- Random Forest (ensemble, non-linear)
- XGBoost (gradient boosting)

### 6. Hyperparameter Tuning
Use Optuna to optimize Random Forest and XGBoost hyperparameters through Bayesian search.

### 7. Evaluation
Compare all models using:
- Accuracy
- Recall (critical for medical risk -- minimize missed high-risk cases)
- F1-Score
- Confusion Matrix

### 8. Model Persistence
Save the best-performing model and fitted scaler using Joblib for use in the Streamlit app.

---

## Screenshots

> Screenshots will be added as each module is completed.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/Rudra2986/Predictive-Modeling-for-Cancer-Risk-Assessment.git
cd Predictive-Modeling-for-Cancer-Risk-Assessment

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the full ML pipeline
python main.py

# Launch the Streamlit app
streamlit run app/app.py
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| Scikit-learn | ML models, preprocessing, evaluation |
| XGBoost | Gradient boosting model |
| Imbalanced-learn | SMOTE for class balancing |
| Optuna | Hyperparameter tuning |
| Streamlit | Web application |
| Joblib | Model serialization |
| Matplotlib / Seaborn | Visualizations |

---

## Future Scope

- Add more models (LightGBM, CatBoost)
- Implement SHAP-based model explainability
- Add patient data upload feature in the Streamlit app
- Integrate CI/CD for automated testing
- Deploy to cloud infrastructure

---

## License

This project is for educational and portfolio purposes.
