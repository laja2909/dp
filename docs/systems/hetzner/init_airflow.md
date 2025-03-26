## Instructions to install airflow to remote server
- canonical Kubernetes and helm chart is used to install airflow

### Canonical Kubernetes

https://documentation.ubuntu.com/canonical-kubernetes/latest/

Canonical Kubernetes is a performant, lightweight, secure and opinionated distribution of Kubernetes which includes everything needed to create and manage a scalable cluster suitable for all use cases.

Canonical Kubernetes builds upon upstream Kubernetes by providing all the extra services such as a container runtime, a CNI, DNS services, an ingress gateway and more that are necessary to have a fully functioning cluster all in one convenient location - a snap!

#### Installation
Prerequisites:
- An Ubuntu environment to run the commands (or another operating system which supports snapd - see the snapd documentation)

- System Requirements: Your machine should have at least 40G disk space and 4G of memory

- A system without any previous installations of containerd/docker. Installing either with Canonical Kubernetes will cause conflicts. If a containerization solution is required on your system, consider using LXD to isolate your installation.

- Steps:
    - Open terminal
    - run: ```sudo snap install k8s --classic --channel=1.32-classic/stable```
    - bootstrap Kubernetes cluster by running: ```sudo k8s bootstrap```
    - To confirm installation, run: ```sudo k8s status```
    -add kubeconfig env variable:
    ```export KUBECONFIG=/etc/kubernetes/admin.conf```
    - More info of the Kubernetes commands check [here](docs/systems/hetzner/kubernetes_commands.md)

### Helm
Helm is the package manager for Kubernetes
#### Installation
- run: ```curl -O https://get.helm.sh/helm-v3.16.2-linux-amd64.tar.gz```
- run: ```tar xvf helm-v3.16.2-linux-amd64.tar.gz```
- run: ```sudo mv linux-amd64/helm /usr/local/bin```
- run: ```rm helm-v3.16.2-linux-amd64.tar.gz```
- run: ```rm -rf linux-amd64```
- verify installation: ```helm version```

### Airflow
Now that you've kubernetes and helm installed, we can use them to install airflow

#### Installation
- Add helm chart repository for Airflow
```helm repo add apache-airflow https://airflow.apache.org```
- update helm repository
```helm repo update```
- download values.yaml from:https://artifacthub.io/packages/helm/apache-airflow/airflow (default values)
- modify values.yaml that suits your needs, for instance:
executor: "KubernetesExecutor"
- Create namespace:
```kubectl create namespace airflow && kubectl config set-context --current --namespace=airflow```
- To install airflow in namespace airflow:
```helm upgrade --install airflow apache-airflow/airflow --namespace airflow -f values.yaml```
-add port:
```sudo k8s kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow```
-check that helm deployed airlow:
```helm ls --kubeconfig /etc/kubernetes/admin.conf``` (kubeconfig in canonical kubernetes by default hase config file there.)
-to access some pod (for example, default airflow.cfg exists in pod/airflow-scheduler...)
```sudo k8s kubectl exec -it <scheduler-pod-name> -- cat /opt/airflow/airflow.cfg```