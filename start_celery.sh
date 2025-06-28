#!/bin/bash

# Start Celery worker for ALX Travel App
echo "Starting Celery worker..."

# Make sure Redis is running first
echo "Checking Redis connection..."
redis-cli ping

# Start Celery worker
celery -A alx_travel_app worker --loglevel=info
