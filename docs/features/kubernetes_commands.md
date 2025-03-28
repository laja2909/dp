## Some commands in kubernetes

The standard tool for deploying and managing workloads on Kubernetes is kubectl. For convenience, Canonical Kubernetes bundles a version of kubectl for you to use with no extra setup or configuration.

### In terminal
- to view your node: ```sudo k8s kubectl get nodes```
- to see running service: ```sudo k8s kubectl get services```
- to list all the pods in the kube-system namespace: ```sudo k8s kubectl get pods -n kube-system```
- uninstall canonical kubernetes snap: ```sudo snap remove k8s```
- uninstall canonical kubernetes snap and not saving its data, run:
```sudo snap remove k8s --purge```
- enable ingress


