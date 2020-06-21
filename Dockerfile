FROM python:3.8-alpine

# author of file
LABEL "maintainer"="Ang Houfu <houfu@outlook.sg>"

# Copy all the files from current source directory(from your system) to
# Docker container in /app directory
COPY . /code/
WORKDIR /code

# Chromium
RUN apk add curl && \
    apk add unzip chromium chromium-chromedriver

# Project install
RUN apk add --no-cache build-base pkgconfig zeromq-dev freetype-dev libffi-dev libressl-dev musl-dev && \
        pip3 install --no-cache-dir poetry && \
        poetry config virtualenvs.create false && \
        poetry install --no-dev --no-interaction --no-ansi && \
        apk del build-base pkgconfig zeromq-dev freetype-dev libffi-dev libressl-dev musl-dev

# Specifies a command that will always be executed when the
# container starts.
# In this case we want to start the python interpreter
ENTRYPOINT ["python", "/code/pdpc_decisions/pdpcdecision.py"]