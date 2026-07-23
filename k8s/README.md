# Kubernetes Deployment

These manifests show a production-style deployment shape:

- `backend`: two FastAPI replicas with health probes and Redis-backed distributed rate limiting.
- `redis`: shared rate-limit store for multiple backend pods.
- `frontend`: nginx-served React build with `/api` proxied to the backend service.
- `hpa`: backend autoscaling target.
- `migration-job`: a bounded non-root Alembic migration that must complete before application rollout.
- `configmap` + `secret`: non-sensitive runtime config is split from PostgreSQL, IAM, and integration secrets.
- security contexts: app pods run as non-root users.
- versioned backend and frontend images published to GitHub Container Registry by tagged releases, with SBOM and signed provenance attestations.

These are deployment-shape manifests, not a secret-distribution system. Before applying them, replace the Secret placeholders through the target platform's external secret manager and configure the corporate OIDC issuer, audience, JWKS, group mapping, and PostgreSQL URL.

Controlled cluster flow:

```powershell
docker build -t regulated-ai-agent-platform-backend:latest .\backend
docker build -t regulated-ai-agent-platform-frontend:latest .\frontend
kubectl apply -f .\k8s\namespace.yaml
kubectl apply -f .\k8s\configmap.yaml -f .\k8s\secret.yaml
kubectl apply -f .\k8s\redis.yaml
kubectl apply -f .\k8s\migration-job.yaml
kubectl -n regulated-ai wait --for=condition=complete job/backend-schema-migration --timeout=180s
kubectl apply -f .\k8s\backend.yaml -f .\k8s\frontend.yaml -f .\k8s\hpa.yaml
kubectl -n regulated-ai get pods,svc,hpa
```

Use a unique migration Job name or delete the completed Job before applying a later migration revision. Production releases should use immutable image digests, a managed PostgreSQL service, managed Redis, network policy, TLS ingress, image-signature admission, centralized telemetry, and tested backup/restore.

The checked-in manifests reference the `0.1.0` release images for repeatable evaluation. Before a company rollout, resolve those tags to immutable digests and enforce GitHub artifact-attestation verification in the admission policy.

For minikube:

```powershell
minikube service frontend -n regulated-ai
```
