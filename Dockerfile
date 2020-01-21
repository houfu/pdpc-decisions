FROM python:3.8-alpine

# author of file
LABEL "maintainer"="Ang Houfu <houfu@outlook.sg>"

# Packages that we need
COPY requirement.txt /app/
WORKDIR /app

# Chromium
RUN apk add curl && \
    apk add unzip chromium chromium-chromedriver

# instruction to be run during image build
RUN apk add build-base pkgconfig zeromq-dev freetype-dev && \
    pip3 install -r requirement.txt --no-cache-dir

# Copy all the files from current source directory(from your system) to
# Docker container in /app directory
COPY . /code/
WORKDIR /code

# Install spacy english models
RUN pip3 install .

# Specifies a command that will always be executed when the
# container starts.
# In this case we want to start the python interpreter
ENTRYPOINT ["python", "/code/pdpc_decisions/pdpcdecision.py"]