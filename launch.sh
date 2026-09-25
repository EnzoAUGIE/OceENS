#!/bin/bash

cd /home/mde-admin/OceENS

if [ ! -d .venv ]; then
	echo ".venv not found. Installing"
	uv sync --locked
fi

if [ $(ps -aux | grep -E "bin/oceens( |$)" | wc -l) -gt 1 ]; then
	echo "Website already launched"
else

	echo "Launching Website with screen"
	screen -d -m bash -c "PYTHONUNBUFFERED=1 .venv/bin/oceens 2> >(tee -a app.error) | tee -a app.log"
fi

if [ $(ps -aux | grep "bin/oceens-summaries" | wc -l) -gt 1 ]; then
	echo "Summaries generator already launched"
else

	echo "Launching Summaries generator with screen"
	screen -d -m bash -c "PYTHONUNBUFFERED=1 .venv/bin/oceens-summaries 2> >(tee -a summaries.error) | tee -a summaries.log"
fi




