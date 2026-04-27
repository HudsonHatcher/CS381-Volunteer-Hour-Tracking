FROM python:3.11-slim

WORKDIR /app

COPY . .

EXPOSE 5000

RUN pip install flask

ENTRYPOINT ["python", "ui_service.py"]