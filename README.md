# Argus Web Starter

A minimal website-ready starter app for the Argus recon project.

## Run locally

1. Create a virtual environment:

```bash
python -m venv .venv
```

2. Activate it:

On Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the app:

```bash
python app.py
```

5. Open the app in your browser:

```text
http://localhost:8000
```

## What this includes

- FastAPI backend
- HTML dashboard UI
- Target input and module selection
- API endpoint for scanning requests
- Ready to be connected to your real Argus modules later

## Notes

This starter is a working web shell only. It does not yet call your actual recon scripts. The next step is to replace the `/api/scan` handler with real Argus module logic.
