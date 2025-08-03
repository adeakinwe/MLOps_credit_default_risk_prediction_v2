# Navigate to your project directory
cd ~/Projects/MLops_datatalks_project/

# Create a new virtual environment using Python 3.8
python3.8 -m credit-default-risk-venv

source credit-default-risk-venv/bin/activate

python -m pip install --upgrade pip

python -m pip install ipykernel

python -m ipykernel install --user --name=credit-default-risk-venv --display-name "credit default risk prediction (credit-default-risk-venv)"

./credit-default-risk-venv/bin/pip list

# Backend DB
python -m mlflow ui --backend-store-uri sqlite:///cred_sqlite_mlflow.db --host 127.0.0.1 --port 6001

#aws mlflow server --backend-store-uri sqlite:///mlflow3.db --default-artifact-root s3://mlflow-ride-duration21-prediction-artifact-store --host 127.0.0.1 --port 5003

# docker
docker-compose up --build