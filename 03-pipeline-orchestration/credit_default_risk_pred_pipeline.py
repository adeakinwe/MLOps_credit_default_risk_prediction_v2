import argparse
import pandas as pd
import numpy as np
import pickle
import mlflow
import xgboost as xgb
from sklearn.metrics import roc_auc_score
from mlflow.tracking import MlflowClient

def evaluate_model(x_test_path, y_test_path, run_id, model_bundle_artifact_path):
    # Load test data
    print("Loading test data...")
    X_test = pd.read_parquet(x_test_path)
    y_test = np.loadtxt(y_test_path)

    # Set tracking URI
    mlflow.set_tracking_uri("sqlite:///../cred_risk_sqlite_aws_mlflow.db")
    client = MlflowClient()

    # Download and load model bundle
    print("Loading model + vectorizer bundle from MLflow...")
    bundle_path = client.download_artifacts(run_id, model_bundle_artifact_path)
    with open(bundle_path, "rb") as f:
        model_bundle = pickle.load(f)

    model = model_bundle["model"]
    dv = model_bundle["vectorizer"]

    # Transform test data
    cat_cols = ['AGE_GROUP', 'YEARS_EMPLOYED_GROUP', 'PHONE_CHANGE_GROUP']
    num_cols = ['REGION_RATING_CLIENT_W_CITY', 'REGION_RATING_CLIENT',
                'EXT_SOURCE_3', 'EXT_SOURCE_2', 'EXT_SOURCE_1', 'FLOORSMAX_AVG']
    X_test_transformed = dv.transform(X_test[cat_cols + num_cols].to_dict(orient="records"))

    # Predictions
    print("Making predictions...")

    dtest = xgb.DMatrix(X_test_transformed)
    y_pred_proba = model.predict(dtest)  # returns probabilities

    # Metrics
    auc = roc_auc_score(y_test, y_pred_proba)

    print(f"Test AUC: {auc:.4f}")

    # Log metrics back to MLflow
    print("Logging test metrics to MLflow...")
    client.log_metric(run_id, "test_auc", auc)

    print("Evaluation complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate an MLflow model bundle on test data.")
    parser.add_argument("--x_test_path", required=True, help="Path to X_test parquet file")
    parser.add_argument("--y_test_path", required=True, help="Path to y_test text file")
    parser.add_argument("--run_id", required=True, help="MLflow run ID of the trained model")
    parser.add_argument("--model_bundle_artifact_path", required=True, help="Artifact path of the pickled model bundle in MLflow (e.g., 'xgb_credit_pred.bin')")

    args = parser.parse_args()

    evaluate_model(
        x_test_path=args.x_test_path,
        y_test_path=args.y_test_path,
        run_id=args.run_id,
        model_bundle_artifact_path=args.model_bundle_artifact_path
    )
