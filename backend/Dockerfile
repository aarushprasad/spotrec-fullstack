# Use official Python image as base
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code into container
COPY . .

# Expose port FastAPI uses
EXPOSE 8000

# Run the app with uvicorn (adjust main:app if your entry point differs)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

