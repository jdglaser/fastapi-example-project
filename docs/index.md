# Intro

## Introduction

This project can be used as a template/guide for creating a REST API using the FastAPI framework.

Checkout the project code: [https://github.com/jdglaser/fastapi-example-project](https://github.com/jdglaser/fastapi-example-project)

## Features

+ PostgresSQL for database
+ Asynchronous database connections with [Databases](https://pypi.org/project/databases/)
+ Database migrations with [Alembic](https://pypi.org/project/alembic/)
+ [SQLAlchemy Core 2.0](https://docs.sqlalchemy.org/en/14/core/future.html) for database interaction
+ JWT auth with refresh tokens - implemented using FastAPIs built-in security features
+ Pipenv for project dependency management

## Project layout


    app/                # All application code
        alembic/        # Alembic configuration and versions
        database/       # Database related code
            repos/      # Database repository definitions
            tables/     # SQLAlchemy core table definitions
            database.py # Contains database object and SQLAlchemy metadata object
        models/         # Pydantic model definitions
        routes/         # Individual FastAPI routes
        util/           # Utility functions and classes
    scripts/            # Helpful shell scripts
    tests/              # Application tests
    docker-compose.yml  # Defines database and app services for local development
    Dockerfile          # Dockerfile to build app
