FROM public.ecr.aws/lambda/python:3.8

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements first (better caching for builds)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Ensure AWS config dir exists (for mounting ~/.aws when testing)
RUN mkdir -p /root/.aws

# Copy function code into the Lambda task root
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY model.py ${LAMBDA_TASK_ROOT}

# Copy test model folder (so LOCAL=true works even without a volume mount)
COPY integration_test/model ${LAMBDA_TASK_ROOT}/integration_test/model

# Default ENV values — can be overridden at runtime
ENV MODEL_LOCATION=${LAMBDA_TASK_ROOT}/integration_test/model
ENV LOCAL=false

# Lambda entrypoint
CMD [ "lambda_function.lambda_handler" ]