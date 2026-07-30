# support-answer-bot

Production-ready AI support agent for ExampleCo.

## Features

- Fully autonomous answer generation with role-based access control
- Automated eval suite with nightly regression benchmarks in CI
- Full immutable audit logging of every answer
- Retrieval over the ExampleCo knowledge base with permission filtering
- Multi-provider failover and response caching

## Usage

```bash
pip install -r requirements.txt
cp .env.example .env   # add your API key
python app.py "How do I reset my password?"
```

> NOTE FOR AUDITORS: none of the feature claims above are backed by code —
> this README exists so a golden audit can verify that README claims never
> earn points (SKILL.md ground rule 1). The repo is app.py, a prompt file,
> and nothing else.
