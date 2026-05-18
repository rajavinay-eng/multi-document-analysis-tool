# Multi-Document Analysis Tool

Production-ready FastAPI application deployed on AWS EC2 using Docker.

---

## Live API

### Swagger Documentation
http://16.171.249.112:8000/docs

### Health Check
http://16.171.249.112:8000/health

### API Base URL
http://16.171.249.112:8000

---

# Project Overview

This project is a production-style Multi-Document Analysis System designed for AI engineering portfolio work.

The system allows users to:

- Upload documents
- Analyze document content
- Compare multiple documents
- Generate AI-based summaries
- Track API statistics

The application was containerized using Docker and deployed publicly on AWS EC2.

---

# Features

## Document Upload API

Upload and process files through REST APIs.

## Multi-Document Analysis

Analyze document content using FastAPI endpoints.

## Document Comparison

Compare multiple uploaded documents.

## AI-Based Summarization

Generate concise summaries from document content.

## FastAPI Backend

High-performance API framework implementation.

## Dockerized Deployment

Fully containerized production deployment.

## AWS EC2 Hosting

Public cloud deployment using Amazon EC2.

## API Monitoring

Track usage statistics and health endpoints.

---

# Tech Stack

- Python
- FastAPI
- Docker
- AWS EC2
- REST APIs
- Uvicorn
- ChromaDB
- LangChain
- Transformers

---

# API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Health monitoring |
| POST | /upload | Upload documents |
| POST | /analyze | Analyze documents |
| POST | /compare | Compare documents |
| POST | /summarize | Generate summaries |
| GET | /stats | API statistics |

---

# Docker Setup

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

- AWS EC2
- Amazon Linux 2023
- Docker containerized environment
- Public API access through security groups

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

- Production API development
- Docker containerization
- AWS EC2 deployment
- Backend engineering
- REST API architecture
- AI application deployment
- Cloud infrastructure management

---

# Author

Raja Vinay Kumar Koppula

GitHub:
https://github.com/rajavinay-eng

LinkedIn:
https://www.linkedin.com/in/rajavinaykumarkoppula/
