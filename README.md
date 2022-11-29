Ansible Harbor Server
=====================
This playbook deploys Harbor on Kubernetes through helm to make it highly available. This way, Harbor users are not affected by outages on any of the nodes where it runs.

Deploys two components using Ansible to either openstack (using `dev_inventory`) or direct (using `prod_inventory`):

- A docker hub caching layer 
- A harbor instance

These are served via two configurable domain names, such as `docker.example.com` and `harbor.example.com`, so that users can either use a transparent cache or private registry. Further justification can be found later in **Reference**.

Requirements
============

- Kubernetes cluster 1.10+ (can use Cluster API)
- Helm 2.8.0+
- High available ingress controller
- High available PostgreSQL database
- High available Redis (Redis Sentinel) 
- PVC that can be shared across nodes or external object storage

Preparing to Deploy
===================

- Create a virtual environment 
`sudo apt install python3-venv`
`python3 -m venv venv`
`source venv/bin/activate`
- In `roles/harbor_server/defaults/main` copy `secrets.yml.template` to `secrets.yml` and fill in as appropriate
- In `playbooks/deploy_docker_mirror`, check the planned instance name and variables associated
- Ensure that `defaults/main.yml` for the docker mirror role match the harbor role
- If you want a volume for Harbor mount `/harbor_data` using `/etc/fstab` before deploying
- Decide if SSL termination will be done upstream and set the var in the playbook as appropriate.
- If you are using a docker hub token, create a file at `/opt/nginx/docker-mirror.env` with `REGISTRY_PROXY_USERNAME` set to the username and `REGISTRY_PROXY_PASSWORD` set to the access token.
- If you are using postrgres in Kubernetes: 
`export DB_PASSWORD=$(kubectl get secret --namespace default postgres-db-2-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d) ` 
`export DB_PASSWORD=<your DB password>`
`export REDIS_PASSWORD=<your REDIS password>`

With Host SSL
-------------

If you are planning on handling SSL termination on the server you must do the following too:
- Issue a certificate to the harbor hostname and the docker mirror
- Copy .pem files to `roles/docker_cache/files` as per the instructions inside. By default these are in .gitignore
- Create TLS secret (chage order of the chain if certifications are from Digital Infrastructure)
`kubectl create secret tls secret-tls --cert test.harbor.stfc.ac.uk.crt --key test.harbor.stfc.ac.uk.key -n harbor`

Deploy / Reconfigure
====================

- If you are using an openstack instance (likely for development testing) use `dev_inventory/openstack.yml`
- If you are using a production instance check the hostname in `prod_inventory/inventory.yml`
- Run ansible playbook as follows: `ansible-playbook playbooks/deploy_docker_mirror.yml -i < inventory path >`


E.g.
`ansible-playbook playbooks/deploy_docker_mirror.yml -i dev_inventory/openstack.yml`

Reference Notes
===============

This script affects the following directories: 
- `/opt/harbor_online-installer-{version}` 
- `/opt/harbor`
- `/opt/nginx`

/opt/harbor_online-installer-{version}
--------------------------------------

This directory is the installed directory from which Harbor runs. The components downloaded by the install step can be configured in `roles/harbor_server/templates/harbor.yaml.tmpl.j2` which is copied over.

As part of an upgrade it's recommended to leave the n-1 directory behind. This allows rapid rollback by updating the link (as described below) back to the older version.

/opt/harbor
-----------

This is a soft link to the currently running version of harbor, as described above. Ansible will configure the link to point to the correct version of harbor, but then does all subsequent steps through this ref-link.

/opt/nginx
----------

This directory contains an nginx reverse proxy, docker registry and config for docker.

The Nginx proxy is the entry-point for services provided on the node. This either serves on port 80 (redirect) + 443 if SSL termination is enabled. Or just port 80 if SSL termination is upstream.

It will redirect through the docker-compose network to the registry, or to the docker host on port 8080 for harbor.

A separate docker registry is run in this compose, in addition to harbor. This is because of docker hub allowing "bare named pulls" (my description), such as `docker pull nginx`.

Other repositories including Harbor require a library name, for example `docker pull nginx/nginx` and will not fix-up on the user behalf. The current "supported way" of doing this in harbor is with an Nginx URL rewrite using Regex to fix-up the URL in transit. This is at best, hacky and could break.

By deploying a separate Docker Registry component we can ensure that any weird quirks, like bare named pulls, are matched to upstream so that it "just works" for users. This is at the cost of additional disk space in the unlikely case that users mirror docker hub images into our harbor instance.

