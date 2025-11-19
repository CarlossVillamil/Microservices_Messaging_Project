📦 Microservices Messaging Project
🛰️ Arquitectura de Microservicios con FastAPI • RabbitMQ • Kubernetes • Kustomize • Monitor UI

Este proyecto implementa un sistema distribuido de mensajería para actualizaciones de envíos.
Incluye microservicios, cola de mensajes, dashboard interactivo, y un despliegue completo en Kubernetes.

🚀 1. Arquitectura del Sistema
UI Monitor → Producer → RabbitMQ → Consumer
                     ↑            ↓
             Kubernetes Deployments + Services

Componentes:
Servicio	Tecnología	Descripción
Producer	FastAPI	Envía mensajes a RabbitMQ
Consumer	Python	Consume mensajes y simula procesamiento
RabbitMQ	StatefulSet	Broker de mensajería
Monitor UI	FastAPI + HTML/CSS	Dashboard para enviar mensajes y ver métricas

📁 2. Estructura del Proyecto
Microservices_Messaging_Project/
├── producer-service/
├── consumer-service/
├── monitor-service/
├── docs/
│   └── message_format.json
└── k8s/
    ├── namespace.yaml
    ├── app-config.yaml
    ├── rabbitmq-secret.yaml
    ├── rabbitmq-statefulset.yaml
    ├── rabbitmq-services.yaml
    ├── producer-deployment.yaml
    ├── consumer-deployment.yaml
    ├── monitor-deployment.yaml
    ├── ingress-monitor.yaml   (opcional)
    └── kustomization.yaml

📬 3. Formato de Mensaje

Los microservicios usan el formato definido en:

docs/message_format.json

Ejemplo:

{
  "shipmentId": "A123",
  "status": "IN_TRANSIT",
  "timestamp": "2025-11-19T01:20:00Z",
  "location": {
    "lat": 3.43,
    "lng": -76.52
  }
}

☸️ 4. Despliegue en Kubernetes
➊ Crear namespace
kubectl apply -f k8s/namespace.yaml

➋ Aplicar TODO el sistema con Kustomize
kubectl apply -k k8s/

➌ Verificar pods
kubectl get pods -n microservices-messaging


Debes ver algo así:

producer-xxxx       Running
consumer-xxxx       Running
monitor-xxxx        Running
rabbitmq-0          Running

📊 5. Acceder al Monitor UI

Ejecuta:

kubectl port-forward -n microservices-messaging svc/monitor 8002:8002


Abrir en navegador:

👉 http://localhost:8002

Desde aquí puedes:

Ver estado de Producer y RabbitMQ

Ver consumidores conectados

Ver mensajes en cola

Enviar mensajes individuales

Enviar lotes de mensajes

📤 6. Probar el Producer (Manual)
Postman o curl:

POST → http://localhost:8001/send-shipment

Body:

{
  "shipmentId": "A123",
  "status": "IN_TRANSIT",
  "timestamp": "2025-11-19T01:20:00Z",
  "location": {
    "lat": 3.43,
    "lng": -76.52
  }
}


Si recibes:

{
  "message": "Shipment update sent",
  "data": { ... }
}


El mensaje llegó a RabbitMQ correctamente.

🧪 7. Ver mensajes procesados (Consumer)
kubectl logs deployment/consumer -n microservices-messaging -f


Deberías ver:

Message received { ... }
Message acknowledged

🎛️ 8. Truco para demostrar la cola funcionando

Por defecto, el consumer es TAN rápido que la cola queda vacía.
Si quieres demostrar acumulación de mensajes:

1️⃣ Apaga el consumidor:
kubectl scale deployment consumer -n microservices-messaging --replicas=0

2️⃣ Envía mensajes desde el Monitor

La cola comenzará a llenarse.

3️⃣ Enciende el consumer:
kubectl scale deployment consumer -n microservices-messaging --replicas=1


Y verás cómo procesa todo el backlog.
