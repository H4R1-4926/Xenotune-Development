# 🐍 Use official slim Python image
FROM python:3.11-slim

# 🔧 Install system-level dependencies needed for fluidsynth and audio processing
RUN apt-get update && apt-get install -y \
    fluidsynth \
    ffmpeg \
    libasound2 \
    libsndfile1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 📂 Set the working directory inside the container
WORKDIR /app

# 📦 Copy only requirements first (for better Docker caching)
COPY requirements.txt

# 🐍 Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 📁 Copy the FluidR3_GM folder separately for clarity
COPY FluidR3_GM /app/FluidR3_GM

# 📁 Copy the rest of the app code (excluding what's already copied)
COPY . .

# 🌐 Expose FastAPI's port
EXPOSE 8000

# 🚀 Run the FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
