# Python RAG Chatbot

A modular Python chatbot that combines **Retrieval-Augmented Generation (RAG)**, semantic search, and conversational NLP to provide context-aware responses from a collection of documents.

## Overview

This project explores how a chatbot can retrieve relevant information from a local knowledge base before generating a response. It separates document processing, embedding generation, retrieval, language-model interaction, and conversation routing into dedicated modules.

## Key Features

- **Retrieval-Augmented Generation (RAG):** Retrieves relevant document context to support answers.
- **Semantic Search:** Uses embeddings to find content based on meaning rather than exact keyword matches.
- **Document Processing:** Supports chunking, metadata handling, indexing, and retrieval workflows.
- **Conversational NLP:** Includes command parsing and small-talk handling.
- **Modular Architecture:** Separates RAG services, chatbot modules, and conversation memory.
- **Extensible Design:** Provides a foundation for adding knowledge sources and new chatbot capabilities.

## Architecture

```text
User Query
    |
    v
Flask Application
    |
    v
Chatbot NLP / Router
    |
    +----> Small Talk / Quiz / Course / Price Modules
    |
    v
RAG Retrieval Pipeline
    |
    +----> Query Embedding
    +----> Vector Search
    +----> Relevant Document Chunks
    |
    v
LLM Response Generation
    |
    v
Final Answer
```

The indexing workflow processes source documents, divides them into chunks, generates embeddings, and stores them in a vector database. At query time, the retrieval pipeline searches for relevant context that can be supplied to the language model.

## Technology Stack

- **Language:** Python
- **Web Framework:** Flask
- **Embeddings and NLP:** Sentence Transformers and supporting NLP libraries
- **Vector Database:** ChromaDB
- **Language Model:** Configured through the project's LLM service
- **Version Control:** Git and GitHub

## Project Structure

```text
Python-RAG-Chatbot/
├── app.py
├── chatbot_nlp.py
├── build_index.py
├── config.py
├── RAG_PIPELINE.md
├── requirements.txt
├── memory/
├── modules/
├── nlp/
├── rag_documents/
└── services/
```

- `app.py` — Flask application entry point.
- `chatbot_nlp.py` — Core chatbot NLP logic.
- `build_index.py` — Document indexing workflow.
- `modules/` — Chatbot routing and feature-specific modules.
- `nlp/` — Command parsing and NLP utilities.
- `memory/` — Conversation-memory functionality.
- `services/` — Chunking, embeddings, indexing, retrieval, vector storage, and LLM integration.
- `rag_documents/` — Sample documents used as knowledge sources.
- `RAG_PIPELINE.md` — Additional documentation about the RAG pipeline.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Sanabatool/Python-RAG-Chatbot.git
cd Python-RAG-Chatbot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file and configure the environment variables required by your application.

**Never commit `.env` or publish API keys, passwords, or other credentials.**

Check `config.py` and the LLM service to identify the exact environment-variable names required by your implementation.

### 5. Build the document index

Review `build_index.py` and `RAG_PIPELINE.md` to confirm the correct indexing command and any prerequisites before running the indexing workflow.

### 6. Run the application

```bash
python app.py
```

If Flask starts successfully, open the local address printed in your terminal.

## Future Improvements

- Evaluate retrieval quality and answer correctness using a documented test dataset.
- Add source attribution to retrieved answers.
- Improve handling of ambiguous queries and missing context.
- Measure retrieval latency and end-to-end response time.
- Expand the knowledge base and evaluate performance across different document types.

## Author

**Sana Batool**

GitHub: [@Sanabatool](https://github.com/Sanabatool)

---

*This project is developed for learning and experimentation with Retrieval-Augmented Generation, semantic retrieval, and modular chatbot architecture.*