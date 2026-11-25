# KrishiMitra AI – Multilingual Farmer Advisory Assistant

A medium-level MCA project demonstrating Generative AI, Large Language Models (LLMs), and Retrieval-Augmented Generation (RAG) for agricultural information access.

## Features
- Chat-style farmer interface built with Streamlit.
- Farmer context: state, crop, soil type and season.
- Local LLM integration through Ollama (default: `llama3.2:3b`).
- RAG retrieval over local agricultural knowledge files using TF-IDF.
- Upload PDF/TXT references and index them during the session.
- Language selection: English, Kannada, Hindi, Telugu, Tamil and Marathi.
- Reference passages displayed with responses.
- Transparent fallback when Ollama is unavailable.

## Requirements
- Windows 10/11
- Python 3.10 or later (Python 3.11 recommended)
- Internet connection for initial package/model downloads
- Ollama for LLM-generated responses (optional for testing the retrieval fallback)

## Run on Windows (VS Code terminal)

```powershell
cd F:\GEn_Ai_Project\KrishiMitra_AI
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run this once in the current terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Enable the LLM
1. Install Ollama from https://ollama.com/
2. Open a new terminal and run:
```powershell
ollama pull llama3.2:3b
```
3. Ensure Ollama is running. It normally listens at `http://localhost:11434`.

### Start the app
```powershell
streamlit run app.py
```
The browser should open at `http://localhost:8501`.

## How to use
1. Select language and farmer context in the sidebar.
2. Ask a crop or agriculture question in the chat tab.
3. Expand “Reference material” to inspect retrieved passages.
4. Upload trusted PDF/TXT agricultural documents in the document tab and index them.
5. For best answers, include crop stage, symptoms, district, recent irrigation and weather observations.

## Architecture
User query + farmer profile → TF-IDF retrieval → relevant passages → Ollama LLM prompt → generated response + references.

## Project structure
```text
KrishiMitra_AI/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── llm.py
│   ├── rag.py
│   └── utils.py
└── data/
    └── knowledge_base/
        ├── crop_basics.txt
        ├── government_support.txt
        └── advisory_workflow.txt
```

## Academic evaluation suggestions
- Retrieval Precision@K: manually label relevant passages for a small test-query set.
- Answer faithfulness: human score whether each factual claim is supported by retrieved passages.
- Answer relevance: 1–5 human rating.
- Response latency: measure retrieval and LLM response time separately.
- Language quality: native-speaker review for each supported language.
- Compare RAG answers against LLM-only answers using the same questions.

## Important safety note
This is an educational prototype, not a certified agricultural advisory service. Sample content is general and not a current official crop-protection recommendation. Verify pesticide selection, dosage, waiting periods, scheme eligibility and local agronomic decisions with official sources, the local KVK or a qualified agriculture professional. Never use AI output as the sole basis for chemical application.
