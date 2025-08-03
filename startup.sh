#!/bin/bash

# Install packages if not already installed
apt-get update && apt-get install -y ffmpeg fluidsynth

# Start your app
uvicorn main:app --host 0.0.0.0 --port 10000
