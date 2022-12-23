#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
source venv/bin/activate
python collect_all.py
