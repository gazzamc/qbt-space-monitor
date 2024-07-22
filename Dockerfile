FROM alpine:latest

ARG PYTHON_VERSION=3.11

RUN apk --no-cache add \
    python3 \
    py3-pip \
    py3-requests

WORKDIR /app

COPY ./src ./

CMD ["python", "qbt-space-monitor.py"]
