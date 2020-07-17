#!/bin/bash


sudo apt-get install unixodbc unixodbc-dev graphviz libgraphviz-dev graphviz-dev pkg-config build-essential python3-dev gcc libpq-dev -y
pip install --upgrade pip
pip -r requirements.txt