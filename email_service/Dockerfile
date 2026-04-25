FROM python:3.11-slim

WORKDIR /app

COPY . .

EXPOSE 5002

RUN pip install --no-cache-dir

CMD ["python", "email_service.py"]