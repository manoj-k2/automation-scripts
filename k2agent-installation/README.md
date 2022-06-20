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
- Edit config.json file :
    ```sh
    $ vi config.json
    Mandatory fields:
    - pem file ( location of your aws instance ssh file eg.- k2-qa.pem )
    - k2GroupName (eg. IAST)
    - rc         (eg. 2.0.1-rc5 should be latest) 
    - validator  (eg. 650)
    - microagent (eg. 230)
    incase of vm 
    - vm : (eg. 192.168.5.68 )
    incase of aws instance
    - public ip, user (eg. 18.191.247.91, ubuntu)
    - root : true or false
    - docker : true or false 
    ```

- Run script on your machine (eg. Mac):
    ```sh
    python3 k2agent_install.py 
    ```
