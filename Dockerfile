FROM python:3.13
WORKDIR /usr/src/app

COPY pyproject.toml .
RUN mkdir -p application && touch application/__init__.py
RUN pip install --no-cache-dir .

COPY . .
RUN pip install --no-cache-dir .
