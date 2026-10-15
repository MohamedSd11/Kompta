#!/bin/bash
# macOS launcher (double-click in Finder); equivalent of StartKompta.bat.
cd "$(dirname "$0")" || exit 1

PY=$(command -v python3.13 || command -v python3.12 || command -v python3.11 || command -v python3.10 || command -v python3)
if [ ! -x ".venv/bin/python" ]; then
  "$PY" -c 'import sys; sys.exit(sys.version_info < (3, 10))' || { echo "Python 3.10+ requis."; read -r -p "Entrée pour fermer..."; exit 1; }
  "$PY" -m venv .venv && .venv/bin/python -m pip install -r requirements.txt || { read -r -p "Installation échouée. Entrée pour fermer..."; exit 1; }
fi

(sleep 2; open "http://127.0.0.1:${KOMPTA_PORT:-8000}/") &
exec .venv/bin/python run.py
