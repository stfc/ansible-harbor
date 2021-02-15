Ansible Harbor Server
=====================

Configuring Local Environment
=============================

- Activate .venv if present then install pip deps: `pip3 install ansible openstacksdk`
- Obtain a copy of clouds.yaml for your project, place it in `~/.configs/openstack/clouds.yaml` and rename `openstack` to `jupyter-development`
- Test using `openstack --os-cloud=jupyter-development coe cluster template list`, which will always return built-in templates

Configuring Remote Env
=======================

- In `roles/harbor_server/defaults` copy `secrets.yml.template` to `secrets.yml` and fill in as appropriate
- In playbooks/host_vars check the .yml file name matches the planned instance name (`harbor_docker_hub_cache` by default)
- If you have changed the instance name, in `playbooks/deploy_docker_mirror` change the hostname
- Check the values inside the .yml file and create an instance manually with the same name 

- Create a volume and mount using `/etc/fstab` to `/data`

- Issue a certificate to the harbor hostname and the docker mirror
- Copy .pem files to `roles/docker_cache/files` as per the instructions inside
- Ensure that `defaults/main.yml` for the docker mirror role match the harbor role

- Run ansible playbook as follows: `ansible-playbook playbooks/deploy_docker_mirror.yml -i dev_inventory/openstack.yml`
