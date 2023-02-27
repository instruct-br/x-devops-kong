# =============================================================================
# registry - Recebe como argumento o registry (proxy) Nexus Equinix,
#            devendo utilizar o DockerHub apenas com fallback
# =============================================================================
ARG DOCKER_REGISTRY=index.docker.io
# =============================================================================
# BASE - Python e dependências
# =============================================================================
FROM $DOCKER_REGISTRY/python:3.8 as base
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip && pip install poetry
WORKDIR /code
COPY pyproject.toml poetry.lock /code/
RUN poetry config virtualenvs.create false
RUN poetry install
COPY . /code/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]