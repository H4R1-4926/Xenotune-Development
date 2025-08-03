#!/bin/bash

# Install packages if not already installed
sudo apt-get update && sudo apt-get install -y fluidsynth

# Start your app
uvicorn main:app --host 0.0.0.0 --port 10000
