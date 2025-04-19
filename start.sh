#!/bin/bash
source ./venv/bin/activate
uvicorn main:server --reload --host 0.0.0.0
