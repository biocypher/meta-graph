#!/bin/bash -c
#rm -rf /usr/app
#mkdir /usr/app
cd /usr/app
cp -r /src/* .
rm -rf data
poetry install
python3 create_knowledge_graph.py
#cp -r /usr/app/data/* /data/