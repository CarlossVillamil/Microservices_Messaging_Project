FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# OPCIÓN 1 (solo worker, más real)
CMD ["python", "-m", "app.consumer_worker"]

# OPCIÓN 2 (worker + API en supervisord o PM2 si lo deseas)
# Te la puedo armar si quieres los dos procesos juntos
