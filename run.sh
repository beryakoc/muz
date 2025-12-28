#!/bin/bash
# Helper script to run the Django server with virtual environment activated

cd "$(dirname "$0")"
source venv/bin/activate
python manage.py runserver


