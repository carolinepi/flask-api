FROM python:3.9-slim-buster as base

ENV PROJECT_ROOT=/app/
WORKDIR ${PROJECT_ROOT}

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY api.py api.py
ENTRYPOINT ["python3.9"]
