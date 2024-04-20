# HipFire
Deploy pesky, perilous persistence in parallel with the help of Ansible.

# Usage

Set up Python virtual environment:

```bash
python3 -m venv hipfire
source hipfire/bin/activate
python3 -m pip install -r requirements.txt
```

Let's say the competition environment contains:

- Two teams (team 1 and team 2) with public IP range of 192.168.#.0/16 where # is the team number
- 2 Windows boxes on .3 and .4
- 2 Linux boxes on .5 and .6

Generate your beacon EXEs/ELFs/whatever else and copy them to the corresponding `files` directory under `roles`:
- Windows files: `roles/windows/files/`
- Linxu files: `roles/linux/files/`

Edit your `vars.yml` file with your beacon filenames, user credentials for persistence, etc.

Then you would run:

```bash
python3 hipfire.py -r 192.168.1-2 -w 3,4 -l 5,6 -a fire
```

This would generate a `hosts` file with the corresponding IP ranges/hosts and then run `playbook.yml` through Ansible.

To only generate a `hosts` file:

```bash
python3 hipfire.py -r 192.168.1-2 -w 3,4 -l 5,6 -a create
```

You may need to install Ansible, as well as community Ansible collections:
```bash
ansible-galaxy collection install ansible.windows
ansible-galaxy collection community.general
ansible-galaxy collection community.windows
```

Full help menu:

```
usage: hipfire.py [-h] (-r RANGE | -f FILE) [-w WIN_HOSTS] [-l LIN_HOSTS] -a ACTION [--playbook PLAYBOOK] [--edit-vars EDIT_VARS] [--create-file CREATE_FILE]

options:
  -h, --help            show this help message and exit
  -r RANGE, --range RANGE
                        specify range of hosts
  -f FILE, --file FILE  specify path to hosts file
  -a ACTION, --action ACTION
                        action to take
  --playbook PLAYBOOK   path to playbook.yml file (default=playbook.yml)
  --edit-vars EDIT_VARS
                        vars to edit, e.g. lin.lin_user:root
  --create-file CREATE_FILE
                        filename to write inventory to if --create is used (default=hosts)

  -w WIN_HOSTS, --win-hosts WIN_HOSTS
                        comma-separated 4th octets of Windows hosts
  -l LIN_HOSTS, --lin-hosts LIN_HOSTS
                        comma-separated 4th octets of Linux hosts
```
