FROM python:3.13-slim

WORKDIR /app
COPY server/pyproject.toml /app/pyproject.toml
COPY server/src /app/src
RUN pip install --no-cache-dir "/app[postgres]"

COPY content /content

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "--factory", "steadytype_server.main:app_factory", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
