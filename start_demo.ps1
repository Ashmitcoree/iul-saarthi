$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.10 or newer is required. Install Python, then run this script again."
}
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    throw "Ollama is required. Install it from https://ollama.com/download/windows, then run this script again."
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt

$modelList = ollama list 2>$null | Out-String
if ($modelList -notmatch "gemma4:e2b") {
    ollama pull gemma4:e2b
}

& ".venv\Scripts\python.exe" -m streamlit run app.py

