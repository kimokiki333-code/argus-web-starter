from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import socket
import ssl
import json
from datetime import datetime, timezone
from urllib import request as urllib_request
from urllib.error import URLError, HTTPError

import dns.resolver

app = FastAPI(title="Argus Recon")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_MODULES = {"dns", "ports", "headers", "ssl", "whois"}


class ScanRequest(BaseModel):
    target: str = Field(..., min_length=1)
    modules: List[str] = ["dns", "ports"]
    options: Optional[dict] = None


def normalize_target(value: str) -> str:
    target = value.strip().strip("/")
    if target.startswith(("http://", "https://")):
        target = target.split("://", 1)[1]
    if target.startswith("www."):
        return target
    return target


def resolve_host(target: str) -> str:
    try:
        return socket.gethostbyname(target)
    except Exception:
        return target


def run_dns_scan(target: str) -> Dict[str, Any]:
    records: Dict[str, Any] = {}
    for qtype in ["A", "AAAA", "CNAME", "TXT"]:
        try:
            answers = dns.resolver.resolve(target, qtype, lifetime=5)
            records[qtype] = [str(item) for item in answers]
        except Exception:
            records[qtype] = []

    try:
        ip = socket.gethostbyname(target)
    except Exception:
        ip = None

    return {
        "target": target,
        "resolved_ip": ip,
        "records": records,
    }


def run_port_scan(target: str, ports: Optional[List[int]] = None) -> Dict[str, Any]:
    host = target
    common_ports = ports or [21, 22, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 8080, 8443]
    results: Dict[str, Any] = {"target": host, "open_ports": []}

    try:
        host_ip = socket.gethostbyname(host)
        results["resolved_ip"] = host_ip
    except Exception:
        results["resolved_ip"] = host

    for port in common_ports:
        try:
            with socket.create_connection((host, port), timeout=1.5):
                results["open_ports"].append(port)
        except Exception:
            continue

    return results


def run_headers_scan(target: str) -> Dict[str, Any]:
    urls = [f"http://{target}", f"https://{target}"]
    response = {"target": target, "results": []}

    for url in urls:
        try:
            req = urllib_request.Request(url, method="HEAD")
            with urllib_request.urlopen(req, timeout=6) as r:
                header_map = dict(r.headers.items())
                response["results"].append(
                    {
                        "url": url,
                        "status": getattr(r, "status", None),
                        "headers": header_map,
                    }
                )
        except (HTTPError, URLError, ValueError):
            try:
                req = urllib_request.Request(url, method="GET")
                with urllib_request.urlopen(req, timeout=6) as r:
                    header_map = dict(r.headers.items())
                    response["results"].append(
                        {
                            "url": url,
                            "status": getattr(r, "status", None),
                            "headers": header_map,
                        }
                    )
            except Exception:
                continue

    return response


def run_ssl_scan(target: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"target": target, "certificate": None}

    try:
        context = ssl.create_default_context()
        with socket.create_connection((target, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=target) as ssock:
                cert = ssock.getpeercert()
                result["certificate"] = cert
                result["subject"] = cert.get("subject") if cert else None
                result["issuer"] = cert.get("issuer") if cert else None
                result["not_before"] = cert.get("notBefore") if cert else None
                result["not_after"] = cert.get("notAfter") if cert else None
    except Exception as exc:
        result["error"] = str(exc)

    return result


def run_whois_scan(target: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"target": target, "raw": None}
    try:
        with socket.create_connection(("whois.iana.org", 43), timeout=5) as sock:
            sock.sendall((target + "\r\n").encode("utf-8"))
            chunks = []
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data.decode("utf-8", errors="replace"))
            result["raw"] = "".join(chunks)[:2000]
    except Exception as exc:
        result["error"] = str(exc)
    return result


@app.get("/")
async def root():
    return FileResponse("index.html")


@app.get("/index.html")
async def index():
    return FileResponse("index.html")


@app.get("/styles.css")
async def css():
    return FileResponse("styles.css")


@app.get("/script.js")
async def js():
    return FileResponse("script.js")


@app.post("/api/scan")
async def scan(req: ScanRequest):
    target = normalize_target(req.target)
    selected_modules = [m.lower() for m in req.modules]
    unknown = [m for m in selected_modules if m not in ALLOWED_MODULES]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unsupported modules: {unknown}")

    if not target:
        raise HTTPException(status_code=400, detail="Target is required")

    results: Dict[str, Any] = {}

    if "dns" in selected_modules:
        results["dns"] = run_dns_scan(target)
    if "ports" in selected_modules:
        results["ports"] = run_port_scan(target)
    if "headers" in selected_modules:
        results["headers"] = run_headers_scan(target)
    if "ssl" in selected_modules:
        results["ssl"] = run_ssl_scan(target)
    if "whois" in selected_modules:
        results["whois"] = run_whois_scan(target)

    return {
        "status": "ok",
        "target": target,
        "modules": selected_modules,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
