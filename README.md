# User Management: React + FastAPI + MySQL + Kubernetes

## Architecture
Browser -> frontend-service -> 3 React pods (Nginx)
Nginx /api -> backend-service -> 3 FastAPI pods -> mysql:3306 -> MySQL StatefulSet + PVC

The frontend Nginx configuration proxies `/api/` to `backend-service` using Kubernetes DNS.
The backend connects to the MySQL Service using hostname `mysql`.

## 1. Build and push images

Replace `YOUR_DOCKERHUB_USERNAME` in `k8s/backend.yaml` and `k8s/frontend.yaml`.

From the project root:

```bash
docker login
docker build -t YOUR_DOCKERHUB_USERNAME/user-management-backend:1.0 ./backend
docker build -t YOUR_DOCKERHUB_USERNAME/user-management-frontend:1.0 ./frontend
docker push YOUR_DOCKERHUB_USERNAME/user-management-backend:1.0
docker push YOUR_DOCKERHUB_USERNAME/user-management-frontend:1.0
```

## 2. Deploy to Kubernetes

Make sure your cluster has a default StorageClass that can provision a 5Gi PVC.

```bash
kubectl apply -f k8s/mysql.yaml
kubectl rollout status statefulset/mysql
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
```

Check resources:

```bash
kubectl get pods -o wide
kubectl get deployments
kubectl get services
kubectl get pvc
kubectl get endpoints backend-service
```

Get the external address:

```bash
kubectl get service frontend-service
```

Open the EXTERNAL-IP in your browser. On local clusters, use the relevant service exposure method (for example `minikube service frontend-service`).

## 3. Test the API

```bash
kubectl port-forward service/backend-service 8000:8000
```

Then open `http://localhost:8000/docs` or run:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/users   -H "Content-Type: application/json"   -d '{"name":"Alex","email":"alex@example.com"}'
curl http://localhost:8000/api/users
```

## 4. Scale replicas

```bash
kubectl scale deployment/backend --replicas=3
kubectl scale deployment/frontend --replicas=3
kubectl get pods -l app=backend
kubectl get pods -l app=frontend
```

## 5. Useful troubleshooting

```bash
kubectl describe pod POD_NAME
kubectl logs deployment/backend
kubectl logs statefulset/mysql
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl describe pvc mysql-pvc
```

## Important production notes

- This is a learning/demo deployment, not a production-hardened platform.
- Change the sample passwords. For production, use a managed secret solution or sealed/external secrets; avoid committing credentials to Git.
- The backend example uses a simple DB URL for clarity. Move it to a Kubernetes Secret in a real deployment.
- A single MySQL replica is a single point of failure. Three FastAPI replicas do not make the database highly available.
- Use database migrations (for example Alembic), connection pooling limits, backups, TLS, authentication, and monitoring before production.
- The MySQL PVC requires a working StorageClass. A ReadWriteOnce volume is expected for this single MySQL pod.
- Configure resource sizing and autoscaling based on measured load.
