# K2 Agent version 2.x Auto-Installation
- This script can run install k2 components on any VM/AWS instance from your machine (Mac)
- It can install in following environments:
  - Docker 
  - Non-Docker
- It can be installed in following user priveledges:
  - Root user
  - Non-Root user

### Steps to setup k2agent
- Clone the latest repository from GitHub on your with-LC machine:
  ```
  git clone https://github.com/manoj-k2/automation-scripts.git
  ```
  
- Go inside the directory :
    ```sh
    cd automation-scripts/k2agent-installation/
    ```

- Install Python3 on your machine and install this module :
    ```sh
    pip3 install -U pip setuptools 
    pip3 install paramiko
    ```

- Run script on your machine (eg. Mac):
    ```sh
    python3 k2agent_install.py 
    ```