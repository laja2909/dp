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
    - More info of the Kubernetes commands check [here](docs/systems/hetzner/kubernetes_commands.md)