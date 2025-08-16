import time
import random
import logging
import pandas as pd
import psycopg
import joblib
import numpy as np
import pytz
import xgboost as xgb
from datetime import datetime
from sklearn.metrics import roc_auc_score

from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric

# --- Config ---
SEND_TIMEOUT = 10
DEFAULT_THRESHOLD = 0.5
DB_CONN_STR = "host=localhost port=5432 user=postgres password=example"
DB_NAME = "test"
TABLE_NAME = "credit_default_prediction_metrics"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
rand = random.Random()

# --- SQL schema ---
create_table_statement = f"""
drop table if exists {TABLE_NAME};
create table {TABLE_NAME}(
    batch_id integer,
    prediction_drift float,
    num_drifted_columns integer,
    share_missing_values float,
    auc float,
    date_time_created timestamp
)
"""

# --- Load reference data ---
reference_data = pd.read_parquet("data/reference.parquet")

# --- Load model ---
with open("models/xgb_cred_pred_ref.bin", "rb") as f_in:
    dv, booster = joblib.load(f_in)

# --- Load validation data ---
X_val = pd.read_parquet("../processed_data/X_val.parquet")
y_val = np.loadtxt("../processed_data/y_val.txt").astype(int)

assert len(X_val) == len(y_val), "Mismatch between X_val and y_val"
X_val["TARGET"] = y_val

# --- Features ---
num_features = X_val.select_dtypes(include=["int64", "float64"]).columns.tolist()
cat_features = X_val.select_dtypes(include=["category", "object"]).columns.tolist()

column_mapping = ColumnMapping(
    prediction="PREDICTION",
    numerical_features=num_features,
    categorical_features=cat_features,
    target="TARGET"
)

report = Report(metrics=[
    ColumnDriftMetric(column_name="PREDICTION"),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric()
])


# --- Database setup ---
def prep_db():
    with psycopg.connect(DB_CONN_STR, autocommit=True) as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'")
        if len(res.fetchall()) == 0:
            conn.execute(f"create database {DB_NAME};")
    with psycopg.connect(f"{DB_CONN_STR} dbname={DB_NAME}", autocommit=True) as conn:
        conn.execute(create_table_statement)


# --- Metrics calculation ---
def calculate_metrics_postgresql(curr, batch_id, current_data, threshold=DEFAULT_THRESHOLD):
    # Handle missing values
    current_data[num_features] = current_data[num_features].fillna(0)
    for col in cat_features:
        current_data[col] = current_data[col].astype(str).fillna("missing")

    # Transform
    records = current_data[num_features + cat_features].to_dict(orient="records")
    X_transformed = dv.transform(records)

    # Predict
    dmat = xgb.DMatrix(X_transformed)
    proba = booster.predict(dmat)

    # Predictions
    current_data["PREDICTION_PROB"] = proba
    current_data["PREDICTION"] = (proba >= threshold).astype(int)

    # Compute AUC
    auc = None
    if "TARGET" in current_data.columns:
        try:
            auc = round(roc_auc_score(current_data["TARGET"], proba), 3)
        except ValueError:
            auc = None

    # Ensure reference_data has aligned schema
    reference_aligned = reference_data.copy()
    if "PREDICTION_PROB" not in reference_aligned.columns:
        ref_records = reference_aligned[num_features + cat_features].to_dict(orient="records")
        X_ref = dv.transform(ref_records)
        ref_proba = booster.predict(xgb.DMatrix(X_ref))
        reference_aligned["PREDICTION_PROB"] = ref_proba
    if "TARGET" not in reference_aligned.columns:
        reference_aligned["TARGET"] = None

    # Run Evidently report
    report.run(reference_data=reference_aligned, current_data=current_data, column_mapping=column_mapping)
    result = report.as_dict()

    prediction_drift = result["metrics"][0]["result"]["drift_score"]
    num_drifted_columns = result["metrics"][1]["result"]["number_of_drifted_columns"]
    share_missing_values = result["metrics"][2]["result"]["current"]["share_of_missing_values"]

    # Insert metrics
    curr.execute(
        f"""
        INSERT INTO {TABLE_NAME}
        (batch_id, prediction_drift, num_drifted_columns, share_missing_values, auc, date_time_created)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (batch_id, prediction_drift, num_drifted_columns, share_missing_values, auc, datetime.now(pytz.timezone('Africa/Lagos')))
    )

    logging.info(
        f"Batch {batch_id} | Drift={prediction_drift:.4f}, DriftedCols={num_drifted_columns}, "
        f"Missing={share_missing_values:.4f}, AUC={auc if auc else 'N/A'}"
    )


# --- Monitoring loop ---
def batch_monitoring_backfill():
    prep_db()
    last_send = time.time() - SEND_TIMEOUT

    chunk_size = 2000
    with psycopg.connect(f"{DB_CONN_STR} dbname={DB_NAME}", autocommit=True) as conn:
        for batch_id, start_idx in enumerate(range(0, len(X_val), chunk_size)):
            end_idx = start_idx + chunk_size
            current_data = X_val.iloc[start_idx:end_idx].copy()

            with conn.cursor() as curr:
                try:
                    calculate_metrics_postgresql(curr, batch_id, current_data)
                except Exception as e:
                    logging.error("Failed to process batch %s: %s", batch_id, str(e))
                    continue

            # pacing
            new_send = time.time()
            seconds_elapsed = new_send - last_send
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            last_send = new_send


if __name__ == "__main__":
    batch_monitoring_backfill()