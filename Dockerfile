FROM python:3.11-slim

WORKDIR /app

ARG PIP_INDEX_URL=https://pypi.org/simple

# Install production dependencies only
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy data files (for analysis page and training)
COPY data/ ./data/

# Copy pyproject.toml for any runtime config needs
COPY pyproject.toml .

# Ensure /app is on Python path so 'app' package is importable
ENV PYTHONPATH=/app

EXPOSE 8501

# Streamlit default: port 8501, bind to 0.0.0.0
CMD ["streamlit", "run", "app/main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
