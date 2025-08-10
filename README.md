# Credit Default Risk – MLOps Project

## Overview
This project uses the **Home Credit Default Risk** dataset's `application_train.csv` file to build an **end-to-end Machine Learning pipeline** that predicts the probability of a client defaulting on a loan.

The dataset contains anonymized demographic, financial, and employment-related information for loan applicants. The goal is to integrate **machine learning with MLOps best practices**, ensuring reproducibility, scalability, and continuous improvement.

---

## Dataset
- **Source:** [Home Credit Default Risk – Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk)
- **File Used:** `application_train.csv`
- **Rows:** ~307,000
- **Columns:** ~122 features + target
- **Target:** `TARGET`
  - `0` → Loan repaid on time
  - `1` → Loan default

---

## MLOps Workflow

### 1. Data Ingestion & Preprocessing
- Load `application_train.csv`
- Handle missing values
- Encode categorical features
- Normalize/scale numerical features
- Split into training/validation/test sets

---

### 2. Model Training
- Train supervised ML models (Logistic Regression and XGBoost)
- Apply class imbalance handling (class weights)

---

### 3. Experiment Tracking
- **Tool:** MLflow
- Track:
  - Model type
  - Hyperparameters
  - Metrics (AUC, Accuracy)
  - Training time and resource usage
- Compare and select best-performing model

---

### 4. Pipeline Orchestration
- **Tool:** Prefect
- Automate:
  - Data ingestion
  - Feature engineering
  - Model training
  - Model evaluation
  - Model registration

---

### 5. Model Deployment
- Deploy best model as a **REST API** using Flask
- Containerize with Docker
- Expose endpoint for real-time scoring

---

### 6. Model Monitoring
- Track prediction drift and data drift
- Monitor latency, throughput, and error rates
- Retrain model when performance degradation is detected

---

## Best Practices Applied
- **Version Control:** Git for code & DVC for data
- **Reproducibility:** Fixed random seeds, environment files (`requirements.txt`)
- **Automation:** CI/CD pipelines for testing & deployment
- **Documentation:** Clear project structure and inline comments
- **Scalability:** Containerized workloads ready for Kubernetes deployment
- **Security:** Input validation & API authentication

---

## Project Goals
1. Build a high-performing credit default risk prediction model
2. Integrate with an **MLOps pipeline** for automation & reproducibility
3. Ensure **continuous monitoring and improvement** post-deployment

---

## References
- [Kaggle Competition](https://www.kaggle.com/competitions/home-credit-default-risk)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Prefect Documentation](https://docs.prefect.io/)

# PROJECT GUIDES

# Navigate to your project directory
cd ~/Projects/MLops_credit_default_risk_prediction/

# Make python3.8 the default for this project
1. which python3.8

2. echo "alias python='/usr/local/bin/python3.8'" > .env

3. if [ -f .env ]; then
    source .env
   fi

4. source ~/.zshrc

# Create a new virtual environment using Python 3.8
python -m credit-default-risk-pred-venv

source credit-default-risk-pred-venv/bin/activate

python -m pip install --upgrade pip

python -m pip install ipykernel

python -m ipykernel install --user --name=credit-default-risk-pred-venv --display-name "credit default risk prediction (credit-default-risk-pred-venv)"

python -m pip install -r requirements.txt

./credit-default-risk-pred-venv/bin/pip list
w
# Backend DB
#local sqlite db
python -m mlflow ui --backend-store-uri sqlite:///cred_risk_sqlite_mlflow.db --host 127.0.0.1 --port 8001

#aws s3
mlflow server --backend-store-uri sqlite:///cred_s3bucket_mlflow.db --default-artifact-root s3://mlflow-credit-default-risk-prediction-artifact-store-v2 --host 127.0.0.1 --port 8002

# pipeline arguments
- run pipeline with arguments
python credit_default_risk_pred_pipeline.py  --x_test_path ../processed_data/X_test.parquet --y_test_path ../processed_data/y_test.txt --run_id 2c2f5792316545ed84ddf88b09b072a9  --model_bundle_artifact_path xgb_credit_pred.bin

- run prefect orchestration locally
python credit_default_risk_pred_pipeline_orch.py

- prefect server start

# docker
docker-compose up --build