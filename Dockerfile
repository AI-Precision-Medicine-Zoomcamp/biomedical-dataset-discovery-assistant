FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
COPY evaluation ./evaluation
COPY eval ./eval
COPY data ./data
COPY tests ./tests

RUN pip install --no-cache-dir -e .

EXPOSE 8000 8501

CMD ["python", "-m", "evaluation.retrieval_eval", "--catalog", "data/processed/catalog.json"]
