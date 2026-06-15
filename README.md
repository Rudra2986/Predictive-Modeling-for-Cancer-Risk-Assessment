# OncoRisk AI

OncoRisk AI is a production-grade healthcare AI platform focused on predictive modeling for cancer risk assessment using machine learning. The platform utilizes demographic, lifestyle, and health-related clinical patient profiles to predict cancer risk levels (Low, Medium, High) along with confidence scores and explainable model metrics.

The platform is designed using a clean, decoupled architecture:
1. **Frontend Dashboard:** A responsive Next.js web application utilizing Tailwind CSS for minimal styling, Framer Motion for micro-animations, and Recharts for interactive clinical charts.
2. **FastAPI Backend:** An asynchronous REST API executing data processing pipelines and loading serialized machine learning models.
3. **ML Prediction Engine:** A modular pipeline utilizing Scikit-learn, XGBoost, and SMOTE for class imbalance handling, optimized using Optuna hyperparameter search.
4. **Local PostgreSQL Database:** Relational persistent storage mapped via SQLAlchemy ORM for patient query logs and audits.

---

## System Architecture

```
User (Web Browser)
       │
       ▼
┌────────────────────────────────────────┐
│ Next.js Frontend Dashboard (App Router)│
└───────────────────┬────────────────────┘
                    │
            HTTPS REST Request
                    │
                    ▼
┌────────────────────────────────────────┐
│        FastAPI REST Backend            │
│ ┌────────────────────────────────────┐ │
│ │        ML Prediction Engine        │ │
│ │   - Custom Preprocessing Pipeline  │ │
│ │   - XGBoost Classifier Inference   │ │
│ └──────────────────┬─────────────────┘ │
└────────────────────┼───────────────────┘
                     │
              SQLAlchemy ORM
                     │
                     ▼
┌────────────────────────────────────────┐
│        PostgreSQL Database             │
└────────────────────────────────────────┘
```

---

## Repository Structure

```
OncoRisk-AI/
│
├── frontend/             # Next.js Web Dashboard
│   ├── app/              # App Router Pages
│   ├── components/       # Reusable UI Components
│   ├── animations/       # Framer Motion Configs
│   ├── charts/           # Recharts Visualizations
│   ├── public/           # Static Assets
│   └── styles/           # Global Styling
│
├── backend/              # FastAPI Application
│   ├── api/              # Route Handlers & Controllers
│   ├── models/           # SQLAlchemy DB Models & Schemas
│   ├── ml/               # Model Inference & Saved Pipelines
│   ├── database/         # Session Configuration & Migrations
│   ├── services/         # Business Logic Layer
│   ├── utils/            # Shared Helpers (Logging, Security)
│   └── main.py           # Application Entrypoint
│
├── datasets/             # Data Assets
│   ├── raw/              # Raw CSV Dataset Files
│   └── processed/        # Processed/Cleaned Splits
│
├── notebooks/            # Jupyter Notebooks for EDA
│
├── deployment/           # Deployment Configurations
│   └── configs/          # Docker & Reverse Proxy Configs
│
├── reports/              # Model Validation & Metric Reports
│
├── README.md             # Project Documentation
├── requirements.txt      # Python Package Dependencies
├── .gitignore            # Git Excluded Path Configurations
└── docker-compose.yml    # Local Infrastructure Orchestration
```

---

## Machine Learning Workflow

The pipeline utilizes historical patient clinical variables to train a classifier to predict risk levels:
1. **Ingestion & Validation:** Load dataset containing lifestyle factors (Smoking, Diet, Obesity, Alcohol Use) and clinical inputs (BRCA Mutation, H. Pylori Infection, BRCA status, Calcium intake).
2. **Data Preprocessing:** Impute missing values, scale numeric columns, and perform one-hot encoding on categorical features using a pipeline serialization class.
3. **Class Imbalance Handling:** Apply Synthetic Minority Over-sampling Technique (SMOTE) to prevent majority-class bias.
4. **Model Tuning & Training:** Run hyperparameter tuning on Random Forest and XGBoost architectures using Optuna, searching across learning rate, depth, and regularization factors.
5. **Model Evaluation:** Produce classification reports (Accuracy, Recall, Precision, F1-Score), confusion matrix matrices, and compute SHAP/feature importance metrics.

---

## API Documentation

FastAPI automatically generates interactive Swagger API documentation when the backend runs.

### Endpoint Specifications

#### 1. System Health
* **URL:** `/api/health`
* **Method:** `GET`
* **Response:**
  ```json
  {
    "status": "ok",
    "version": "1.0.0"
  }
  ```

#### 2. Model Prediction
* **URL:** `/api/predict`
* **Method:** `POST`
* **Request Body:**
  ```json
  {
    "Age": 55,
    "Gender": 1,
    "Smoking": 7,
    "Alcohol_Use": 9,
    "Obesity": 8,
    "Family_History": 0,
    "Diet_Red_Meat": 4,
    "Diet_Salted_Processed": 6,
    "Fruit_Veg_Intake": 3,
    "Physical_Activity": 2,
    "Air_Pollution": 2,
    "Occupational_Hazards": 10,
    "BRCA_Mutation": 0,
    "H_Pylori_Infection": 0,
    "Calcium_Intake": 4,
    "BMI": 27.0,
    "Physical_Activity_Level": 6
  }
  ```
* **Response:**
  ```json
  {
    "prediction": "High",
    "confidence_score": 0.88,
    "contributing_factors": [
      {"factor": "Obesity", "impact": "High"},
      {"factor": "Smoking", "impact": "Medium"}
    ]
  }
  ```

---

## Local Development Setup

### Infrastructure Setup
Start the local PostgreSQL database using Docker:
```bash
docker compose up -d
```

### Backend Setup
1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI development server:
   ```bash
   uvicorn backend.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install NPM packages:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

---

## Future Improvements
- Integrate SHAP (SHapley Additive exPlanations) directly in the REST API response for advanced mathematical explainability.
- Add multi-tenant JWT-based database authentication.
- Implement CI/CD automated pipeline for running Optuna search automatically when dataset updates.
