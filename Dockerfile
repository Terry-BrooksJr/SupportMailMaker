# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

FROM python:3.10-slim
LABEL Maintainer="Terry Brooks, Jr. <terry.Brooks@learnosity.com>"
LABEL Name="SupportMail Generator"
LABEL Version="1"

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=-1
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_PORT=7500
ENV GRADIO_NODE_PATH="/usr/bin/node"
ENV GRADIO_NUM_PORTS=1000
ENV GRADIO_NODE_NUM_PORTS=1000
ENV GRADIO_ANALYTICS_ENABLED=True
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV SUPPORTMAIL_HTML_TEMPLATE="/src/templates"
WORKDIR /src

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN set -e \
        && apt update \
        && apt upgrade -y \
        && apt-get install -y --no-install-recommends \
        python3-invoke \
        nodejs \
        npm \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.

# Copy the source code into the container.
COPY support_mail_maker/ /src/

# Expose the port that the application listens on.
EXPOSE 7500
EXPOSE 7860

# Run the application.
CMD $(which python) /src/app.py
