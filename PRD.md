# Banking Regulatory RAG Application

An AI-powered Retrieval-Augmented Generation (RAG) application that helps bank employees quickly search, understand, compare, and verify banking regulations, circulars, policies, and compliance documents.

## 📌 Overview

Banks maintain **10–20+ years of regulatory documents**, including:

* Rules and regulations
* Banking circulars
* Compliance policies
* Internal guidelines
* Regulatory notifications
* Historical documents

These documents are often stored across thousands of PDFs and other files, making it difficult for employees to quickly find the correct information.

This project aims to build a **local, free, AI-powered RAG system** that allows bank employees to ask questions about regulations using natural language and receive answers backed by the bank's actual documents.

---

## 🚨 Problem

Bank employees face several challenges when working with large collections of regulatory documents:

* Finding the correct rule quickly
* Finding what a rule was in the past
* Determining whether an old rule is still valid
* Comparing historical and current regulations
* Understanding how a regulation has changed
* Verifying the source of an answer
* Manually searching through hundreds or thousands of PDFs

Traditional document searching is slow, inefficient, and can lead to incorrect interpretation.

### Example Problems

An employee may need to answer questions such as:

> "What is the current rule for X?"

> "What was the rule for X in 2015?"

> "How has this rule changed over time?"

Finding these answers manually could require searching through multiple documents, dates, sections, and amendments.

---

## 💡 Solution

We will build an **AI-powered Banking Regulatory RAG Application** that allows employees to ask regulatory questions in natural language.

Instead of allowing an LLM to answer purely from its trained knowledge, the system retrieves relevant information from the bank's actual documents and uses that information to generate the answer.

### Core Workflow

```text
Bank Regulatory Documents
          ↓
     PDF Extraction
          ↓
      OCR Processing
          ↓
    Document Chunking
          ↓
       Embeddings
          ↓
    Vector Database
          ↓
      User Question
          ↓
   Relevant Retrieval
          ↓
       LLM / RAG
          ↓
    Generated Answer
          ↓
 Source + Section + Date
```

The goal is to make every answer **traceable back to the original regulatory document**.

---

## 🎯 Core Features

### 1. Natural Language Regulatory Search

Employees can ask questions naturally instead of manually searching through documents.

Example:

```text
What is the current rule regarding X?
```

The system retrieves the relevant regulatory information and generates an answer.

---

### 2. Historical Regulation Search

Users can ask about regulations from a specific period.

Example:

```text
What was the rule regarding X in 2015?
```

The system should retrieve historical documents relevant to that time period.

---

### 3. Regulation Comparison

Users can compare historical and current regulations.

Example:

```text
How has the regulation for X changed since 2015?
```

The system should identify relevant historical and current documents and explain the major changes.

---

### 4. Source Verification

Every AI-generated answer should provide evidence from the source documents.

The response should ideally contain:

```text
Answer
↓
Source Document
↓
Section
↓
Page
↓
Publication Date
```

This allows employees to verify the information instead of blindly trusting the AI.

---

### 5. Document-Based Answers

The LLM should primarily use retrieved regulatory documents when generating answers.

This reduces the risk of the AI providing information that is unrelated to the bank's actual regulatory corpus.

---

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │   Bank Documents     │
                    │ PDFs / Circulars     │
                    │ Policies / Rules     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Document Processing  │
                    │      Docling         │
                    │     PaddleOCR        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Chunking & Metadata  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Embedding Generation │
                    │       BGE-M3         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Qdrant Vector DB   │
                    └──────────┬───────────┘
                               │
                               │
       ┌───────────────────────┘
       │
       ▼
┌──────────────────────┐
│   React Frontend     │
│ React + Vite +       │
│ Tailwind CSS         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    FastAPI Backend   │
│       Python         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      LlamaIndex      │
│     RAG Pipeline     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Ollama + LLM       │
│   Local Inference    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Answer + Evidence    │
│ Source + Section     │
│ Date + Page          │
└──────────────────────┘
```

---

## 🛠️ Technology Stack

| Area             | Technology                  |
| ---------------- | --------------------------- |
| Frontend         | React + Vite + Tailwind CSS |
| Backend          | Python + FastAPI            |
| RAG Framework    | LlamaIndex                  |
| LLM Runtime      | Ollama                      |
| LLM              | Local LLM                   |
| Embeddings       | BGE-M3                      |
| Vector Database  | Qdrant                      |
| Main Database    | PostgreSQL                  |
| Document Storage | MinIO                       |
| PDF Processing   | Docling                     |
| OCR              | PaddleOCR                   |
| Cache / Jobs     | Redis                       |
| Containerization | Docker                      |

---

## 🔍 RAG Pipeline

The application follows a Retrieval-Augmented Generation architecture.

### Step 1 — Document Ingestion

Regulatory documents are uploaded into the system.

```text
PDF
Circular
Policy
Notification
     ↓
Document Storage
```

Documents are stored using MinIO.

---

### Step 2 — Document Processing

Documents are processed using Docling.

For scanned documents or documents containing images, PaddleOCR is used to extract text.

```text
Document
    ↓
Text Extraction
    ↓
OCR if required
    ↓
Structured Content
```

---

### Step 3 — Chunking

Large documents are divided into smaller meaningful sections or chunks.

Each chunk should retain important metadata such as:

```text
Document ID
Document Name
Section
Page Number
Publication Date
Effective Date
Regulation Type
Source
```

---

### Step 4 — Embedding

Each document chunk is converted into a vector representation using **BGE-M3**.

```text
Text Chunk
    ↓
BGE-M3
    ↓
Embedding Vector
```

---

### Step 5 — Vector Storage

The generated embeddings are stored in **Qdrant**.

When a user asks a question, the question is also converted into an embedding.

Qdrant then finds the most semantically relevant document chunks.

---

### Step 6 — Retrieval

The RAG system retrieves the most relevant information.

```text
User Question
      ↓
Question Embedding
      ↓
Qdrant Search
      ↓
Relevant Chunks
```

---

### Step 7 — Generation

The retrieved context is provided to the local LLM through LlamaIndex.

```text
Question
   +
Retrieved Context
   ↓
Local LLM
   ↓
Answer
```

The model should generate an answer based on the retrieved regulatory information.

---

### Step 8 — Evidence

The final response should contain references to the original document.

Example:

```text
Answer:
The current requirement is X.

Source:
Circular ABC-2026

Section:
Section 4.2

Page:
Page 17

Effective Date:
January 2026
```

---

## 🗄️ Data Storage

The system uses different storage technologies for different purposes.

### PostgreSQL

Used for structured application data such as:

* Users
* Documents
* Document metadata
* Regulatory versions
* Access information
* Query history
* Audit records

### Qdrant

Used for:

* Document embeddings
* Semantic search
* Vector similarity retrieval

### MinIO

Used for:

* Original PDFs
* Uploaded documents
* Processed document files

### Redis

Used for:

* Caching
* Background jobs
* Processing queues
* Temporary data

---

## 🤖 Local AI

The MVP is designed to run using local AI models through **Ollama**.

This means the system does not require paid OpenAI or Anthropic APIs for the core RAG workflow.

```text
Application
     ↓
LlamaIndex
     ↓
Ollama
     ↓
Local LLM
```

This approach provides:

* No per-request API cost
* Local inference
* Better control over sensitive documents
* No requirement to send regulatory documents to an external AI provider

---

## 🔐 Security Considerations

Because this application deals with banking and regulatory information, security is an important part of the system.

The production version should consider:

* Authentication
* Role-based access control
* Document-level permissions
* API authentication
* Secure document storage
* Audit logging
* Query logging
* Encryption
* Data access policies
* Prompt injection protection
* Sensitive information protection

The MVP will focus primarily on the RAG pipeline and can run locally.

---

## 📊 Example Queries

The system should support questions such as:

```text
What is the current rule for X?
```

```text
What was the rule for X in 2015?
```

```text
When did this regulation change?
```

```text
How has the regulation changed between 2015 and 2026?
```

```text
Which circular introduced this requirement?
```

```text
Is the 2018 circular still applicable?
```

```text
What section of the circular contains this requirement?
```

---

## 🧠 Key Design Principle

The most important principle of this application is:

> **The AI should not simply answer from its own knowledge. It should retrieve the relevant regulatory documents and use them as evidence for its answer.**

The system should prioritize:

```text
Correct Retrieval
       +
Accurate Context
       +
Source Verification
       +
Clear Explanation
```

---

## 💰 Cost Strategy

The MVP is designed to run **locally and for free**.

We will avoid dependency on:

* Paid LLM APIs
* Paid vector databases
* Paid cloud storage
* Paid AI inference services

Instead, the MVP will use:

```text
Ollama
Qdrant
PostgreSQL
MinIO
Redis
Docker
Local Models
```

All running locally.

---

## 🐳 Deployment

The application will use Docker to simplify local setup and deployment.

Expected services:

```text
Frontend
Backend
PostgreSQL
Qdrant
MinIO
Redis
Ollama
```

A Docker-based environment allows the entire application stack to be started consistently.

---

## 🚀 MVP Goal

The first version of the application should demonstrate the complete RAG workflow:

```text
Upload Regulatory Document
          ↓
Extract Text / OCR
          ↓
Create Chunks
          ↓
Generate Embeddings
          ↓
Store in Qdrant
          ↓
Ask Question
          ↓
Retrieve Relevant Context
          ↓
Generate Answer
          ↓
Display Source Evidence
```

The MVP does not need to solve every banking compliance requirement immediately.

The primary objective is to prove that the system can:

1. Store regulatory documents.
2. Process and index them.
3. Retrieve relevant information.
4. Answer questions using RAG.
5. Provide source evidence.
6. Search historical regulations.
7. Compare regulatory changes.

---

## 🎯 Project Objective

The ultimate goal is to create a reliable regulatory knowledge assistant that helps bank employees move from:

```text
Thousands of Documents
        ↓
Manual Searching
        ↓
Slow Investigation
        ↓
Possible Errors
```

to:

```text
Natural Language Question
        ↓
AI-Powered Retrieval
        ↓
Relevant Regulation
        ↓
Clear Answer
        ↓
Verified Source
```

### Core Idea

**Store the documents → retrieve the correct information → use AI to explain it → show the original source as evidence.**

This project demonstrates how **RAG, local AI, document processing, vector search, and modern web technologies** can be combined to build a practical banking regulatory knowledge system.
