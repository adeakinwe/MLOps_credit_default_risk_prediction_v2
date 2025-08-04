import argparse
import pandas as pd
import numpy as np
import pickle
import mlflow
import mlflow.xgboost
from sklearn.metrics import accuracy_score, roc_auc_score
from mlflow.tracking import MlflowClient

def model_pipeline(x_test_path, y_test_path, run_id, model_artifact_path, preprocessor_artifact_path):
    # Load test data
    print("Loading test data...")
    X_test = pd.read_parquet(x_test_path)
    y_test = np.loadtxt(y_test_path)

    # Set tracking URI
    mlflow.set_tracking_uri("sqlite:///../02-experiment-tracking/cred_sqlite_mlflow.db")
    client = MlflowClient()

    # Download and load preprocessor
    print("Loading preprocessor from MLflow artifacts...")
    local_preprocessor_path = client.download_artifacts(run_id, preprocessor_artifact_path)
    with open(local_preprocessor_path, "rb") as f:
        dv = pickle.load(f)

    # Transform test data
    cat_cols = ['AGE_GROUP', 'YEARS_EMPLOYED_GROUP', 'PHONE_CHANGE_GROUP']
    num_cols = ['REGION_RATING_CLIENT_W_CITY', 'REGION_RATING_CLIENT',
                'EXT_SOURCE_3', 'EXT_SOURCE_2', 'EXT_SOURCE_1', 'FLOORSMAX_AVG']
    X_test_transformed = dv.transform(X_test[cat_cols + num_cols].to_dict(orient="records"))

    # Load model from MLflow
    print("Loading model from MLflow...")
    model_uri = f"runs:/{run_id}/{model_artifact_path}"
    model = mlflow.xgboost.load_model(model_uri)

    # Predictions
    print("Making predictions...")
    y_pred = model.predict(X_test_transformed)
    y_pred_proba = model.predict_proba(X_test_transformed)[:, 1]

    # Metrics
    auc = roc_auc_score(y_test, y_pred_proba)

    print(f"AUC: {auc:.4f}")

    # Log metrics back to the same run
    print("Logging metrics to MLflow...")
    client.log_metric(run_id, "test_auc", auc)

    print("Evaluation complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate a trained MLflow model on test data.")
    parser.add_argument("--x_test_path", required=True, help="Path to X_test parquet file")
    parser.add_argument("--y_test_path", required=True, help="Path to y_test text file")
    parser.add_argument("--run_id", required=True, help="MLflow run ID of the trained model")
    parser.add_argument("--model_artifact_path", required=True, help="Artifact path of the saved model in MLflow")
    parser.add_argument("--preprocessor_artifact_path", required=True, help="Artifact path of the saved DictVectorizer in MLflow")
    
    args = parser.parse_args()

    model_pipeline(
        x_test_path=args.x_test_path,
        y_test_path=args.y_test_path,
        run_id=args.run_id,
        model_artifact_path=args.model_artifact_path,
        preprocessor_artifact_path=args.preprocessor_artifact_path
    )
