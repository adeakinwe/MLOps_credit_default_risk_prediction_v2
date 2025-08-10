import os
import pandas as pd
import numpy as np
import pickle
import mlflow
import xgboost as xgb
from sklearn.metrics import roc_auc_score
from mlflow.tracking import MlflowClient
from prefect import task, flow

# ------------------ Path Setup ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "../processed_data"))
MLFLOW_DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../cred_risk_sqlite_aws_mlflow.db"))

DEFAULT_X_TEST = os.path.join(DATA_DIR, "X_test.parquet")
DEFAULT_Y_TEST = os.path.join(DATA_DIR, "y_test.txt")

# ------------------ Prefect Tasks ------------------

@task
def load_test_data(x_test_path: str, y_test_path: str):
    """Load test data from files."""
    print(f"Loading test data from:\n  X: {x_test_path}\n  y: {y_test_path}")
    X_test = pd.read_parquet(x_test_path)
    y_test = np.loadtxt(y_test_path)
    return X_test, y_test


@task
def load_model_bundle(run_id: str, model_bundle_artifact_path: str):
    """Download and load model + vectorizer bundle from MLflow."""
    print(f"Setting MLflow tracking URI to: sqlite:///{MLFLOW_DB_PATH}")
    mlflow.set_tracking_uri(f"sqlite:///{MLFLOW_DB_PATH}")
    client = MlflowClient()

    print("Downloading model bundle from MLflow...")
    bundle_path = client.download_artifacts(run_id, model_bundle_artifact_path)

    with open(bundle_path, "rb") as f:
        model_bundle = pickle.load(f)

    return model_bundle, client


@task
def transform_data(X_test: pd.DataFrame, model_bundle: dict):
    """Transform test data using the vectorizer."""
    cat_cols = ['AGE_GROUP', 'YEARS_EMPLOYED_GROUP', 'PHONE_CHANGE_GROUP']
    num_cols = [
        'REGION_RATING_CLIENT_W_CITY', 'REGION_RATING_CLIENT',
        'EXT_SOURCE_3', 'EXT_SOURCE_2', 'EXT_SOURCE_1', 'FLOORSMAX_AVG'
    ]
    dv = model_bundle["vectorizer"]
    X_test_transformed = dv.transform(
        X_test[cat_cols + num_cols].to_dict(orient="records")
    )
    return X_test_transformed


@task
def evaluate_model(X_test_transformed, y_test, model_bundle: dict):
    """Run predictions and calculate AUC."""
    print("Making predictions...")
    model = model_bundle["model"]
    dtest = xgb.DMatrix(X_test_transformed)
    y_pred_proba = model.predict(dtest)

    auc = roc_auc_score(y_test, y_pred_proba)
    print(f"Test AUC: {auc:.4f}")
    return auc


@task
def log_metrics(client: MlflowClient, run_id: str, auc: float):
    """Log metrics to MLflow."""
    print("Logging test metrics to MLflow...")
    client.log_metric(run_id, "test_auc_prefect", auc)


# ------------------ Prefect Flow ------------------

@flow(name="MLflow Model Evaluation Pipeline")
def model_evaluation_pipeline(
    x_test_path: str = DEFAULT_X_TEST,
    y_test_path: str = DEFAULT_Y_TEST,
    run_id: str = "fe69b7b9817240789feb57c59ff31cc5",
    model_bundle_artifact_path: str = "xgb_credit_pred.bin"
):
    X_test, y_test = load_test_data(x_test_path, y_test_path)
    model_bundle, client = load_model_bundle(run_id, model_bundle_artifact_path)
    X_test_transformed = transform_data(X_test, model_bundle)
    auc = evaluate_model(X_test_transformed, y_test, model_bundle)
    log_metrics(client, run_id, auc)


# ------------------ Deployment Setup ------------------
if __name__ == "__main__":
    # Local run
    model_evaluation_pipeline()