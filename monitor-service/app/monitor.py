import json
import requests
import pika
import logging
from datetime import datetime
from fastapi import FastAPI, Response, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .config import RABBITMQ_URL, PRODUCER_URL, QUEUE_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("monitor")

app = FastAPI()

# Mount simple static UI under /ui
app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")


@app.get("/")
def root():
    return RedirectResponse(url="/ui/")


def check_producer():
    try:
        resp = requests.get(f"{PRODUCER_URL}/", timeout=2)
        if resp.status_code == 200:
            return {"status": "up", "detail": resp.json()}
        return {"status": "down", "detail": {"code": resp.status_code}}
    except Exception as e:
        logger.warning(f"Producer check failed: {e}")
        return {"status": "down", "error": str(e)}


def check_rabbitmq():
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        q = channel.queue_declare(queue=QUEUE_NAME, passive=True)
        message_count = q.method.message_count
        consumer_count = q.method.consumer_count
        connection.close()
        return {"status": "up", "message_count": message_count, "consumer_count": consumer_count}
    except Exception as e:
        logger.warning(f"RabbitMQ check failed: {e}")
        return {"status": "down", "error": str(e)}


@app.get("/health")
def health():
    prod = check_producer()
    rabbit = check_rabbitmq()
    if prod["status"] == "up" and rabbit["status"] == "up":
        overall = "up"
    elif prod["status"] == "down" and rabbit["status"] == "down":
        overall = "down"
    else:
        overall = "degraded"

    return {"status": overall, "producer": prod, "rabbitmq": rabbit}



@app.post("/api/send")
async def api_send(request: Request):
    """Proxy endpoint: recibe un JSON desde la UI y lo reenvía al `producer`."""
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    try:
        resp = requests.post(f"{PRODUCER_URL}/send-shipment", json=payload, timeout=5)
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        return JSONResponse(status_code=resp.status_code, content={"ok": resp.ok, "response": body})
    except Exception as e:
        logger.error(f"Error proxying to producer: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/send_batch")
async def api_send_batch(request: Request):
    """Envía múltiples mensajes al producer para simular carga; retorna el resultado por mensaje."""
    try:
        data = await request.json()
    except Exception:
        data = {}

    count = int(data.get("count", 1))
    template = data.get("message", {}) or {}
    results = []

    for i in range(count):
        msg = dict(template)
        # ensure unique id and fresh timestamp
        base_id = msg.get("shipmentId", "AUTO")
        msg["shipmentId"] = f"{base_id}-{i}-{int(datetime.utcnow().timestamp())}"
        msg["timestamp"] = datetime.utcnow().isoformat() + "Z"

        try:
            resp = requests.post(f"{PRODUCER_URL}/send-shipment", json=msg, timeout=5)
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            results.append({"index": i, "status": resp.status_code, "ok": resp.ok, "body": body})
        except Exception as e:
            results.append({"index": i, "error": str(e)})

    return JSONResponse(status_code=200, content={"results": results})


@app.get("/metrics")
def metrics():
    prod = check_producer()
    rabbit = check_rabbitmq()
    lines = []
    lines.append(f"monitor_producer_up {1 if prod['status'] == 'up' else 0}")

    if rabbit.get("status") == "up":
        lines.append("monitor_rabbitmq_up 1")
        lines.append(f"monitor_queue_messages {rabbit.get('message_count', 0)}")
        lines.append(f"monitor_queue_consumers {rabbit.get('consumer_count', 0)}")
    else:
        lines.append("monitor_rabbitmq_up 0")
        lines.append("monitor_queue_messages 0")
        lines.append("monitor_queue_consumers 0")

    body = "\n".join(lines) + "\n"
    return Response(content=body, media_type="text/plain")
