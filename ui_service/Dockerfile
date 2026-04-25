FROM python:3.11-slim

WORKDIR /app

COPY . .

EXPOSE 5003

RUN pip install flask

CMD ["python", "DashboardService.py"]