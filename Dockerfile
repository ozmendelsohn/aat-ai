FROM python:3.10.11

ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry==1.5.1

RUN mkdir /app

COPY pyproject.toml /app

WORKDIR /app

RUN poetry config virtualenvs.create false

CMD poetry install
