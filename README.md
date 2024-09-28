# velosafe

[![CI](https://github.com/github_username/hackyeah2024/actions/workflows/backend.yml/badge.svg)](https://github.com/github_username/hackyeah2024/actions)

Project for hackyeah 2024

# Prerequisites

## Native way with virtualenv
- [Python3.10](https://www.python.org/downloads/)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/)

## Docker way
- [Docker](https://docs.docker.com/engine/install/)  
- [Docker Compose](https://docs.docker.com/compose/install/)

## Local Development

## Native way with virtualenv

First create postgresql database:

```sql
create user velosafe with createdb;
alter user velosafe password 'velosafe';
create database velosafe owner velosafe;
```
Now you can setup virtualenv and django:
```bash
virtualenv venv
source venv/bin/activate
pip install pip-tools
make bootstrap
```

## Docker way

Start the dev server for local development:
```bash
docker compose up
```

Run a command inside the docker container:

```bash
docker compose run --rm web [command]
```


## Pre-commit hooks

To install pre-commit hooks run:

```bash
pre-commit install
```
