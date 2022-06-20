# Tail 2.x IC and LC logs on your machine (Mac)
- This script can tail LC logs for following LCs:
  - Ruby
  - Java
  - Node
  - PHP
  - Python
  - Go

### Steps to get logs
- Clone the latest repository from GitHub on your with-LC machine:
  ```
  git clone https://github.com/manoj-k2/automation-scripts.git
  ```
  
- Go inside the directory :
    ```sh
    cd automation-scripts/agent-logs/
    ```

- Install Python3 on your machine and install these module paramiko:
    ```sh
    pip3 install -U pip setuptools 
    pip3 install paramiko
    ```
- Edit USER-INPUT Values according to your configurations in the script:
    ```sh
    Mandatory fields: 
    - public_ip
    - user
    - pem_file
    - k2home
    ```

- To get LC logs :
    ```sh
    get lc logs for VM:
    $ python3 lc_log.py 
    get lc logs for aws:
    $ python3 lc_log.py aws 
    ```

- To get IC logs :
  - To get prevent web logs: 
    ```sh
    get ic logs for VM:
    $ python3 ic_log.py 
    or use -
    $ python3 ic_log.py vm 
    get ic logs for aws:
    $ python3 ic_log.py aws 
    ```
  - To get vulnerability records:
    ```sh
    $ python3 ic_log.py aws record
    ```
  - To get vulnerability scanner:
    ```sh
    $ python3 ic_log.py aws scanner
    ```
  - To get vulnerability events:
    ```sh
    $ python3 ic_log.py aws events
    ```
   
    