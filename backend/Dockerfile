FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
# Install only the base deps (no pipecat/daily extras) for the lean Deepgram-direct demo path;
# the Pipecat/Daily production path (pipeline.py) is imported lazily and only needed if that path is used.
RUN uv pip install --system fastapi "uvicorn[standard]" sqlalchemy aiosqlite greenlet websockets python-dotenv

COPY app ./app
COPY tests ./tests

EXPOSE 8000
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
