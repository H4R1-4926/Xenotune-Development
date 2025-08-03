# Use official Python image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    fluidsynth \
    ffmpeg \
    libasound2 \
    libsndfile1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your code and requirements
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for FastAPI
EXPOSE 8000

# Start FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
