FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY docker/api-requirements.txt /tmp/api-requirements.txt

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r /tmp/api-requirements.txt

RUN mkdir -p /workspace/projects/03-retail-revenue-analytics/data

COPY api /workspace/projects/03-retail-revenue-analytics/api

EXPOSE 5002

CMD ["python", "projects/03-retail-revenue-analytics/api/app.py"]
