from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Argus Web Starter")

class ScanRequest(BaseModel):
    target: str
    modules: List[str] = ["dns", "ports"]
    options: Optional[dict] = None

@app.get("/")
async def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Argus Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #0b1020;
                color: white;
                margin: 0;
                padding: 40px;
            }
            .container {
                max-width: 800px;
                margin: auto;
                background: #111827;
                border: 1px solid #23314d;
                border-radius: 14px;
                padding: 24px;
            }
            input, button {
                width: 100%;
                box-sizing: border-box;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #334155;
                margin-top: 10px;
            }
            input {
                background: #0f172a;
                color: white;
            }
            button {
                background: #2563eb;
                color: white;
                border: none;
                cursor: pointer;
                font-weight: bold;
            }
            .module-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 10px;
                margin-top: 12px;
                margin-bottom: 12px;
            }
            label {
                display: flex;
                align-items: center;
                gap: 8px;
                background: #1e293b;
                padding: 10px;
                border-radius: 8px;
            }
            pre {
                background: #020817;
                border: 1px solid #1e293b;
                border-radius: 10px;
                padding: 14px;
                white-space: pre-wrap;
                word-wrap: break-word;
                min-height: 180px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Argus Dashboard</h1>

            <label for="target">Target</label>
            <input id="target" value="example.com" />

            <div class="module-grid">
                <label><input type="checkbox" value="dns" checked> DNS</label>
                <label><input type="checkbox" value="ports" checked> Ports</label>
                <label><input type="checkbox" value="headers"> Headers</label>
                <label><input type="checkbox" value="ssl"> SSL</label>
                <label><input type="checkbox" value="subdomains"> Subdomains</label>
                <label><input type="checkbox" value="whois"> WHOIS</label>
            </div>

            <button onclick="runScan()">Run Scan</button>

            <h3>Results</h3>
            <pre id="resultBox">No scan run yet.</pre>
        </div>

        <script>
            async function runScan() {
                const target = document.getElementById('target').value.trim();
                if (!target) {
                    document.getElementById('resultBox').textContent = 'Please enter a target.';
                    return;
                }

                const selected = Array.from(document.querySelectorAll('input[type=checkbox]'))
                    .filter(cb => cb.checked)
                    .map(cb => cb.value);

                document.getElementById('resultBox').textContent = 'Running...';

                try {
                    const response = await fetch('/api/scan', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            target: target,
                            modules: selected,
                            options: {}
                        })
                    });

                    const data = await response.json();
                    document.getElementById('resultBox').textContent = JSON.stringify(data, null, 2);
                } catch (err) {
                    document.getElementById('resultBox').textContent = 'Error: ' + err.message;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "argus-web"}

@app.post("/api/scan")
async def run_scan(req: ScanRequest):
    return {
        "status": "queued",
        "target": req.target,
        "modules": req.modules,
        "summary": f"Scan queued for {req.target}",
        "results": {
            "notes": "This is the working website shell. Replace this section with your actual Argus recon modules later.",
            "selected_modules": req.modules,
            "target": req.target
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
