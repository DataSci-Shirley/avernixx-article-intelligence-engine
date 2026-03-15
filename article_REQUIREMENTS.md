# 📋 Requirements & Installation Guide
### Avernixx Article Intelligence Engine — Setup Reference

> This document covers everything you need to install, configure, and run the Avernixx Article Intelligence Engine on a Windows machine.

---

## 🖥️ System Requirements

| Component | Minimum | Recommended |
|---|---|---|
| **OS** | Windows 10 | Windows 11 |
| **Python** | 3.10 | 3.13 |
| **RAM** | 8 GB | 16 GB (for local LLM) |
| **Storage** | 5 GB free | 10 GB free (for Llama3 model) |
| **Internet** | Required for initial install | Not required after setup (if using Ollama) |

---

## 📦 Full Dependencies

```
crewai
crewai_tools
langchain_community
litellm
streamlit
python-docx
pytz
openai              ← only needed if using OpenAI GPT mode
ollama              ← desktop application (only for local LLM mode)
jupyterlab          ← optional
```

---

## 🔧 Step-by-Step Installation

### Step 1 — Install CrewAI and Dependencies

Open **Windows PowerShell** and run:

```powershell
pip install -U crewai crewai_tools langchain_community
```

Verify:
```python
import crewai
print(f"CrewAI version {crewai.__version__} is ready!")
```

> ⚠️ If installing inside Jupyter, use `!pip install` and restart the kernel after.

---

### Step 2 — Install LiteLLM (Critical)

LiteLLM is the bridge that lets CrewAI talk to local LLMs like Ollama. Without it, only cloud providers work.

```powershell
pip install litellm
```

---

### Step 3 — Install Streamlit

```powershell
pip install streamlit
```

Verify:
```python
import streamlit
print("Streamlit is ready!")
```

---

### Step 4 — Install Additional Dependencies

```powershell
pip install python-docx pytz
```

- `python-docx` — enables Word (.docx) export
- `pytz` — Singapore 12-hour timestamps on all exports

---

### Step 5A — Local LLM Setup (Ollama/Llama3)

**Skip this step if you plan to use OpenAI GPT only.**

**Install Ollama:**

Method A (Recommended): Download from https://ollama.com/download and run the installer.

Method B (PowerShell one-liner):
```powershell
irm https://ollama.com/install.ps1 | iex
```

After installation, **close and reopen PowerShell**, then pull the model:
```powershell
ollama pull llama3
```

Verify Ollama is running — open browser and go to:
```
http://localhost:11434
```
You should see: `Ollama is running`

---

### Step 5B — OpenAI GPT Setup

**Skip this step if you plan to use Ollama only.**

Install the OpenAI package:
```powershell
pip install openai
```

Get your API key from: https://platform.openai.com/api-keys

You will enter this key directly in the Streamlit UI — no `.env` file needed.

> ⚠️ Never commit your OpenAI API key to GitHub. The UI input is password-masked and session-only.

---

## 🚀 Launching the Application

### The Two-Window Rule

| PowerShell Window | Purpose |
|---|---|
| **Window 1** | Keeps JupyterLab running (if using notebooks) — do not close |
| **Window 2** | Runs the Streamlit app |

> If you are not using JupyterLab, only Window 2 is needed.

---

### Launch Steps

**Navigate to the project folder:**
```powershell
cd "C:\Users\<your-username>\path\to\avernixx-article-intelligence-engine"
```

**Verify the file exists:**
```powershell
dir article_app.py
```

**Launch Streamlit:**
```powershell
python -m streamlit run article_app.py --server.port 8501
```

**Open in browser:**
```
http://localhost:8501
```

---

## 🎛️ Using the UI

Once the app is running:

1. **Select your LLM** — Local (Ollama) or Cloud (OpenAI)
2. **If OpenAI** — paste your API key and select your model (GPT-3.5 / GPT-4)
3. **Enter your topic** — be as specific or broad as you like
4. **Set your controls** — tone, audience, word count, SEO keywords
5. **Click Generate Article** — watch the live agent trace as they collaborate
6. **Download your article** — as `.md`, `.txt`, or `.docx` with timestamp

---

## 🔑 Key Concepts

| Concept | Explanation |
|---|---|
| **Ollama must be running** | Before clicking Generate in local mode, verify Ollama is active at `http://localhost:11434` |
| **OpenAI key is session-only** | The key is never saved — you re-enter it each session. This is by design for security. |
| **Port 8501** | Always use this port when launching via PowerShell |
| **Manual reset** | Use the Reset button to clear the session without restarting Streamlit |
| **Word count is a target** | The LLM will aim for your word count — actual output may vary by ±10-20% |

---

## 🐛 Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `File does not exist: article_app.py` | Wrong directory in PowerShell | `cd` to the correct project folder first |
| `Ollama not found` | Ollama not running | Open Ollama app or run `ollama serve` |
| `ModuleNotFoundError: crewai` | Package not installed | Run `pip install crewai` |
| `ModuleNotFoundError: litellm` | LiteLLM missing | Run `pip install litellm` |
| `AuthenticationError: OpenAI` | Invalid or missing API key | Re-enter a valid key in the UI |
| `localhost refused to connect` | Streamlit not running | Launch via PowerShell command above |
| App shows old version | Streamlit cached old file | `Ctrl+C`, replace file, restart |
| `KeyError: warnings` (Python 3.13) | Known Python 3.13 issue | Already patched in `article_app.py` |

---

## 📁 File Reference

| File | Description |
|---|---|
| `article_app.py` | Main Streamlit application |
| `README.md` | Project overview, architecture, and quick start |
| `REQUIREMENTS.md` | This file — full installation and troubleshooting guide |

---

## 📬 Support

For questions about this project or Avernixx's AI deployment services:

🌐 [www.avernixx.com](http://www.avernixx.com)

---

© 2026 Avernixx Pte. Ltd. All rights reserved.
