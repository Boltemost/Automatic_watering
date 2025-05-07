#!/bin/bash
./pocketbase serve --http 0.0.0.0:8090 &
source ./venv/bin/activate
uvicorn main:server --host 0.0.0.0

