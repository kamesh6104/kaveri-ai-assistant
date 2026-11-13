
# Kaveri Exports AI Assistant

## About

The Kaveri Exports AI Assistant is an AI-powered application designed to help sales heads and employees access business information efficiently. It consists of three main components: a SQL Assistant that answers questions using the sales database with read-only SQL queries, a Document Assistant (RAG) that retrieves answers from company policy documents with citations, and a Research Agent that searches external sources and generates research reports with source links. The system focuses on reliable, verifiable and secure answers.

## Setup

1. Create and activate a Python virtual environment:
   `python -m venv .venv`

2. Install dependencies:
   `pip install -r requirements.txt`

3. Copy `.env.example` to `.env` and configure your own API credentials. Never commit `.env`.

4. Place the sales CSV files inside `data/raw/`.

5. Run the database loader:
   `python load_db.py`

## Project layout

| Folder | What is in it |
|---|---|
| `src/` | Application source code and AI assistant modules |
| `prompts/` | System prompts and AI instructions |
| `eval/` | Evaluation datasets and evaluation scripts |
| `docs/` | Business documentation and policy documents |
| `tests/` | Unit tests and integration tests |
| `data/` | Raw datasets, data dictionary and database-related files |
