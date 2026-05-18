# Multi-Document Analysis Tool

Production-ready AI document analysis API built using FastAPI, Docker, and AWS EC2.

## Live Deployment

API Base URL:

```bash
http://16.171.249.112:8000
```

Swagger API Docs:

```bash
http://16.171.249.112:8000/docs
```

Health Check:

```bash
http://16.171.249.112:8000/health
```

---

# Project Overview

This project is a production-style Multi-Document Analysis System designed for AI engineering portfolio work.

The system allows users to:

* Upload documents
* Analyze document content
* Compare multiple documents
* Generate summaries
* Track API statistics

The project was containerized using Docker and deployed publicly on AWS EC2.

---

# Features

## Document Upload API

Upload and process files.

## Multi-Document Analysis

Analyze document content through REST APIs.

## Document Comparison

Compare multiple documents.

## AI-Based Summarization

Generate concise summaries.

## FastAPI Backend

High-performance API framework.

## Dockerized Deployment

Containerized production deployment.

## AWS EC2 Hosting

Live cloud deployment using AWS.

## Swagger Documentation

Interactive API testing interface.

---

# Tech Stack

| Technology            | Usage                 |
| --------------------- | --------------------- |
| Python                | Core backend language |
| FastAPI               | API framework         |
| Docker                | Containerization      |
| AWS EC2               | Cloud deployment      |
| Uvicorn               | ASGI server           |
| PyMuPDF               | PDF processing        |
| Transformers          | NLP processing        |
| ChromaDB              | Vector database       |
| Sentence Transformers | Embeddings            |
| LangChain             | AI orchestration      |

---

# API Endpoints

| Method | Endpoint   | Description         |
| ------ | ---------- | ------------------- |
| GET    | /health    | Health check        |
| POST   | /upload    | Upload documents    |
| POST   | /analyze   | Analyze documents   |
| POST   | /compare   | Compare documents   |
| POST   | /summarize | Summarize documents |
| GET    | /stats     | API statistics      |

---

# Docker Deployment

## Build Docker Image

```bash
docker build -t project3 .
```

## Run Docker Container

```bash
docker run -d -p 8000:8000 --name project3-container project3
```

---

# AWS EC2 Deployment

The application was deployed on:

* AWS EC2
* Amazon Linux 2023
* Docker containerized environment
* Public API access enabled through security groups

---

# Local Installation

## Clone Repository

```bash
git clone https://github.com/rajavinay-eng/multi-document-analysis-tool.git
```

## Navigate to Project

```bash
cd multi-document-analysis-tool
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Application

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

# Learning Outcomes

This project helped build practical experience in:

* Production API development
* Docker containerization
* AWS cloud deployment
* FastAPI backend systems
* REST API design
* Linux server management
* Security group configuration
* Public API hosting

---

# Future Improvements

* Authentication system
* Database integration
* CI/CD pipeline
* HTTPS support
* Kubernetes deployment
* Load balancing
* Monitoring dashboards

---

# Author

Raja Vinay Kumar Koppula

AI Engineer Portfolio Project


