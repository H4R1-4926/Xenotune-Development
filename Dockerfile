# Use official Python slim image
FROM python:3.11-slim

# Install system dependencies like fluidsynth and ffmpeg
RUN apt-get update && apt-get install -y \
    fluidsynth \
    ffmpeg \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy your code into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
