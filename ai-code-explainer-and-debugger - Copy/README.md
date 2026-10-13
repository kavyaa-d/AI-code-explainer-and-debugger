# AI Code Explainer & Debugger

A small Flask starter app for explaining snippets and checking for basic bracket mismatches.

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. The current explainer is a placeholder; the debugger only checks basic bracket balance and is not a full parser. Add an AI provider to `explain_code` when you're ready.
