# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

FROM python:3.12-slim-bookworm AS base
USER root
WORKDIR /app
ENV HOME=/home
ENV PATH=$HOME/.local/bin:/app/bin:$PATH
ENV VIRTUAL_ENV=/app
ENV MODEL_ENTRYPOINT=/model
ENV CME_LIVE_MODE=0
EXPOSE 8000

RUN apt-get update && \
  apt-get install --yes --no-install-recommends \
  curl \
  git \
  git-lfs \
  gir1.2-pango-1.0 \
  graphviz \
  libcairo2-dev \
  libgirepository1.0-dev \
  nodejs && \
  apt-get autoremove --yes && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

USER 1000

FROM base AS build

USER root
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -Lo /tmp/install.sh https://astral.sh/uv/install.sh && \
  chmod +x /tmp/install.sh && \
  UV_NO_MODIFY_PATH=1 sh /tmp/install.sh && \
  rm /tmp/install.sh
RUN curl -fsSL https://get.pnpm.io/install.sh | ENV="$HOME/.bashrc" SHELL="$(which bash)" PNPM_HOME="$HOME/.local/bin" bash -

COPY . /build

WORKDIR /build
RUN git restore -- Dockerfile && \
  uv run cme build

RUN uv venv /app && \
  uv sync --active --locked --no-default-groups --no-editable

USER 1000

FROM base

USER root
RUN mkdir /model
COPY --chown=0:0 --chmod=755 entrypoint.sh /
COPY --link --from=build --chown=0:0 /app /app
COPY --link --from=build /build/templates /templates
COPY --link --from=build /build/static /data/static
RUN /app/bin/python -c "from capellambse_context_diagrams import install_elk; install_elk()"
WORKDIR /data

RUN git config --global --add safe.directory /model && \
  git config --global --add safe.directory /model/.git && \
  chmod -R a=rwX /home

USER 1000

ENTRYPOINT ["/entrypoint.sh"]
