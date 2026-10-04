FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY client.py .
COPY database.py .
COPY init_db.py .
COPY condutores_service.py .
COPY veiculos_service.py .
COPY multas_service.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "--version"]