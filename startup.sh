#!/bin/bash

# Install packages if not already installed
apt-get update && apt-get install -y ffmpeg fluidsynth

# Start your app
gunicorn main:app --bind 0.0.0.0:8000
