# Stage 1: Build layer dependencies
FROM public.ecr.aws/lambda/python:3.13 AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --target python

# Stage 2: Build runtime image
FROM public.ecr.aws/lambda/python:3.13

# Ensure Python knows to look inside /var/task/src
ENV PYTHONPATH="${PYTHONPATH}:/var/task/src"

# Copy dependencies from builder
COPY --from=builder /build/python /var/task/

# Copy source code and lambda handler
COPY lambda_handler.py lambda_handler.py
COPY src src/

# Final entrypoint
CMD ["lambda_handler.lambda_handler"]
