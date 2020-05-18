# Setting defaults
FROM python:3.7-alpine as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Building necessary tools, then python env
FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.0.5

RUN apk add --no-cache gcc libffi-dev musl-dev postgresql-dev \
    && pip install "poetry==$POETRY_VERSION" \
    && python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin

COPY . /app/
RUN poetry build && /venv/bin/pip install dist/*.whl

# Creafting runtime image
FROM base as final

RUN apk add --no-cache libffi libpq
COPY --from=builder /venv /venv

EXPOSE 5000

CMD [ "/venv/bin/python", "-m", "toychain", "--host", "0.0.0.0", "--port", "5000" ]