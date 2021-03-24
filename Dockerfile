ARG PYTHON_VERSION

FROM python:$PYTHON_VERSION

ARG DB_ENGINE

RUN echo "DB_ENGINE=$DB_ENGINE"

WORKDIR /code

COPY setup.py .

RUN pip install -e .[testing]

RUN pip install -e .[$DB_ENGINE]

COPY . .