FROM python:3.13-slim

# Set work directory
WORKDIR /app/src

# Install dependencies
COPY SRC_for_docker/requirements.txt /app/src
RUN pip install --no-cache-dir -r requirements.txt

# Set Python path so it can find src modules
ENV PYTHONPATH=/app/src

# Copy source code
COPY SRC_for_docker/src/ /app/src

# Set entrypoint
CMD ["python", "scripts/update_consumption_data.py"]
