# System Architecture

SignalIQ follows a modular architecture.

Frontend

- React
- TypeScript
- Tailwind CSS
- React Router

Backend

- FastAPI
- Python

Database

- PostgreSQL

Caching

- Redis

AI

- OpenAI
- LangGraph
- LangChain

Data Sources

- Yahoo Finance
- Sahm API
- Saudi Exchange
- News APIs

Architecture

Frontend
↓

FastAPI Backend
↓

AI Agents
↓

Data Collectors
↓

Database

Each layer is independent.

Business logic belongs in the backend.

Frontend should never perform financial calculations.

The frontend only consumes REST APIs.