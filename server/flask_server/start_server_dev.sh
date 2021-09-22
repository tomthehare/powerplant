#!/bin/bash

#python3 -m venv venv
#source venv/bin/activate
#pip install -r requirements.txt

export FLASK_ENV=dev
export FLASK_APP=server

flask run --host 192.168.86.182
