# Software Architecture Recommender Agent

Software architects accumulate vast libraries of diagrams, white-papers, and Confluence pages from past projects.  
When a new initiative kicks off they often comb through this unstructured content manually to find reusable patterns—a slow and error-prone task.  
This repository shows how Large Language Models (LLMs) and agentic workflows can automate that research: it surfaces the closest-matching reference architectures and explains, in detail, how each one satisfies—or falls short of—the new project’s requirements.

---

## 1. Project Overview
This repo contains two main workflows:

| Module | Purpose |
|--------|---------|
| **scripts/**[`create_and_upload_index.py`](software-architecture-generator-agent/scripts/create_and_upload_index.py) | • Extract text + figures from PDF architecture white-papers<br>• Summarise every diagram with Azure OpenAI Vision<br>• Build vector embeddings and publish both images & metadata to Azure Cognitive Search + Blob Storage |
| **backend/** | FastAPI service that exposes a conversational **Intake Agent** which: <br>1. Collects user requirements<br>2. Runs hybrid semantic+vector search over the indexed diagrams<br>3. Uses RAG to explain how the closest architecture fits the use-case |

---

## 2. Key Features
* OCR + Figure extraction with Azure Document Intelligence and GPT-4o 
* GPT-4o to sumarize the extracted architecture diagrams

* Upload of diagram PNGs to Azure Blob Storage  
* Tool-calling chat agent that decides when to trigger search vs. keep asking follow-up questions  

---

## 3. Directory Structure
```
software-architecture-generator-agent/
├─ backend/          # FastAPI + agents
├─ scripts/          # one-off data-pipeline
├─ data/             # local cache (PDFs, split_pages/, figures/)
├─ requirements.txt
└─ README.md            # (this file)
```

---

## 4. Quick Start

### 4.1 Prerequisites
* Python 3.10+  
* Azure subscription with:
  * Azure AI Search
  * Azure Blob Storage
  * Azure OpenAI (GPT-4o + Embedding deployment)
  * Azure AI Document Intelligence (Layout model)

### 4.2 Installation
```powershell
# Windows (PowerShell)
> python -m venv .venv
> .\.venv\Scripts\activate
> pip install -r requirements.txt
```

### 4.3 Configuration
Store secrets as environment variables or in a `.env` file **never commit keys**.

| Variable | Description |
|----------|-------------|
| `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `Azure_OpenAI_Embedding_Deployment_Name` |
| `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_ADMIN_KEY`, `AZURE_SEARCH_INDEX` |
| `AZURE_STORAGE_ACCOUNT`, `AZURE_STORAGE_CONTAINER` |
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`, `AZURE_DOCUMENT_INTELLIGENCE_KEY` |
| `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` |

---

## 5. Building the Vector Index
```powershell
# Edit scripts/create_and_upload_index.py → fill <credentials> + input PDF
> python scripts\create_and_upload_index.py
```
The script will:
1. Split each PDF page & detect figure bounding boxes  
2. Export pages and diagrams to `data/figures/` & `data/split_pages/`  
3. Extract service lists & AI summaries  
4. Upload PNGs to Blob Storage  
5. Create / update the AI Search index and push json documents with embeddings  

---

## 6. Running the Intake-Agent API
```powershell
> cd backend
> uvicorn app:query_endpoint --reload  # dev
```
Call the endpoint programmatically:
```python
import requests, json
body = {
  "query": "I need a batch ingestion pipeline on Azure Data Lake (1 TB/day)…",
  "conversation_history": []
}
resp = requests.post("http://127.0.0.1:8000/query", json=body).json()
print(resp["assistant_response"])
```
Or run the interactive CLI:
```powershell
> python app.py
```

---

## 7. Testing
To add unit tests place files under `tests/` and run:
```powershell
> pytest
```

---

## 8. Troubleshooting
* `azure.core.exceptions.HttpResponseError`: check that your service principal has *Cognitive Search Data Contributor* & *Storage Blob Data Contributor* roles.  
* Empty search results – ensure embeddings dimensions match (3072 for `text-embedding-3-large`).  

---

## 9. Roadmap / TODO
- Streamline secrets via Azure Key Vault  
- Dockerfile & Bicep for one-click deploy
- Enhancement of the prompts used in the document cracking script for more accurate and detailed extraction of the architecture diagrams
- Web front-end with diagram preview
- Integrating the architecture recommender system with automation scripts so that the agent does not only find the closest architecture match but also triggers its build out. 

---

## 10. License
MIT (see [LICENSE](LICENSE)) – sample keys in the repo are **dummy values** and must be replaced.