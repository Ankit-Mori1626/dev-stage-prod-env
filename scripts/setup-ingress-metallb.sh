#!/usr/bin/env bash
# ==============================================================================
# Script: setup-ingress-metallb.sh
# Purpose: Installs MetalLB (Bare-metal LoadBalancer) & NGINX Ingress Controller
# Usage: ./setup-ingress-metallb.sh <IP_START> <IP_END>
# Example: ./setup-ingress-metallb.sh 192.168.1.240 192.168.1.250
# ==============================================================================

set -euo pipefail

IP_START="${1:-192.168.1.240}"
IP_END="${2:-192.168.1.250}"

echo "========================================================"
echo " ☸️  Setting up MetalLB & NGINX Ingress on Kubeadm"
echo " 🌐 LoadBalancer Pool Range: ${IP_START} - ${IP_END}"
echo "========================================================"

# 1. Enable strict ARP mode in kube-proxy (Required for MetalLB)
echo "==> Configuring kube-proxy strictARP..."
kubectl get configmap kube-proxy -n kube-system -o yaml | \
sed -e "s/strictARP: false/strictARP: true/" | \
kubectl apply -f - -n kube-system

# 2. Install MetalLB
echo "==> Deploying MetalLB native manifests..."
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb-native.yaml

echo "==> Waiting for MetalLB controller & speaker pods to be ready..."
kubectl rollout status deployment/controller -n metallb-system --timeout=180s
kubectl rollout status daemonset/speaker -n metallb-system --timeout=180s

# 3. Configure IPAddressPool and L2Advertisement
echo "==> Applying IPAddressPool and L2Advertisement..."
cat <<EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: default-pool
  namespace: metallb-system
spec:
  addresses:
    - ${IP_START}-${IP_END}
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: default-l2
  namespace: metallb-system
spec:
  ipAddressPools:
    - default-pool
EOF

# 4. Install NGINX Ingress Controller
echo "==> Deploying NGINX Ingress Controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml

echo "==> Waiting for NGINX Ingress Controller pod..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=180s

echo "========================================================"
echo " ✅ MetalLB & NGINX Ingress Setup Completed!"
echo " 📌 Ingress LoadBalancer External IP:"
kubectl get svc -n ingress-nginx ingress-nginx-controller
echo "========================================================"
