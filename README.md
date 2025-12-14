
# Earnest RCM – AI Coding Task

This repository contains my implementation of the Earnest RCM Independent Coding Task. The project implements a small Django-based API for ingesting medical charts, storing structured clinical notes, and assigning ICD-10 Category G (nervous system) codes using a vector similarity approach with LangChain and Chroma.


### Overview

At a high level, the system:

1. Defines a schema for storing medical charts as individual clinical notes

2. Parses a raw chart text file into structured note objects

3. Persists notes in a SQLite database using Django

4. Builds a local Chroma vector store from ICD-10 G-code descriptions

5. Assigns the most relevant ICD-10 code to each note via vector similarity search

6. Provides a test script that exercises the full API end-to-end

Repository Structure
```
ai-coding-mvp/
├── ai_coding_app/
│   ├── app/
│   │   ├── models.py        # Medical note data model
│   │   ├── views.py         # API endpoints
│   │   ├── urls.py          # Routing
│   │   └── vector_store.py  # Chroma + LangChain logic
│   ├── manage.py
│   └── db.sqlite3
├── data/
│   ├── medical_chart.txt
│   └── g_codes.csv
├── scripts/
│   └── test_api_script.py
├── taskfile.yaml
├── pyproject.toml
└── README.md
```

### Data Model

Charts are represented as collections of MedicalNote records rather than a separate chart table. Each note stores:

- chart_id
- note_id
- note_type
- content
- created_at

This design keeps ingestion simple and allows notes to be handled independently.

## API Endpoints

### GET /app/test-view/
- Sanity check endpoint provided by the starter code.

### GET /app/chart-schema/
- Returns the database schema used to store medical notes.

### POST /app/upload-chart/
- Ingests a structured chart payload and persists its notes.
- The endpoint is idempotent
- Re-uploading the same chart will not create duplicate notes

### GET /app/charts/
- Returns all stored medical notes.

### POST /app/code-chart/ 
- Assigns ICD-10 G-codes to each note in a specified chart.

## Behavior
1. Loads all notes for the given chart_id from SQLite
2. Queries a persisted Chroma vector store
3. Uses k = 1 similarity search per note
4. Returns one ICD-10 code and similarity score per note

## Vector Store & Coding Implemented using LangChain + Chroma
- ICD-10 G-code long descriptions are embedded using OpenAI’s text-embedding-3-large
- The Chroma vector store is persisted locally to avoid rebuilding embeddings on each run
- Coding uses a retrieval-only approach, as specified in the task

# Running the Application
## Requirements

- ### Python 3.11+

- ### OpenAI API key

   - Set the API key in your environment:
       ```
       export OPENAI_API_KEY="your_api_key_here"
       ```
## Start the API server
### Environment Setup

This project uses uv for Python dependency and virtual environment management.

To configure the local virtual environment and install all required dependencies, run:
```
uv sync
```

This will:

- Create a local virtual environment

- Install all dependencies defined in pyproject.toml

- Lock exact package versions via uv.lock

From the repository root:
```
uv run task run-local
```
Run the test script In a separate terminal:
```
uv run task test-api
```

The test script calls all API endpoints in sequence and prints their outputs.

## Notes

- The upload endpoint is idempotent, so notes_inserted may be 0 on repeat runs

- Some low-signal sections (e.g., vitals or metadata) may produce weaker semantic matches, which is expected for a pure vector similarity approach

