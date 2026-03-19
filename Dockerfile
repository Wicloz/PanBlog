FROM python:alpine
RUN apk add --no-cache pandoc-cli

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -Ur /app/requirements.txt

COPY ./ /app/
WORKDIR /app/

CMD ["python", "generate.py"]
