#!/usr/bin/env bash
# Run checks in the WSL-accessible Windows project venv
VENV_PY="/mnt/c/Users/Windows 11/whatsapp_scheduler/.venv/bin/python"

echo "Using venv python: $VENV_PY"
if [ ! -x "$VENV_PY" ]; then
  echo "ERROR: venv python not found or not executable: $VENV_PY"
  exit 2
fi

echo "--- venv python & version ---"
"$VENV_PY" -c 'import sys, platform; print("exe:", sys.executable); print("pyver:", platform.python_version())'

echo "--- pip show twilio ---"
"$VENV_PY" -m pip show twilio || echo "twilio: not installed"

echo "--- pip show python-dotenv ---"
"$VENV_PY" -m pip show python-dotenv || echo "python-dotenv: not installed"

echo "--- import twilio test ---"
"$VENV_PY" -c 'import twilio; print("twilio OK", twilio.__version__)' 2>/dev/null || echo "twilio import: FAILED"

echo "--- import dotenv test ---"
"$VENV_PY" -c 'from dotenv import load_dotenv; print("dotenv OK")' 2>/dev/null || echo "dotenv import: FAILED"

echo "--- pip list (first 40) ---"
"$VENV_PY" -m pip list --format=columns | sed -n '1,40p'
#!/bin/bash

VENV_PY="/mnt/c/Users/Windows 11/whatsapp_scheduler/.venv/bin/python"

echo "--- venv python & version ---"
"$VENV_PY" -c 'import sys, platform; print("exe:", sys.executable); print("pyver:", platform.python_version())'

echo "--- pip show twilio ---"
"$VENV_PY" -m pip show twilio || echo "twilio: not installed"

echo "--- pip show python-dotenv ---"
"$VENV_PY" -m pip show python-dotenv || echo "python-dotenv: not installed"

echo "--- import twilio test ---"
"$VENV_PY" -c 'import twilio; print("twilio OK", twilio.__version__)' 2>/dev/null || echo "twilio import: FAILED"

echo "--- import dotenv test ---"
"$VENV_PY" -c 'from dotenv import load_dotenv; print("dotenv OK")' 2>/dev/null || echo "dotenv import: FAILED"
