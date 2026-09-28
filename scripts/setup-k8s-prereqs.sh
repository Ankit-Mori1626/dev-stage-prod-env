#!/usr/bin/env bash
# ==============================================================================
# Script: setup-k8s-prereqs.sh
# Purpose: Prepares Ubuntu 22.04 / 24.04 nodes with containerd, kubelet, kubeadm, kubectl
# Usage: sudo ./setup-k8s-prereqs.sh
# ==============================================================================

set -euo pipefail

K8S_VERSION="v1.29"

echo "========================================================"
echo " ⚙️  Installing Kubernetes Prerequisites (${K8S_VERSION})"
echo "========================================================"

# 1. Disable swap
swapoff -a
sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# 2. Kernel modules & sysctl configuration
cat <<EOF | tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

modprobe overlay
modprobe br_netfilter

cat <<EOF | tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sysctl --system

# 3. Install containerd runtime
apt-get update
apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y containerd.io

# Configure containerd to use SystemdCgroup
mkdir -p /etc/containerd
containerd config default | tee /etc/containerd/config.toml >/dev/null
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml
systemctl restart containerd
systemctl enable containerd

# 4. Install Kubeadm, Kubelet, Kubectl
curl -fsSL "https://pkgs.k8s.io/core:/stable:/${K8S_VERSION}/deb/Release.key" | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/${K8S_VERSION}/deb/ /" | tee /etc/apt/sources.list.d/kubernetes.list

apt-get update
apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl

systemctl enable --now kubelet

echo "========================================================"
echo " ✅ Node preparation complete!"
echo " 👉 For Master: sudo kubeadm init --pod-network-cidr=192.168.0.0/16"
echo " 👉 For Worker: Run the 'kubeadm join' token from master"
echo "========================================================"
