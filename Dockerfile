FROM python:3.12-alpine

RUN echo 'https://dl-cdn.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories
RUN apk add --no-cache dart-sass pandoc-cli

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -Ur /app/requirements.txt

COPY ./ /app/
WORKDIR /app/

CMD ["python", "generate.py"]
