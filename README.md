# 🚀 3-Tier Multi-Cluster (Dev, Stage, Prod) Kubernetes Project

An enterprise-grade, production-ready **3-Tier Web Application** designed for **3 isolated Kubernetes clusters (`dev`, `stage`, `prod`)** bootstrapped using **`kubeadm`**, with support for **NGINX Ingress Controller**, **MetalLB LoadBalancing**, **AWS ALB (Application Load Balancer) Controller**, and **Jenkins Multi-Branch Declarative CI/CD Pipelines**.

---

## 📐 1. Architecture

```
                                [ Developer Git Push ]
                                          │
                                 [ Jenkins Multi-Branch ]
                    ┌─────────────────────┼─────────────────────┐
             (branch: dev)         (branch: stage)       (branch: main)
                    ▼                     ▼                     ▼
          ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
          │    DEV CLUSTER    │ │   STAGE CLUSTER   │ │   PROD CLUSTER    │
          │                   │ │                   │ │                   │
          │ Ingress / ALB:    │ │ Ingress / ALB:    │ │ Ingress / ALB:    │
          │ dev.3tier.local   │ │ stage.3tier.local │ │ prod.3tier.local  │
          │                   │ │                   │ │                   │
          │ ┌───────────────┐ │ │ ┌───────────────┐ │ │ ┌───────────────┐ │
          │ │ Tier 1: Front │ │ │ │ Tier 1: Front │ │ │ │ Tier 1: Front │ │
          │ └───────┬───────┘ │ │ └───────┬───────┘ │ │ └───────┬───────┘ │
          │ ┌───────▼───────┐ │ │ ┌───────▼───────┐ │ │ ┌───────▼───────┐ │
          │ │ Tier 2: API   │ │ │ │ Tier 2: API   │ │ │ │ Tier 2: API   │ │
          │ └───────┬───────┘ │ │ └───────┬───────┘ │ │ └───────┬───────┘ │
          │ ┌───────▼───────┐ │ │ ┌───────▼───────┐ │ │ ┌───────▼───────┐ │
          │ │ Tier 3: PG DB │ │ │ │ Tier 3: PG DB │ │ │ │ Tier 3: PG DB │ │
          │ └───────────────┘ │ │ └───────────────┘ │ │ └───────────────┘ │
          └───────────────────┘ └───────────────────┘ └───────────────────┘
```

---

## 🖥️ 2. Frontend Tabs & Ingress Features

The Streamlit dashboard (`frontend/app.py`) provides 4 dedicated tabs designed specifically for Ingress and ALB operations:

1. **📋 Tab 1: Workload & Task Manager (Core App)**
   - CRUD task manager with real-time cluster context, environment badges, priority filters, and one-click status toggle.
2. **🌐 Tab 2: Ingress & AWS ALB Routing Inspector**
   - Interactive route simulator & tester for:
     - `/` ➡️ `frontend-service:80` (Streamlit UI)
     - `/api/*` ➡️ `backend-service:5000` (Express REST API)
     - `/ready` & `/healthz` ➡️ `backend-service:5000` (Probes)
     - `/metrics` ➡️ `backend-service:5000` (Prometheus Metrics)
   - Live Ingress Header Analysis (`Host`, `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Amzn-Trace-Id`).
3. **📊 Tab 3: Cluster Telemetry & Probes**
   - Real-time probe telemetry and Prometheus metric scrapers.
4. **🛠️ Tab 4: Ingress & ALB YAML Manifest Generator**
   - Dynamic generator for **NGINX Ingress** & **AWS ALB Ingress** with customizable domains, SSL ARNs, and target types (`ip` vs `instance`).

---

## 📁 3. Project Directory Structure

```
.
├── backend/                        # Tier 2: Node.js Express REST API + Prometheus Metrics
│   ├── src/
│   │   ├── db.js                   # PostgreSQL Connection Pool & Auto Migration
│   │   ├── server.js               # Express Server + Ingress Info (/api/ingress-info) + Probes
│   │   └── routes/tasks.js         # Full CRUD REST API
│   ├── Dockerfile                  # Multi-stage security-hardened Dockerfile
│   └── package.json
├── frontend/                       # Tier 1: 4-Tab Streamlit Dashboard
│   ├── app.py                      # Multi-Tab UI (Workloads, Ingress, Telemetry, Generator)
│   ├── requirements.txt            # Streamlit, requests, pandas
│   └── Dockerfile                  # Lightweight Python 3.10-slim container
├── database/                       # Tier 3: PostgreSQL Schema
│   └── init.sql                    # Initial database tables and seed records
├── docker-compose.yml              # Single-command local test
├── Jenkinsfile                     # Declarative Multi-Branch Pipeline (Dev/Stage/Prod)
├── k8s/                            # Kubernetes Manifests (Kustomize)
│   ├── base/                       # Shared base manifests
│   │   ├── backend/                # Deployment, Service, ConfigMap
│   │   ├── frontend/               # Deployment, Service, ConfigMap
│   │   ├── database/               # StatefulSet, Service, Secret
│   │   ├── ingress-nginx.yaml      # NGINX Ingress Controller Manifest
│   │   ├── ingress-alb.yaml        # AWS ALB Ingress Controller Manifest
│   │   └── kustomization.yaml
│   └── overlays/                   # Environment-specific overlays
│       ├── dev/                    # 1 Replica, Debug log, dev.3tier.local
│       ├── stage/                  # 2 Replicas, Info log, stage.3tier.local
│       ├── prod/                   # 3 Replicas, HPA autoscaling, NetworkPolicies
│       └── aws-alb/                # AWS Application Load Balancer overlay
└── scripts/
    ├── setup-k8s-prereqs.sh        # Kubeadm node preparation script
    └── setup-ingress-metallb.sh    # MetalLB + NGINX Ingress installation
```

---

## ⚡ 4. Quickstart: Test Locally with Docker Compose

To test the entire 3-Tier stack on your local machine:

```bash
# Start all 3 tiers (Database, Backend API, Frontend Web)
docker compose up --build -d

# Open browser:
# Frontend UI: http://localhost:8501
# Backend Health: http://localhost:5000/ready
# Ingress Header Info: http://localhost:5000/api/ingress-info
# Prometheus Metrics: http://localhost:5000/metrics

# Stop containers
docker compose down -v
```

---

## ☸️ 5. Multi-Cluster Setup using Kubeadm

Repeat this process for each of your 3 clusters (**Dev**, **Stage**, **Prod**):

### Step 1: Prepare Nodes (Run on Master & Worker nodes)
```bash
sudo chmod +x scripts/setup-k8s-prereqs.sh
sudo ./scripts/setup-k8s-prereqs.sh
```

### Step 2: Initialize Master Node
```bash
sudo kubeadm init --pod-network-cidr=192.168.0.0/16

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install Calico CNI
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/tigera-operator.yaml
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/custom-resources.yaml
```

### Step 3: Join Worker Nodes
```bash
sudo kubeadm join <MASTER_IP>:6443 --token <TOKEN> --discovery-token-ca-cert-hash sha256:<HASH>
```

### Step 4: Install MetalLB & NGINX Ingress Controller
```bash
chmod +x scripts/setup-ingress-metallb.sh
./scripts/setup-ingress-metallb.sh 192.168.1.200 192.168.1.210
```

---

## 🌐 6. Ingress Routing & AWS ALB Controller

### Option A: NGINX Ingress Controller (Kubeadm / MetalLB)
Deploy via Kustomize:
```bash
kubectl apply -k k8s/overlays/dev
# or
kubectl apply -k k8s/overlays/stage
# or
kubectl apply -k k8s/overlays/prod
```

### Option B: AWS ALB Ingress Controller (EKS / AWS)
Deploy with AWS Load Balancer Controller:
```bash
kubectl apply -k k8s/overlays/aws-alb
```

---

## 🌐 7. DNS / Local Hosts Setup

Add the Ingress External IPs to `/etc/hosts` (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):

```
<DEV_INGRESS_IP>    dev.3tier.local
<STAGE_INGRESS_IP>  stage.3tier.local
<PROD_INGRESS_IP>   prod.3tier.local
```

Access in browser:
- **Dev**: `http://dev.3tier.local`
- **Stage**: `http://stage.3tier.local`
- **Prod**: `http://prod.3tier.local`
