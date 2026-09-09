FROM mcr.microsoft.com/devcontainers/python:1-3.14-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /workspaces/${localWorkspaceFolderBasename}

COPY pyproject.toml uv.lock* ./
RUN uv sync --dev