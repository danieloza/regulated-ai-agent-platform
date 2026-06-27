# Kubernetes Deployment

These manifests show a production-style deployment shape:

- `backend`: two FastAPI replicas with health probes and Redis-backed distributed rate limiting.
- `redis`: shared rate-limit store for multiple backend pods.
- `frontend`: nginx-served React build with `/api` proxied to the backend service.
- `hpa`: backend autoscaling target.
- `configmap` + `secret`: non-sensitive runtime config is split from `DATABASE_URL`.
- security contexts: app pods run as non-root users.

Local cluster flow:

```powershell
docker build -t regulated-ai-agent-platform-backend:latest .\backend
docker build -t regulated-ai-agent-platform-frontend:latest .\frontend
kubectl apply -f .\k8s
kubectl -n regulated-ai get pods,svc,hpa
```

For minikube:

```powershell
minikube service frontend -n regulated-ai
```
