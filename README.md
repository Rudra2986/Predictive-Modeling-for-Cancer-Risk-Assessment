# OncoRisk AI — Predictive Modeling for Cancer Risk Assessment

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg?style=flat&logo=next.js)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-supported-blue.svg?style=flat&logo=docker)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg?style=flat&logo=postgresql)](https://www.postgresql.org/)

OncoRisk AI is a production-grade healthcare application focused on predictive modeling for cancer risk assessment. It processes demographic, lifestyle, and health-related clinical patient profiles to predict cancer risk levels (Low, Medium, High) along with confidence scores and explainable model metrics.

This repository demonstrates the transition of a typical machine learning model from a Jupyter Notebook experiment into a fully realized production system. The platform handles real-world software engineering challenges including database persistence, secure authentication, role-based access control (RBAC), self-healing ML pipelines, and active containerized deployments.

---

## System Architecture

The platform is designed around a decoupled client-server architecture:

```
                                 +--------------------------------+
                                 |         User Browser           |
                                 +---------------+----------------+
                                                 | (HTTPS)
                                                 v
                                 +---------------+----------------+
                                 |      Nginx Reverse Proxy       |
                                 +---------------+----------------+
                                                 |
                         +-----------------------+-----------------------+
                         | (Static Files / SSR)                          | (API Requests)
                         v                                               v
         +---------------+----------------+              +---------------+----------------+
         |    Next.js Web Frontend        |              |      FastAPI REST API          |
         |    (Vercel or Container)       |              |  (Render / Docker / Python 11) |
         +--------------------------------+              +-------+---------------+--------+
                                                                 |               |
                                                      SQLAlchemy |               | (joblib, shap)
                                                             ORM |               v
                                                                 |        +------+--------+
                                                                 v        | ML Artifacts  |
                                                +----------------+----+   +---------------+
                                                | PostgreSQL Database |
                                                +---------------------+
```

---

## Core Features

- **Asynchronous Predictions**: Predictive risk inferences using Random Forest and XGBoost ensemble model pipelines.
- **Explainable AI (SHAP)**: Dynamic mathematical explanation using SHAP (SHapley Additive exPlanations) values to identify risk drivers and protective factors per patient profile, with a static fallback rule-based system.
- **Conversational AI Assistant (Chatbot)**: A patient assistant allowing conversational query of risk assessment parameters, explanation breakdown, platform help, and health guidance with full context history, safety guardrails, and caching support.
- **Source Citations & Recommendations**: Chatbot responses include medical citations and actionable recommendations based on patient classification.
- **Feedback Loop**: Users can submit votes (HELPFUL/NOT_HELPFUL) on chatbot responses to persist user feedback in the database.
- **Self-Healing ML Infrastructure**: Self-healing server startup that automatically runs a fast hyperparameter tuning search (n_trials=5) and trains compatible models if joblib files are missing or serialized with incompatible dependencies.
- **Live Retraining Engine**: Admin-controlled Optuna optimization dashboard to retrain models and select the best model based on weighted F1 metrics.
- **Robust Security Model**: Password hashing using `bcrypt`, stateless `JWT` tokens for authorization, and strict database validations.
- **Active Health Checks**: Active checks querying the SQL engine, verification of joblib artifact states, and explainer capability checks.
- **Persistent Audit Logging**: Relational storage of assessment queries linked to optional patient users to track history and risk trends.

---

## Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Frontend** | Next.js 14, React 18, Recharts, Framer Motion | App Router architecture, responsive charts, and fluid user interactions. |
| **Backend** | FastAPI, Uvicorn, Pydantic v2 | High-performance asynchronous REST API with strict request validation. |
| **Database** | PostgreSQL 15, SQLAlchemy, Alembic | Relational database schema with declarative models and migration histories. |
| **Machine Learning** | Scikit-learn, XGBoost, SMOTE, Optuna, SHAP | Preprocessing pipeline, ensemble classifiers, imbalance handling, hyperparameter search, and explainability. |
| **DevOps** | Docker, Nginx, docker-compose | Orchestrated local environment and containerized multi-stage builds. |

---

## Machine Learning Pipeline

The machine learning workflow processes demographic and clinical variables to execute prediction:

```
  Raw CSV Data Ingestion
           │
           ▼
  Data Cleaning & Split (80/20)
           │
           ▼
  Feature Processing (Pipeline: Numerical Scaling + Categorical One-Hot Encoding)
           │
           ▼
  Class Imbalance Handling (SMOTE Over-sampling)
           │
           ▼
  Hyperparameter Optimization (Optuna study over RF & XGBoost classifiers)
           │
           ▼
  Model Evaluation (Metrics: F1, Accuracy, Classification Report, Confusion Matrix)
           │
           ▼
  Model Selection (Select winner between Logistic Regression, RF, XGBoost)
           │
           ▼
  Artifact Serialization (best_model.joblib + preprocessor.joblib + metrics.json)
```

### ML Engineering Highlights
- **SMOTE Balancing**: Implements Synthetic Minority Over-sampling Technique to handle severe class imbalance in cancer occurrences without introducing synthetic bias.
- **Optuna Hyperparameter Tuning**: Automatically optimizes learning rate, estimators, depth, and regularization factors on XGBoost and Random Forest.
- **SHAP Explainability**: Uses TreeExplainer to calculate exact game-theoretic contributions of lifestyle behaviors (e.g. smoking index, processed food diet) and clinical flags (e.g. BRCA mutation) to generate a customized narrative explaining predictions.
- **Self-Healing Recovery**: If the Docker backend detects incompatible Python serialization (such as `numpy._core` version mismatches from local environment differences), the startup sequence automatically retrains a fresh model in 5 trials to avoid Render boot crashes.

---

## Security & Reliability Highlights

- **Stateless JWT Authorization**: Signed JSON Web Tokens manage authorization with expiration guards.
- **Role-Based Access Control (RBAC)**: Prediction APIs are open to guests and registered users, but admin-only endpoints (`/api/admin/retrain`) require administrator-promoted status database checks.
- **Production Secret Validation**: Startup validators throw errors in production mode if the backend detects default passwords or short development secret keys.
- **Graceful Degradation**: If model loading fails and retraining is blocked (e.g. if the raw dataset file is missing), the backend starts up successfully and returns a custom `503 Service Unavailable` error for predictions instead of crashing the process or returning generic `500 Internal Server Error` failures.

---

## Repository Structure

```
OncoRisk-AI/
│
├── frontend/             # Next.js Web Dashboard
│   ├── app/              # App Router Pages (Chat Assistant, Dashboard, History, etc.)
│   ├── components/       # Reusable UI Components (Navbar, charts)
│   ├── animations/       # Framer Motion Configs
│   ├── charts/           # Recharts Visualizations
│   ├── public/           # Static Assets
│   └── styles/           # Global Styling
│
├── backend/              # FastAPI Application
│   ├── api/              # Route Handlers (auth, predict, predictions, admin, chatbot)
│   ├── models/           # SQLAlchemy DB Models (user, chat message/session/feedback, prediction log)
│   ├── ml/               # Model Inference, Training & Saved Pipelines
│   ├── database/         # Session Configuration & Alembic Migrations
│   ├── services/         # Business Logic Layer (AI, chatbot, caching, guardrails, prediction, etc.)
│   ├── utils/            # Shared Helpers (Logging, Security configs)
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

## API Documentation

FastAPI exposes interactive Swagger documentation at `/docs` when the server is running.

| Endpoint | Method | Authentication | Purpose |
|---|---|---|---|
| `/api/auth/register` | `POST` | None | Register a new patient account (with strict password checks). |
| `/api/auth/login` | `POST` | None | Authenticate patient credentials and return a stateless JWT. |
| `/api/auth/me` | `GET` | User JWT | Fetch the current logged-in user profile attributes. |
| `/api/predict` | `POST` | Optional JWT | Process patient inputs and return cancer risk level + SHAP explainability. |
| `/api/predictions/history` | `GET` | User JWT | Retrieve historical assessment submissions log for the authenticated user. |
| `/api/predictions/analytics` | `GET` | Admin JWT | Retrieve aggregate metrics, risk distribution summaries, and trends. |
| `/api/admin/retrain` | `POST` | Admin JWT | Trigger an Optuna hyperparameter optimization run in the background. |
| `/api/admin/retrain/status` | `GET` | Admin JWT | Stream status logs and metrics of the current retraining background thread. |
| `/api/health` | `GET` | None | Check database connection status, ML model loaded status, and explainer capacity. |
| `/api/chatbot/message` | `POST` | User JWT | Post a user query to the conversational assistant (with context & guardrails). |
| `/api/chatbot/sessions` | `GET` | User JWT | List active chat sessions for the logged-in user. |
| `/api/chatbot/sessions` | `POST` | User JWT | Create a new chat session. |
| `/api/chatbot/sessions/{session_uuid}/messages` | `GET` | User JWT | Load historical messages in a session. |
| `/api/chatbot/sessions/{session_uuid}` | `DELETE` | User JWT | Soft delete a chat session. |
| `/api/chatbot/feedback` | `POST` | User JWT | Store or update user feedback (HELPFUL/NOT_HELPFUL) for a message. |
| `/api/chatbot/clear` | `POST` | User JWT | Clear the active in-memory conversation context. |

---

## Deployment Architecture

The production environment deployment is automated:

```
  [Developer Commit]
         │
         ├──► [Vercel Deployment] ──► Next.js Frontend Live
         │
         └──► [GitHub Repository]
                    │
                    ▼ (Trigger Webhook)
              [Render Cloud]
                    │
            (Build Phase: Dockerfile)
                    │
                    ├──► Ingest Base Image (python:3.11-slim)
                    ├──► Install Apt Packages & requirements.txt
                    ├──► Copy Backend & Alembic Modules
                    │
            (Release Phase: Startup Script)
                    │
                    ├──► Run Alembic Migrations (upgrade head)
                    ├──► Seed Admin User in PostgreSQL
                    ├──► Startup Uvicorn Server (backend.main:app)
                    │
                    ▼ (Self-Healing Check)
              Check joblib artifacts.
              If missing/invalid: run startup retraining (n_trials=5).
              Reload and serve predictions.
```

---

## Local Development Setup

### System Prerequisites
Ensure you have the following installed:
- Python 3.11
- Node.js (v18+)
- Docker Desktop

### 1. Database Setup
Start the local PostgreSQL database:
```bash
docker compose up -d
```

### 2. Backend API Setup
1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate # On Unix: source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
4. Run migrations and seed default administrative user:
   ```bash
   alembic upgrade head
   python backend/database/seed_admin.py
   ```
5. Run the FastAPI development server:
   ```bash
   uvicorn backend.main:app --reload
   ```

### 3. Frontend Dashboard Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Copy environment configuration:
   ```bash
   cp .env.example .env.local
   ```
4. Start the Next.js development server:
   ```bash
   npm run dev
   ```

### 4. Running Integration Tests
To run the automated verification scripts locally:
```bash
# Run backend API integration tests
.venv\Scripts\python backend\tests\test_api.py

# Run conversational assistant (chatbot) integration tests
.venv\Scripts\python backend\tests\test_chatbot.py

# Or run the entire test suite using pytest
pip install pytest pytest-cov
pytest backend/tests/
```

<details>
<summary><b>Show Environment Variables Configuration Details</b></summary>

Modify these settings inside `.env` for customized deployments:

- `DATABASE_URL`: PostgreSQL connection string (falls back to SQLite `sqlite:///oncorisk.db` if unavailable).
- `SECRET_KEY`: Secret string for cryptographic hashing of JWT.
- `ADMIN_EMAIL`: Default administrator email for retraining operations.
- `ADMIN_PASSWORD`: Default administrator password.
- `BACKEND_CORS_ORIGINS`: Allowed origins (e.g. `["http://localhost:3000"]`).
</details>

---

## Production Deployment

### Docker Deployment
The backend Docker configuration builds a lightweight image using `python:3.11-slim`:
```bash
docker build -t oncorisk-backend -f backend/Dockerfile .
```

To execute a local production multi-container orchestration, use the configuration in `deployment/`:
```bash
docker compose -f deployment/docker-compose.prod.yml up --build -d
```

### Render (Backend) Deployment
1. Create a Web Service on Render and link the GitHub repository.
2. Select **Docker** environment.
3. Configure the environment variables (`DATABASE_URL`, `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`).
4. Render builds the Dockerfile, executes the release migrations command, performs self-healing model setups, and exposes port `8000`.

### Vercel (Frontend) Deployment
1. Link your frontend repository subdirectory to Vercel.
2. Configure `NEXT_PUBLIC_API_URL` environment variable to point to your live backend endpoint.
3. Vercel builds the static bundle and hosts serverless Next.js functions.

---

## UI Preview Placeholders

Below are design frameworks for the primary screens:

### Patient Assessment Dashboard
```
+-----------------------------------------------------------------------------------+
|  OncoRisk AI Dashboard                       [Guest Profile] [Log In / Register]  |
+-----------------------------------------------------------------------------------+
|  Enter Patient Information:                                                        |
|  Age: [ 55 ]          Gender: (o) Male  ( ) Female                                 |
|  Smoking Habits (0-10):   ======[7]========                                        |
|  Alcohol Use (0-10):      ========[9]======                                        |
|  Obesity Level (0-10):    ========[8]======                                        |
|  Family History:          [ ] Checked                                              |
|  Diet red meat (0-10):    ====[4]==========                                        |
|  BRCA Mutation:           [ ] Present                                              |
|                                                                                   |
|                                [ Assess Cancer Risk ]                             |
+-----------------------------------------------------------------------------------+
```

### Clinical Assessment Risk Report
```
+-----------------------------------------------------------------------------------+
|  Assessment Results: HIGH RISK (Confidence: 88%)                                  |
+-----------------------------------------------------------------------------------+
|  Explanation Narrative:                                                           |
|  A high cancer risk score has been generated, heavily influenced by elevated      |
|  lifestyle behaviors and clinical risk markers.                                   |
|                                                                                   |
|  Contributing Risk Factors (SHAP Contributions):                                  |
|  - Obesity Profile (High Impact, +0.22 SHAP)                                      |
|  - Smoking Habits (Medium Impact, +0.14 SHAP)                                     |
|  - Processed Food Diet (Medium Impact, +0.09 SHAP)                                |
+-----------------------------------------------------------------------------------+
```

### Chat Assistant (Conversational AI)
```
+-----------------------------------------------------------------------------------+
|  OncoRisk AI Chat Assistant                                    [ID: 1] [ Logout ] |
+-----------------------------------------------------------------------------------+
|  [New Chat Session]       |  Chat Assistant                                       |
|                           |  Discuss clinical variables and lifestyle choices     |
|  Recent Conversations     |  +-------------------------------------------------+  |
|  - General Health...      |  | OncoRisk Advisor [Educational Guidance]         |  |
|  - Lung Cancer Overview   |  | What lifestyle improvements should I make?      |  |
|                           |  |                                                 |  |
|                           |  | - Increase physical activity frequency          |  |
|                           |  | - Reduce consumption of processed foods         |  |
|                           |  |                                                 |  |
|                           |  | Sources: [lifestyle] [prevention]               |  |
|                           |  | [Thumbs Up] [Thumbs Down]                       |  |
|                           |  +-------------------------------------------------+  |
|                           |                                                       |
|                           |  [ Type your question here...                  ] [Send] |
+-----------------------------------------------------------------------------------+
```

---

## Future Improvements

- **Interactive SHAP Plots**: Embed dynamic, interactive force plots and summary plots directly in the Next.js frontend using web-compatible SHAP visualization libraries.
- **Model Registry Integration**: Connect the backend to MLflow or a custom model registry for artifact versioning and historical evaluation tracking.
- **Enhanced Data Imputation Pipelines**: Upgrade from basic imputers to sophisticated predictive model-based imputation (e.g. IterativeImputer) for handling incomplete clinical profiles.
- **OAuth2 / Social Authentication Integration**: Support federated identity providers (such as Google or Microsoft Health) for patient registrations.

---

## Reflection: What I Learned

Throughout building and debugging this deployment framework, I gained solid engineering insights:
- **ML Dependency Fragility**: Encountering the `numpy._core` loading error highlighted that minor package changes between training and production environments will easily crash machine learning models. I resolved this by pinning stable numpy/shap pairs and writing self-healing startup routines.
- **Self-Healing Design**: I learned the importance of designing services that recover gracefully from state corruption. Running a fast 5-trial recovery retraining sequence on boot ensures the API goes live regardless of missing or corrupted assets.
- **Docker Production Isolations**: Utilizing multi-stage Docker builds and environment verification locks dependencies down and isolates code, simplifying continuous delivery on environments like Render.
- **Asynchronous Architecture**: Coordinating foreground prediction APIs alongside long-running Optuna tuning threads with `BackgroundTasks` taught me how to manage computation budgets inside thin, high-performance web frameworks.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
