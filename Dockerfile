
FROM python:3.12-slim-bookworm AS base

#
# Fetch requirements
#
FROM base AS builder
RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app/
COPY ./src/requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --prefix="/reqs" -r requirements.txt

#
# Runtime
#
FROM base AS runtime
WORKDIR /usr/src/app/
COPY --from=builder /reqs /usr/local
COPY ./src/ ./

RUN opentelemetry-bootstrap -a install

EXPOSE 8000
ENTRYPOINT [ "opentelemetry-instrument", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]