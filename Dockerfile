FROM python:3.9-slim as base
WORKDIR /app

ENV VERSION="1.49.52.2"

## Build and packaging
FROM base as builder
RUN apt-get update
RUN apt-get install -y curl
# RUN apk upgrade
# RUN apk add curl

# download package
RUN curl -OL https://github.com/DiaxCapital/ccxt/releases/download/v${VERSION}/ccxt-${VERSION}.tar.gz
RUN tar xzf ccxt-${VERSION}.tar.gz

# virtualenv and install
RUN pip install --upgrade pip 
RUN cd ccxt-${VERSION} && python setup.py install

## Final imagem
COPY script.py /app

CMD python ./script.py
