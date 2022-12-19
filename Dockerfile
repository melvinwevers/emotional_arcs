FROM python:3.10-slim as build

RUN apt-get update \
    && apt-get install -y gcc g++ libxml2-dev libxslt-dev python3-lxml \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
LABEL org.opencontainers.image.source = "https://github.com/melvinwevers/emotional_arcs"
COPY --from=build /opt/venv /opt/venv
COPY . /app
ENV PATH="/opt/venv/bin:$PATH"
CMD ["python3", "/app/script.py"]
