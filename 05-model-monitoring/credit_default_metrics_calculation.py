import time
import random
import logging
import pandas as pd
import psycopg
import joblib
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score

from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
rand = random.Random()

create_table_statement = """
drop table if exists credit_default_prediction_metrics;
create table credit_default_prediction_metrics(
    batch_id integer,
    prediction_drift float,
    num_drifted_columns integer,
    share_missing_values float,
    auc float
)
"""

# --- Load reference data (with prediction column already added earlier) ---
reference_data = pd.read_parquet("data/reference.parquet")

# --- Load model ---
with open("models/xgb_cred_pred_ref.bin", "rb") as f_in:
    dv, booster = joblib.load(f_in)

# --- Load validation data ---
X_val = pd.read_parquet("../processed_data/X_val.parquet")
y_val = np.loadtxt("../processed_data/y_val.txt").astype(int)

# Ensure alignment
assert len(reference_data) == len(y_val), "Mismatch between reference_data and y_val length"
assert len(X_val) == len(y_val), "Mismatch between X_val and y_val length"

reference_data["target"] = y_val
X_val["target"] = y_val

# --- Features ---
num_features = X_val.select_dtypes(include=["int64", "float64"]).columns.tolist()
cat_features = X_val.select_dtypes(include=["category", "object"]).columns.tolist()

column_mapping = ColumnMapping(
    prediction="prediction",
    numerical_features=num_features,
    categorical_features=cat_features,
    target="target"
)

report = Report(metrics=[
    ColumnDriftMetric(column_name="prediction"),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric()
])

def prep_db():
    with psycopg.connect("host=localhost port=5432 user=postgres password=example", autocommit=True) as conn:
        res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
        if len(res.fetchall()) == 0:
            conn.execute("create database test;")
        with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example") as conn:
            conn.execute(create_table_statement)
            
def calculate_metrics_postgresql(curr, batch_id, current_data):
    # --- Handle missing values ---
    current_data[num_features] = current_data[num_features].fillna(0)
    for col in cat_features:
        current_data[col] = current_data[col].astype(str).fillna("missing")

    # --- Dict conversion for DictVectorizer ---
    records = current_data[num_features + cat_features].to_dict(orient="records")
    X_transformed = dv.transform(records)

    # --- Predict probabilities using Booster ---
    dmat = xgb.DMatrix(X_transformed)
    proba = booster.predict(dmat)
    
    # --- Add predictions ---
    current_data["prediction_proba"] = proba
    current_data["prediction"] = (proba >= 0.5).astype(int)

    # --- Compute AUC if target exists ---
    auc = None
    if "target" in current_data.columns:
        try:
            auc = round(roc_auc_score(current_data["target"], proba), 3)
        except ValueError:
            auc = None  # In case target is constant in the batch

    # --- Align reference_data schema ---
    reference_aligned = reference_data.copy()
    if "prediction" not in reference_aligned.columns:
        # Add predictions for reference_data if missing
        ref_records = reference_aligned[num_features + cat_features].to_dict(orient="records")
        X_ref = dv.transform(ref_records)
        ref_proba = booster.predict(xgb.DMatrix(X_ref))
        reference_aligned["prediction"] = ref_proba
    if "target" not in reference_aligned.columns:
        reference_aligned["target"] = None  # dummy column

    # --- Run Evidently report ---
    report.run(
        reference_data=reference_aligned,
        current_data=current_data,
        column_mapping=column_mapping
    )
    result = report.as_dict()

    prediction_drift = result["metrics"][0]["result"]["drift_score"]
    num_drifted_columns = result["metrics"][1]["result"]["number_of_drifted_columns"]
    share_missing_values = result["metrics"][2]["result"]["current"]["share_of_missing_values"]

    # --- Insert metrics into DB ---
    curr.execute(
        """
        INSERT INTO credit_default_prediction_metrics
        (batch_id, prediction_drift, num_drifted_columns, share_missing_values, auc)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (batch_id, prediction_drift, num_drifted_columns, share_missing_values, auc)
    )

    print(f"Metrics inserted for batch {batch_id} "
          f"| Prediction drift={prediction_drift:.4f}, Drifted cols={num_drifted_columns}, "
          f"Missing share={share_missing_values:.4f}, AUC={auc if auc is not None else 'N/A'}")


def batch_monitoring_backfill():
    prep_db()
    last_send = time.time() - SEND_TIMEOUT

    chunk_size = 2000  # rows per batch
    with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example", autocommit=True) as conn:
        for batch_id, start_idx in enumerate(range(0, len(X_val), chunk_size)):
            end_idx = start_idx + chunk_size
            current_data = X_val.iloc[start_idx:end_idx].copy()

            with conn.cursor() as curr:
                try:
                    calculate_metrics_postgresql(curr, batch_id, current_data)
                except Exception as e:
                    logging.error("Failed to process batch %s: %s", batch_id, str(e))
                    continue  # Skip this batch and continue with next

            new_send = time.time()
            seconds_elapsed = new_send - last_send
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            last_send = new_send
            logging.info("Batch %s processed", batch_id)

if __name__ == "__main__":
    batch_monitoring_backfill()