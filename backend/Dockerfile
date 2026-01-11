FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY config/ ./config/
COPY database/ ./database/
COPY models/ ./models/
COPY services/ ./services/

# Create necessary directories
RUN mkdir -p uploads logs models

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]