#!/bin/bash

SESSIONNAME="uofthacks12-backend"
# Check if the session exists
tmux has-session -t $SESSIONNAME 2>/dev/null
source .venv/bin/activate
pip install -r requirements.txt
uvicorn index:app --host 0.0.0.0 --port 8000 --reload
#uvicorn index:app --reload --port 8000                                                                                                                  
