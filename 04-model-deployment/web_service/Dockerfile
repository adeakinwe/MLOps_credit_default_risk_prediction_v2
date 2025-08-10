FROM python:3.8-slim-bullseye

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements first for cache efficiency
COPY requirements.txt .

# Create virtualenv
RUN python -m venv /opt/credit-default-risk-pred-venv

# Install dependencies inside venv
RUN . /opt/credit-default-risk-pred-venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Make venv's binaries available system-wide
ENV PATH="/opt/credit-default-risk-pred-venv/bin:$PATH"

# Copy app files
COPY predict.py xgb_credit_pred.bin ./

# Expose port
EXPOSE 9696

# Run the app
ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9696", "predict:app"]