FROM python:3.9.5

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY Pipfile ./
RUN pip install pipenv && \
    pipenv install

COPY . ./

# CMD poetry run alembic upgrade head && \
CMD pipenv run uvicorn --host=0.0.0.0 src.main:app