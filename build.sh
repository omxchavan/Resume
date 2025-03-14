#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy model if needed
python -m spacy download en_core_web_sm 