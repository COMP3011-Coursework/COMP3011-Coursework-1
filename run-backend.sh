#!/usr/bin/env bash
set -e
docker compose up db -d
PYTHONPATH=backend uvicorn app.main:app --reload --reload-dir backend
