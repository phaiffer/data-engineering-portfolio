FROM python:3.12-slim

ENV HOME=/tmp \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace/projects/03-retail-revenue-analytics

COPY docker/pipeline-requirements.txt /tmp/pipeline-requirements.txt

RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r /tmp/pipeline-requirements.txt

COPY . ./

CMD ["sleep", "infinity"]
