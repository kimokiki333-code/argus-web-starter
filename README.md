# Argus Recon

This project is the real backend version of the Argus dashboard.

## Features

- FastAPI backend
- target input form
- scan modules for DNS, ports, headers, SSL, and WHOIS
- real Python-based recon logic
- output shown directly in the browser UI

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open:

```text
http://localhost:8000
```

## Notes

This version is designed to run on a Python server and is intended to be deployed on a capable host like Render, Railway, or a VPS. It is no longer a static mock-only front-end.
