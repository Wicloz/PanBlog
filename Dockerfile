FROM python:slim

RUN apt update && apt install -y pandoc && rm -rf /var/*/apt/

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -Ur /app/requirements.txt

COPY ./ /app/
WORKDIR /app/

CMD ["python", "generate.py"]
